import httpx
import os
import time
import random
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# API配置
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.seedream.ai")
API_TOKEN = os.getenv("SEEDREAM_API_KEY")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30.0"))
DEFAULT_DOWNLOAD_DIR = os.getenv("DEFAULT_DOWNLOAD_DIR", "./generated_images")

async def make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    发起 API 请求的通用函数

    Args:
        endpoint: API 端点路径
        method: HTTP 方法
        params: URL 参数
        data: 请求体数据

    Returns:
        API 响应数据

    Raises:
        MCPError: 当 API 请求失败时
    """
    # 检查API密钥是否配置
    if not API_TOKEN:
        from .errors import MCPError
        raise MCPError(
            message="API密钥未配置",
            suggestion="请设置环境变量SEEDREAM_API_KEY或在.env文件中配置"
        )
    
    # 准备请求头
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 构建完整URL
    url = f"{API_BASE_URL}/{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method, url,
                headers=headers,
                params=params,
                json=data,
                timeout=REQUEST_TIMEOUT  # 图像生成可能需要较长时间
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            from .errors import handle_api_error
            raise handle_api_error(e)

async def download_image(image_url: str, download_dir: str = DEFAULT_DOWNLOAD_DIR) -> str:
    """
    下载图片到本地文件系统
    
    Args:
        image_url: 图片URL
        download_dir: 下载目录路径
        
    Returns:
        本地文件路径
        
    Raises:
        MCPError: 下载失败时抛出
    """
    from .errors import handle_download_error
    
    try:
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        file_extension = "jpg"  # 假设所有图片都是JPG格式
        filename = f"seedream_image_{timestamp}_{random_suffix}.{file_extension}"
        
        # 构建完整文件路径
        file_path = os.path.join(download_dir, filename)
        
        # 下载图片
        async with httpx.AsyncClient() as client:
            response = await client.get(
                image_url,
                timeout=30.0,  # 下载超时设置
                follow_redirects=True
            )
            response.raise_for_status()  # 检查响应状态
            
            # 写入文件
            with open(file_path, "wb") as f:
                f.write(response.content)
        
        # 返回绝对路径
        return os.path.abspath(file_path)
        
    except PermissionError as e:
        raise handle_download_error("PERMISSION_ERROR", str(e))
    except IOError as e:
        # 检查是否是磁盘空间问题
        if "No space left on device" in str(e):
            raise handle_download_error("DISK_SPACE_ERROR", str(e))
        else:
            raise handle_download_error("DOWNLOAD_ERROR", str(e))
    except httpx.HTTPError as e:
        raise handle_download_error("DOWNLOAD_ERROR", f"网络错误: {str(e)}")
    except Exception as e:
        raise handle_download_error("DOWNLOAD_ERROR", str(e))
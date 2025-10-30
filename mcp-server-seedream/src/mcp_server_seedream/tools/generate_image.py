from pydantic import BaseModel, Field
from typing import Literal, Optional
import datetime
import os
from fastmcp import FastMCP
from mcp_server_seedream.utils.api_client import make_api_request, download_image
from mcp_server_seedream.utils.formatters import format_response
from mcp_server_seedream.utils.errors import MCPError

# 创建FastMCP实例
mcp = FastMCP("Seedream MCP Server")

# 从环境变量获取默认下载目录
DEFAULT_DOWNLOAD_DIR = os.getenv("DEFAULT_DOWNLOAD_DIR", "./generated_images")

class GenerateImageInput(BaseModel):
    """生成图像的输入模型"""
    model_config = {"extra": "forbid"}

    prompt: str = Field(
        description="详细的图像描述文本，支持中英文",
        min_length=1,
        max_length=600,
        examples=["一只可爱的小猫在沙发上睡觉", "A beautiful sunset over the mountains"]
    )

    size: str = Field(
        default="2048x2048",
        description="生成图像的尺寸，如'2048x2048'或'1K'/'2K'/'4K'",
        examples=["2048x2048", "1K", "2K"]
    )

    response_format: Literal["url", "b64_json", "local_file"] = Field(
        default="url",
        description="返回格式: 'url'、'b64_json'或'local_file'"
    )
    
    download_dir: Optional[str] = Field(
        default=DEFAULT_DOWNLOAD_DIR,
        description="当response_format为'local_file'时，图片保存的目录"
    )

    optimize_prompt: bool = Field(
        default=True,
        description="是否优化提示词"
    )

    format: Literal["json", "markdown"] = Field(
        default="json",
        description="输出格式: 'json' 或 'markdown'"
    )

    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="详细程度: 'concise' 或 'detailed'"
    )

@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def generate_image(input: GenerateImageInput) -> str:
    """
    根据文本描述生成高质量图像

    使用此工具根据文本提示生成高质量图像，所有生成的图像默认不带水印。
    支持多种输出格式和详细程度选择。

    Args:
        prompt: 详细的图像描述文本，支持中英文，最长600字符
        size: 生成图像的尺寸，默认为2048x2048
        response_format: 返回格式，可选'url'、'b64_json'或'local_file'，默认为'url'
        download_dir: 当response_format为'local_file'时，图片保存的目录
        optimize_prompt: 是否优化提示词，默认为True
        format: 输出格式，可选'json'或'markdown'，默认为'json'
        detail: 详细程度，可选'concise'或'detailed'，默认为'concise'

    Returns:
        格式化的生成结果，包含图像URL和使用信息

    Examples:
        generate_image(prompt="一只可爱的小猫在沙发上睡觉", format="json", detail="concise")
        generate_image(prompt="A beautiful sunset", size="1K", format="markdown", detail="detailed")
        generate_image(prompt="风景图", response_format="local_file", download_dir="./my_images")

    Error Handling:
        - 提示词过长: 请将提示词缩短至600字符以内
        - API密钥错误: 请检查ARK_API_KEY环境变量是否正确设置
        - 权限不足: 请确认API密钥具有图像生成权限
        - 请求过于频繁: 请稍后重试或增加请求间隔
        - 下载失败: 请检查下载目录权限和空间
    """
    try:
        # 准备API请求数据
        api_data = {
            "model": "doubao-seedream-4-0-250828",
            "prompt": input.prompt,
            "size": input.size,
            "response_format": "url" if input.response_format == "local_file" else input.response_format,  # API只支持url和b64_json
            "watermark": False,  # 强制不添加水印
            "optimize_prompt": input.optimize_prompt
        }

        # 调用API
        start_time = datetime.datetime.now()
        response = await make_api_request(
            endpoint="api/v3/images/generations",
            method="POST",
            data=api_data
        )
        processing_time_ms = int((datetime.datetime.now() - start_time).total_seconds() * 1000)

        # 构建响应数据
        image_url = response.get("data", [{}])[0].get("url")
        result_data = {
            "success": True,
            "image_url": image_url,
            "image_size": input.size,
            "token_usage": response.get("usage", {}).get("total_tokens", 0),
            "created_at": datetime.datetime.now().isoformat() + "Z",
            "model_used": "doubao-seedream-4-0-250828",
            "processing_time_ms": processing_time_ms,
            "watermark": False
        }
        
        # 如果需要本地文件，下载图片
        if input.response_format == "local_file" and image_url:
            # 下载图片到指定目录
            local_path = await download_image(image_url, input.download_dir)
            # 更新响应数据，添加本地文件信息
            result_data["local_path"] = local_path
            result_data["downloaded"] = True

        # 格式化输出
        return format_response(
            result_data,
            format=input.format,
            detail=input.detail
        )

    except MCPError:
        # MCPError 已经包含可操作的建议，直接抛出
        raise
    except Exception as e:
        # 其他异常转换为 MCPError
        raise MCPError(
            message=f"图像生成失败: {str(e)}",
            suggestion="请检查提示词和API配置，稍后重试"
        )
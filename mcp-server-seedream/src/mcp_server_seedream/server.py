from fastmcp import FastMCP
import os

# 创建 FastMCP 实例
mcp = FastMCP(
    name="Seedream MCP Server",
    instructions="即梦Seedream 4.0 MCP服务器，提供高质量图像生成服务。支持单图生成和批量生成，所有图像默认不带水印。"
)

# 重新定义并注册生成图像工具
from pydantic import BaseModel, Field
from typing import Literal, Optional
import datetime
import os
from mcp_server_seedream.utils.api_client import make_api_request, download_image
from mcp_server_seedream.utils.formatters import format_response
from mcp_server_seedream.utils.errors import MCPError

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
        default="local_file",
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
    """
    try:
        # 准备API请求数据
        api_data = {
            "model": "doubao-seedream-4-0-250828",
            "prompt": input.prompt,
            "size": input.size,
            "response_format": "url" if input.response_format == "local_file" else input.response_format,
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
        raise
    except Exception as e:
        raise MCPError(
            message=f"图像生成失败: {str(e)}",
            suggestion="请检查提示词和API配置，稍后重试"
        )

# 批量生成图像工具
from pydantic import field_validator
from typing import List

class GenerateImageGroupInput(BaseModel):
    """批量生成图像的输入模型"""
    model_config = {"extra": "forbid"}

    prompts: List[str] = Field(
        description="详细的图像描述文本列表，每个提示词支持中英文",
        min_length=1,
        max_length=10,
        examples=[
            ["一只可爱的小猫在沙发上睡觉", "一只小狗在草地上玩耍"],
            ["A beautiful sunset", "A mountain landscape"]
        ]
    )

    size: str = Field(
        default="2048x2048",
        description="生成图像的尺寸，如'2048x2048'或'1K'/'2K'/'4K'",
        examples=["2048x2048", "1K", "2K"]
    )

    response_format: Literal["url", "b64_json", "local_file"] = Field(
        default="local_file",
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

    @field_validator('prompts')
    @classmethod
    def validate_prompts(cls, v):
        """验证每个提示词的长度"""
        for prompt in v:
            if len(prompt) > 600:
                raise ValueError(f"提示词长度不能超过600字符，当前长度: {len(prompt)}")
            if len(prompt) < 1:
                raise ValueError("提示词不能为空")
        return v

@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def generate_image_group(input: GenerateImageGroupInput) -> str:
    """
    批量根据文本描述生成多张高质量图像

    使用此工具根据多个文本提示批量生成多张高质量图像，所有生成的图像默认不带水印。
    支持多种输出格式和详细程度选择。
    """
    try:
        # 准备结果列表和总token数
        images_data = []
        total_tokens = 0
        start_time = datetime.datetime.now()

        # 对每个提示词单独调用API
        for i, prompt in enumerate(input.prompts):
            try:
                # 准备API请求数据
                api_data = {
                    "model": "doubao-seedream-4-0-250828",
                    "prompt": prompt,
            "size": input.size,
            "response_format": "url" if input.response_format == "local_file" else input.response_format,
            "watermark": False,  # 强制不添加水印
            "optimize_prompt": input.optimize_prompt
                }

                # 调用API
                response = await make_api_request(
                    endpoint="api/v3/images/generations",
                    method="POST",
                    data=api_data
                )

                # 处理响应
                image_url = response.get("data", [{}])[0].get("url")
                tokens = response.get("usage", {}).get("total_tokens", 0)
                total_tokens += tokens

                # 创建图像数据字典
                image_info = {
                    "index": i,
                    "prompt": prompt,
                    "image_url": image_url,
                    "image_size": input.size,
                    "token_usage": tokens,
                    "watermark": False,
                    "success": True
                }
                
                # 如果需要本地文件，下载图片
                if input.response_format == "local_file" and image_url:
                    try:
                        # 下载图片到指定目录
                        local_path = await download_image(image_url, input.download_dir)
                        # 更新图像信息，添加本地文件信息
                        image_info["local_path"] = local_path
                        image_info["downloaded"] = True
                    except Exception as download_error:
                        # 下载失败不影响整体流程，只记录错误
                        image_info["downloaded"] = False
                        image_info["download_error"] = str(download_error)
                
                images_data.append(image_info)

            except Exception as img_error:
                # 单个图像生成失败，记录错误但继续处理其他图像
                images_data.append({
                    "index": i,
                    "prompt": prompt,
                    "error": str(img_error),
                    "success": False
                })

        processing_time_ms = int((datetime.datetime.now() - start_time).total_seconds() * 1000)
        
        # 计算下载统计信息
        downloaded_count = sum(1 for img in images_data if img.get("downloaded", False))
        total_images = len(input.prompts)

        # 构建完整响应数据
        result_data = {
            "success": len(images_data) > 0,
            "total_images": total_images,
            "successful_images": sum(1 for img in images_data if "error" not in img),
            "images": images_data,
            "total_token_usage": total_tokens,
            "created_at": datetime.datetime.now().isoformat() + "Z",
            "model_used": "doubao-seedream-4-0-250828",
            "processing_time_ms": processing_time_ms
        }
        
        # 添加下载汇总信息
        if input.response_format == "local_file":
            result_data["download_summary"] = f"成功下载 {downloaded_count}/{total_images} 张图片"
            result_data["download_dir"] = input.download_dir

        # 格式化输出
        return format_response(
            result_data,
            format=input.format,
            detail=input.detail
        )

    except MCPError:
        raise
    except Exception as e:
        raise MCPError(
            message=f"批量图像生成失败: {str(e)}",
            suggestion="请检查提示词列表和API配置，稍后重试"
        )

if __name__ == "__main__":
    # 使用 STDIO 传输协议运行服务器（默认）
    # 这适合本地运行和Claude Desktop等环境使用
    mcp.run()
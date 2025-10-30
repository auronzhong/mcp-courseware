from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Optional
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

    Args:
        prompts: 详细的图像描述文本列表，每个提示词支持中英文，最长600字符，最多10个
        size: 生成图像的尺寸，默认为2048x2048
        response_format: 返回格式，可选'url'、'b64_json'或'local_file'，默认为'local_file'
        download_dir: 当response_format为'local_file'时，图片保存的目录
        optimize_prompt: 是否优化提示词，默认为True
        format: 输出格式，可选'json'或'markdown'，默认为'json'
        detail: 详细程度，可选'concise'或'detailed'，默认为'concise'

    Returns:
        格式化的生成结果列表，包含所有生成图像的URL和使用信息

    Examples:
        generate_image_group(prompts=["小猫", "小狗"], format="json", detail="concise")
        generate_image_group(prompts=["A sunset", "A mountain"], size="1K", format="markdown", detail="detailed")
        generate_image_group(prompts=["风景图1", "风景图2"], response_format="local_file", download_dir="./batch_images")

    Error Handling:
        - 提示词过长: 请将每个提示词缩短至600字符以内
        - 提示词数量过多: 请限制提示词数量不超过10个
        - API密钥错误: 请检查ARK_API_KEY环境变量是否正确设置
        - 权限不足: 请确认API密钥具有图像生成权限
        - 请求过于频繁: 请稍后重试或增加请求间隔
        - 下载失败: 请检查下载目录权限和空间
        - 部分图像生成失败: 返回成功生成的图像，在错误信息中说明
    """
    try:
        # 准备结果列表和总token数
        images_data = []
        total_tokens = 0
        start_time = datetime.datetime.now()

        # 对每个提示词单独调用API（由于API可能不支持一次请求多个不同提示词）
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
        # MCPError 已经包含可操作的建议，直接抛出
        raise
    except Exception as e:
        # 其他异常转换为 MCPError
        raise MCPError(
            message=f"批量图像生成失败: {str(e)}",
            suggestion="请检查提示词列表和API配置，稍后重试"
        )
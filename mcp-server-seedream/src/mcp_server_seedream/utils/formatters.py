import json
import os
from typing import Any, Dict, Literal
import datetime

CHARACTER_LIMIT = 25000 * 4  # ~25k tokens
DEFAULT_DOWNLOAD_DIR = os.getenv("DEFAULT_DOWNLOAD_DIR", "./generated_images")

def format_response(
    data: Any,
    format: Literal["json", "markdown"] = "json",
    detail: Literal["concise", "detailed"] = "concise"
) -> str:
    """
    格式化响应数据

    Args:
        data: 要格式化的数据
        format: 输出格式（json 或 markdown）
        detail: 详细级别（concise 或 detailed）

    Returns:
        格式化后的字符串
    """
    if format == "json":
        if detail == "concise":
            # 返回精简的 JSON
            result = json.dumps(extract_concise_data(data), indent=2, ensure_ascii=False)
        else:
            # 返回完整的 JSON
            result = json.dumps(data, indent=2, ensure_ascii=False)
    else:  # markdown
        if detail == "concise":
            result = format_markdown_concise(data)
        else:
            result = format_markdown_detailed(data)

    # 检查字符限制
    if len(result) > CHARACTER_LIMIT:
        result = truncate_response(result, CHARACTER_LIMIT)

    return result

def downloadImage(image_url: str, download_dir: str = DEFAULT_DOWNLOAD_DIR) -> Dict[str, Any]:
    """
    下载图片并返回下载信息
    
    Args:
        image_url: 图片URL
        download_dir: 下载目录
        
    Returns:
        包含下载状态的字典
    """
    import asyncio
    from .api_client import download_image
    
    # 使用事件循环执行异步下载
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，使用run_coroutine_threadsafe
            future = asyncio.run_coroutine_threadsafe(
                download_image(image_url, download_dir), loop
            )
            local_path = future.result()
        else:
            # 否则直接运行协程
            local_path = loop.run_until_complete(
                download_image(image_url, download_dir)
            )
        
        return {
            "downloaded": True,
            "local_path": local_path,
            "image_url": image_url
        }
    except Exception as e:
        return {
            "downloaded": False,
            "error": str(e),
            "image_url": image_url
        }

def truncate_response(text: str, max_chars: int) -> str:
    """截断过长的响应"""
    truncated = text[:max_chars]
    return f"""{truncated}

... [Response truncated due to length]

To get complete info:
1. Use more specific filters
2. Request smaller batches
3. Use 'concise' detail level"""

def extract_concise_data(data: Any) -> Any:
    """提取精简数据"""
    if isinstance(data, dict):
        # 根据数据结构提取关键信息
        if "images" in data:  # 组图响应
            # 检查是否有本地路径信息
            result = {
                "success": True,
                "total_images": len(data.get("images", [])),
                "token_usage": data.get("token_usage", 0)
            }
            # 如果有下载信息，添加到结果
            downloaded_images = [img for img in data.get("images", []) if img.get("downloaded")]
            if downloaded_images:
                result["downloaded_images"] = len(downloaded_images)
                result["downloaded_paths"] = [img.get("local_path") for img in downloaded_images]
            else:
                result["image_urls"] = [img.get("image_url") for img in data.get("images", [])]
            return result
        elif "image_url" in data or "local_path" in data:  # 单图响应或本地图片
            result = {
                "success": True,
                "token_usage": data.get("token_usage", 0)
            }
            if data.get("downloaded") and "local_path" in data:
                result["downloaded"] = True
                result["local_path"] = data.get("local_path")
            else:
                result["image_url"] = data.get("image_url")
            return result
        else:
            # 其他响应格式，返回精简版本
            result = {k: v for k, v in data.items() if k in ["success", "message", "error", "token_usage"]}
            # 如果有下载信息，也包含进去
            if data.get("downloaded") is not None:
                result["downloaded"] = data.get("downloaded")
                if "local_path" in data:
                    result["local_path"] = data.get("local_path")
            return result
    elif isinstance(data, list):
        # 列表数据返回前几项
        return data[:3] if len(data) > 3 else data
    return data

def format_markdown_concise(data: Any) -> str:
    """格式化为精简 Markdown"""
    if isinstance(data, dict):
        if "images" in data:
            # 组图响应
            images = data.get("images", [])
            lines = ["# 图像生成结果", ""]
            lines.append(f"## 生成了 {len(images)} 张图像")
            for i, img in enumerate(images[:3]):  # 只显示前3张
                lines.append(f"### 图像 {i+1}")
                # 检查是否有本地路径信息
                if img.get("downloaded") and "local_path" in img:
                    lines.append("✅ 已成功下载到本地")
                    lines.append(f"- 本地路径: {img.get('local_path')}")
                    if img.get('image_url'):
                        lines.append(f"- 原始URL: {img.get('image_url')}")
                else:
                    lines.append(f"- URL: {img.get('image_url')}")
            if len(images) > 3:
                lines.append(f"\n... 还有 {len(images) - 3} 张图像")
            return "\n".join(lines)
        elif "image_url" in data or "local_path" in data:
            # 单图响应或本地图片
            lines = ["# 图像生成结果", ""]
            if data.get("downloaded") and "local_path" in data:
                lines.append("## 图像已下载到本地")
                lines.append(f"✅ 本地路径: {data.get('local_path')}")
                if data.get('image_url'):
                    lines.append(f"- 原始URL: {data.get('image_url')}")
            else:
                lines.append(f"## 图像 URL")
                lines.append(data.get("image_url"))
            return "\n".join(lines)
        else:
            # 通用响应
            lines = ["# 操作结果", ""]
            for k, v in extract_concise_data(data).items():
                lines.append(f"- **{k}**: {v}")
            return "\n".join(lines)
    return str(data)

def format_markdown_detailed(data: Any) -> str:
    """格式化为详细 Markdown"""
    if isinstance(data, dict):
        if "images" in data:
            # 组图详细响应
            images = data.get("images", [])
            lines = ["# 图像生成详细结果", ""]
            lines.append(f"## 总体信息")
            lines.append(f"- **生成图像总数**: {len(images)}")
            lines.append(f"- **Token 用量**: {data.get('token_usage', 0)}")
            if "created_at" in data:
                lines.append(f"- **创建时间**: {data.get('created_at')}")
            if "model_used" in data:
                lines.append(f"- **使用模型**: {data.get('model_used')}")
            
            # 添加下载汇总信息
            downloaded_images = [img for img in images if img.get("downloaded")]
            if downloaded_images:
                lines.append(f"- **已下载图像**: {len(downloaded_images)}")
            
            lines.append("\n## 图像详情")
            for i, img in enumerate(images):
                lines.append(f"### 图像 {i+1}")
                # 检查是否有本地路径信息
                if img.get("downloaded") and "local_path" in img:
                    lines.append("✅ **已成功下载到本地**")
                    lines.append(f"- **本地路径**: {img.get('local_path')}")
                    if img.get('image_url'):
                        lines.append(f"- **原始URL**: {img.get('image_url')}")
                else:
                    lines.append(f"- **URL**: {img.get('image_url')}")
                if "image_size" in img:
                    lines.append(f"- **尺寸**: {img.get('image_size')}")
                if "watermark" in img:
                    lines.append(f"- **水印**: {'是' if img.get('watermark') else '否'}")
            return "\n".join(lines)
        elif "image_url" in data or "local_path" in data:
            # 单图详细响应或本地图片
            lines = ["# 图像生成详细结果", ""]
            lines.append(f"## 图像信息")
            
            # 检查是否有本地路径信息
            if data.get("downloaded") and "local_path" in data:
                lines.append("✅ **已成功下载到本地**")
                lines.append(f"- **本地路径**: {data.get('local_path')}")
                if data.get('image_url'):
                    lines.append(f"- **原始URL**: {data.get('image_url')}")
            else:
                lines.append(f"- **URL**: {data.get('image_url')}")
            
            if "image_size" in data:
                lines.append(f"- **尺寸**: {data.get('image_size')}")
            if "watermark" in data:
                lines.append(f"- **水印**: {'是' if data.get('watermark') else '否'}")
            if "token_usage" in data:
                lines.append(f"- **Token 用量**: {data.get('token_usage')}")
            if "created_at" in data:
                lines.append(f"- **创建时间**: {data.get('created_at')}")
            if "model_used" in data:
                lines.append(f"- **使用模型**: {data.get('model_used')}")
            if "processing_time_ms" in data:
                lines.append(f"- **处理时间**: {data.get('processing_time_ms')} ms")
            return "\n".join(lines)
        else:
            # 通用详细响应
            lines = ["# 操作详细结果", ""]
            for k, v in data.items():
                lines.append(f"- **{k}**: {v}")
            return "\n".join(lines)
    return json.dumps(data, indent=2, ensure_ascii=False)
import httpx
from typing import Optional

class MCPError(Exception):
    """MCP服务器自定义错误类"""
    
    def __init__(self,
                 message: str,
                 suggestion: Optional[str] = None,
                 error_code: Optional[str] = None,
                 status_code: Optional[int] = None):
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self._format_error_message())
    
    def _format_error_message(self) -> str:
        """格式化错误消息"""
        parts = [f"Error: {self.message}"]
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        return "\n".join(parts)

def handle_api_error(e: httpx.HTTPError) -> MCPError:
    """
    处理API请求错误并转换为MCPError
    
    Args:
        e: httpx HTTP错误
        
    Returns:
        格式化的MCPError
    """
    if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code
        
        try:
            # 尝试获取API返回的错误信息
            error_data = e.response.json()
            error_message = error_data.get("message", str(e))
            error_code = error_data.get("error_code")
        except (ValueError, KeyError):
            error_message = str(e)
            error_code = None
        
        # 根据不同的状态码提供不同的建议
        if status_code == 401:
            suggestion = "请检查API密钥是否正确配置"
        elif status_code == 403:
            suggestion = "权限不足，请检查API密钥的权限设置"
        elif status_code == 404:
            suggestion = "请求的资源不存在，请检查端点路径"
        elif status_code == 429:
            suggestion = "请求过于频繁，请稍后重试或增加请求间隔"
        elif status_code >= 500:
            suggestion = "服务器端错误，请稍后重试"
        else:
            suggestion = "请检查请求参数是否正确"
        
        return MCPError(
            message=error_message,
            suggestion=suggestion,
            error_code=error_code,
            status_code=status_code
        )
    
    elif isinstance(e, httpx.RequestError):
        # 网络错误、超时等
        return MCPError(
            message=f"网络请求失败: {str(e)}",
            suggestion="请检查网络连接或API服务器状态"
        )
    
    else:
        # 其他HTTP错误
        return MCPError(
            message=str(e),
            suggestion="请稍后重试或联系管理员"
        )

def handle_download_error(error_type: str, message: str) -> MCPError:
    """
    处理图片下载错误并转换为MCPError
    
    Args:
        error_type: 错误类型
        message: 错误消息
        
    Returns:
        格式化的MCPError
    """
    error_mapping = {
        "DOWNLOAD_ERROR": {
            "message": f"图片下载失败: {message}",
            "suggestion": "请检查网络连接，确保下载目录存在且有写入权限"
        },
        "DISK_SPACE_ERROR": {
            "message": f"磁盘空间不足: {message}",
            "suggestion": "请清理磁盘空间或选择其他下载目录"
        },
        "PERMISSION_ERROR": {
            "message": f"权限不足: {message}",
            "suggestion": "请确保对下载目录有写入权限"
        }
    }
    
    error_info = error_mapping.get(error_type, {
        "message": message,
        "suggestion": "请检查下载目录设置"
    })
    
    return MCPError(
        message=error_info["message"],
        suggestion=error_info["suggestion"],
        error_code=error_type
    )
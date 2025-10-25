"""
示例 MCP Server - 来自快速入门教程第 3 章
这是一个完整可运行的 MCP Server 示例

使用方法：
1. 安装依赖：uv pip install fastmcp
2. 创建测试文件：mkdir notes && echo "Hello MCP!" > notes/hello.txt
3. 运行服务：python example-server.py
4. 配置客户端连接此服务

更多信息请查看教程：tutorials/quickstart/README.md
"""

from fastmcp import FastMCP

# 创建 MCP 服务实例
mcp = FastMCP("Example MCP Server")


# ============================================
# 工具定义（Tools）
# ============================================

@mcp.tool()
def echo(text: str) -> str:
    """
    回显工具：返回用户输入的文本

    这是一个简单的工具示例，演示如何定义一个可被 AI 调用的函数。

    参数：
        text: 要回显的文本

    返回：
        原样返回输入的文本（带前缀）

    来源：基于 MCP Tool 规范实现
    """
    return f"你说：{text}"


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    加法计算器：计算两个整数的和

    这个工具演示了如何定义带多个参数的函数，
    以及如何通过类型注解让 AI 正确理解参数类型。

    参数：
        a: 第一个加数
        b: 第二个加数

    返回：
        两数之和

    来源：基于 MCP Tool 规范实现
    """
    return a + b


# ============================================
# 资源定义（Resources）
# ============================================

@mcp.resource("file://notes/hello.txt")
def read_hello() -> str:
    """
    读取欢迎文件（静态资源示例）

    这是一个静态资源，返回 notes/hello.txt 的内容。
    静态资源适合用于固定路径的文件或数据。

    URI: file://notes/hello.txt
    用途：提供上下文信息给 AI

    来源：基于 MCP Resource 规范实现
    """
    try:
        with open("notes/hello.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "错误：文件不存在，请确保 notes/hello.txt 存在"
    except Exception as e:
        return f"错误：读取文件失败 - {str(e)}"


@mcp.resource("file://notes/{filename}")
def read_note(filename: str) -> str:
    """
    读取指定的笔记文件（动态资源示例）

    这是一个参数化资源，支持读取 notes/ 目录下的任意 .txt 文件。
    动态资源适合用于需要根据参数动态获取数据的场景。

    参数：
        filename: 文件名（例如：todo.txt, python.txt）

    URI 示例：
        - file://notes/todo.txt
        - file://notes/python.txt

    安全提示：
        生产环境中必须进行严格的路径验证，防止路径遍历攻击

    来源：基于 MCP Resource 规范的动态资源实现
    """
    # 安全检查：防止路径遍历攻击（如 ../../etc/passwd）
    if ".." in filename or "/" in filename or "\\" in filename:
        return "错误：非法文件名，不允许包含 '..' 或路径分隔符"

    filepath = f"notes/{filename}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"文件：{filename}\n\n{content}"
    except FileNotFoundError:
        return f"错误：文件 {filename} 不存在"
    except Exception as e:
        return f"错误：读取失败 - {str(e)}"


# ============================================
# 启动服务
# ============================================

if __name__ == "__main__":
    # 运行 MCP 服务器
    # fastmcp 会自动处理所有 MCP 协议细节：
    # - 初始化握手（initialize/initialized）
    # - 能力协商（capabilities negotiation）
    # - 工具列表和调用（tools/list, tools/call）
    # - 资源列表和读取（resources/list, resources/read）
    # - 错误处理和消息路由

    print("正在启动 MCP Server...")
    print("服务名称: Example MCP Server")
    print("可用工具: echo, add")
    print("可用资源: file://notes/hello.txt, file://notes/{filename}")
    print("\n等待客户端连接...")
    print("按 Ctrl+C 停止服务\n")

    mcp.run()

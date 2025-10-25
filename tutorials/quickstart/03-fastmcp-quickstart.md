# 最小 MCP Server：复制就能跑

在这一章，我们将用 **fastmcp** 框架创建一个真正能运行的 MCP Server。整个过程只需 **10 分钟**！

## 目标

完成本章后，你将拥有一个可运行的 MCP Server，它能：

- ✅ 提供 2 个工具：`echo`（回显文本）和 `add`（两数相加）
- ✅ 提供 1 个资源：读取本地文件 `notes/hello.txt`
- ✅ 被任何支持 MCP 的客户端调用

## 步骤一：环境准备

### 1.1 安装 uv（Python 环境管理工具）

**uv** 是新一代 Python 包管理工具，速度极快且易用。

**macOS / Linux：**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows：**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

验证安装：

```bash
uv --version
```

### 1.2 创建项目目录

```bash
# 创建项目文件夹
mkdir my-first-mcp-server
cd my-first-mcp-server

# 创建笔记文件夹（用于存放资源文件）
mkdir notes
```

### 1.3 初始化 Python 环境

```bash
# 使用 uv 创建虚拟环境（Python 3.10+）
uv venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 1.4 安装 fastmcp

```bash
uv pip install fastmcp
```

验证安装：

```bash
python -c "import fastmcp; print(fastmcp.__version__)"
```

## 步骤二：创建测试文件

在 `notes/` 文件夹下创建一个测试文件：

```bash
echo "你好，这是我的第一个 MCP 资源！" > notes/hello.txt
```

## 步骤三：编写 MCP Server

创建 `server.py` 文件，复制以下完整代码：

```python
"""
我的第一个 MCP Server
提供基础工具和资源示例
"""

from fastmcp import FastMCP

# 创建 MCP 服务实例
# 参数：服务名称（会显示给客户端）
mcp = FastMCP("My First MCP Server")

# ============================================
# 工具定义（Tools）
# ============================================

@mcp.tool()
def echo(text: str) -> str:
    """
    回显工具：返回用户输入的文本

    参数：
        text: 要回显的文本

    返回：
        原样返回输入的文本

    来源：基于 MCP Tool 规范实现
    """
    return f"你说：{text}"


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    加法计算器：计算两个整数的和

    参数：
        a: 第一个加数
        b: 第二个加数

    返回：
        两数之和

    来源：基于 MCP Tool 规范实现
    """
    result = a + b
    return result


# ============================================
# 资源定义（Resources）
# ============================================

@mcp.resource("file://notes/hello.txt")
def read_hello() -> str:
    """
    读取欢迎文件

    这是一个静态资源，返回 notes/hello.txt 的内容

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


# ============================================
# 启动服务
# ============================================

if __name__ == "__main__":
    # 运行 MCP 服务器
    # fastmcp 会自动处理：
    # - 初始化握手（initialize）
    # - 能力协商（capabilities negotiation）
    # - 工具列表（tools/list）
    # - 工具调用（tools/call）
    # - 资源列表（resources/list）
    # - 资源读取（resources/read）
    mcp.run()
```

## 步骤四：运行 Server

在终端执行：

```bash
python server.py
```

**预期输出：**

```
MCP Server running on stdio
Server name: My First MCP Server
```

如果看到类似输出，恭喜，你的第一个 MCP Server 已经运行成功了！

**注意：** Server 现在处于等待状态，准备接收来自客户端的连接。按 `Ctrl+C` 可以停止服务。

## 步骤五：理解代码

### 5.1 创建 MCP 实例

```python
mcp = FastMCP("My First MCP Server")
```

- 创建一个 MCP 服务实例
- 参数是服务的名称，会在客户端中显示
- 这个对象负责管理所有工具和资源

### 5.2 定义工具（Tool）

```python
@mcp.tool()
def echo(text: str) -> str:
    """回显工具：返回用户输入的文本"""
    return f"你说：{text}"
```

**关键点：**

- `@mcp.tool()` 装饰器：告诉 fastmcp 这是一个可调用的工具
- 函数名（`echo`）会成为工具名称
- 参数类型注解（`text: str`）很重要：
  - fastmcp 会据此生成参数规范（JSON Schema）
  - AI 会根据这些信息决定如何调用
- 文档字符串（docstring）：
  - AI 通过这个描述理解工具用途
  - 写得越清楚，AI 使用越准确

**对应 MCP 协议：**

- 客户端调用 `tools/list` 时，会看到这个工具
- 客户端调用 `tools/call` 时，fastmcp 会执行这个函数

### 5.3 定义资源（Resource）

```python
@mcp.resource("file://notes/hello.txt")
def read_hello() -> str:
    """读取欢迎文件"""
    with open("notes/hello.txt", "r", encoding="utf-8") as f:
        return f.read()
```

**关键点：**

- `@mcp.resource(uri)` 装饰器：定义资源的唯一标识符（URI）
- URI 格式：`scheme://path`
  - 常见格式：`file://`, `http://`, `database://`
  - 可以自定义，只要保持一致
- 函数返回资源内容（字符串格式）
- 支持动态读取（每次调用都会重新读取文件）

**对应 MCP 协议：**

- 客户端调用 `resources/list` 时，会看到这个资源的 URI
- 客户端调用 `resources/read` 时，fastmcp 会执行这个函数

### 5.4 启动服务

```python
if __name__ == "__main__":
    mcp.run()
```

- `mcp.run()` 启动 MCP 服务器
- 默认使用 **stdio** 传输（标准输入/输出）
  - 客户端通过进程的 stdin/stdout 与 Server 通信
  - 这是本地 MCP Server 的标准运行方式
- fastmcp 自动处理所有 MCP 协议细节：
  - 握手（initialize/initialized）
  - 能力协商（capabilities）
  - 消息路由（request → 对应函数）
  - 错误处理

## 常见问题排查

### 问题 1：找不到 fastmcp 模块

**错误信息：**

```
ModuleNotFoundError: No module named 'fastmcp'
```

**解决方案：**

```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 重新安装
uv pip install fastmcp
```

### 问题 2：找不到 notes/hello.txt

**错误信息：**

```
错误：文件不存在，请确保 notes/hello.txt 存在
```

**解决方案：**

```bash
# 确保在项目根目录
pwd

# 检查文件是否存在
ls notes/hello.txt

# 如果不存在，重新创建
mkdir -p notes
echo "你好，这是我的第一个 MCP 资源！" > notes/hello.txt
```

### 问题 3：端口被占用（如果使用 SSE 传输）

**注意：** 本教程使用 stdio 传输，不会遇到端口问题。如果你修改代码使用了 HTTP/SSE 传输，可能会遇到端口冲突。

**解决方案：**

```python
# 修改端口（如果需要）
mcp.run(transport="sse", port=8080)
```

## 测试检查清单

在连接客户端之前，确保：

- ☑️ uv 已安装并能执行
- ☑️ 虚拟环境已创建并激活
- ☑️ fastmcp 已安装（能 import）
- ☑️ notes/hello.txt 文件存在
- ☑️ server.py 文件创建完成
- ☑️ 运行 `python server.py` 无报错

## 小结

恭喜！你已经：

✅ 搭建了 Python 开发环境（uv + venv）
✅ 安装了 fastmcp 框架
✅ 创建了第一个 MCP Server
✅ 定义了 2 个工具（echo, add）
✅ 定义了 1 个资源（hello.txt）
✅ 成功启动了服务

**核心代码只有约 50 行**，但已经是一个完整的 MCP Server！

下一章，我们将：

1. 小幅扩展功能（支持读取任意文件）
2. 用现成的客户端连接并测试

👉 [下一章：扩展功能并连接客户端](./04-extend-and-use.md)

---

**参考资料**

- fastmcp 框架：https://gofastmcp.com
- uv 包管理工具：https://astral.sh/uv
- MCP Tool 规范：定义可调用函数的标准格式
- MCP Resource 规范：定义可读取资源的标准格式
- stdio 传输：MCP 支持的标准进程间通信方式
- JSON Schema：用于描述工具参数的规范（fastmcp 自动生成）

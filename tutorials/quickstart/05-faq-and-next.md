# FAQ 与进阶路线

恭喜你完成了 MCP Server 开发入门教程！本章将回答常见问题，并为你指明进阶学习的方向。

## 常见问题（FAQ）

### 1. Trae IDE 找不到我的 Server

**症状：** 配置后 Trae IDE 没有显示可用的工具，或者无法连接到 Server。

**排查步骤：**

```bash
# 1. 检查 server.py 路径是否使用绝对路径
# 配置中不能用 ~ 或相对路径

# 2. 手动测试 Server 是否能启动
cd /完整路径/my-first-mcp-server
python server.py

# 3. 确认 Python 环境正确
which python  # 应该指向虚拟环境或系统 Python

# 4. 检查 Trae IDE MCP 设置
# 在 Settings > MCP 中查看 Server 状态
```

**常见原因：**
- ❌ 使用了相对路径或 `~`
- ❌ Python 环境未激活或路径不正确
- ❌ 工作目录（cwd）设置错误
- ❌ JSON 配置格式有误（缺少逗号、引号等）
- ❌ Server 没有被添加到当前使用的 agent

**正确配置示例（Trae IDE 手动添加）：**
```json
{
  "command": "python",
  "args": ["/Users/yourname/my-first-mcp-server/server.py"],
  "env": {},
  "cwd": "/Users/yourname/my-first-mcp-server"
}
```

**提示：** 确保在 Trae IDE 中将 Server 添加到了你正在使用的 agent（如 "Builder with MCP"）。

### 2. 读取文件时报错"文件不存在"

**症状：** Server 启动正常，但读取资源时报 FileNotFoundError。

**原因：** 工作目录（cwd）设置不正确，Server 在错误的目录下寻找文件。

**解决方案：**

```python
# 方案 1：使用绝对路径（推荐用于生产环境）
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(BASE_DIR, "notes")

@mcp.resource("file://notes/{filename}")
def read_note(filename: str) -> str:
    filepath = os.path.join(NOTES_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# 方案 2：在配置文件中正确设置 cwd
# 见问题 1 的配置示例
```

### 3. 工具调用时参数错误

**症状：** AI 调用工具时报 "Invalid parameters" 或参数类型不匹配。

**原因：** 函数签名的类型注解不准确。

**解决方案：**

```python
# ❌ 错误示例：缺少类型注解
@mcp.tool()
def add(a, b):  # fastmcp 无法生成正确的参数规范
    return a + b

# ✅ 正确示例：添加类型注解
@mcp.tool()
def add(a: int, b: int) -> int:
    """两个整数相加"""  # 清晰的文档字符串也很重要
    return a + b

# ✅ 支持更复杂的类型
from typing import List, Optional

@mcp.tool()
def sum_list(numbers: List[int], multiplier: Optional[int] = 1) -> int:
    """对列表求和，可选地乘以倍数"""
    return sum(numbers) * multiplier
```

### 4. 虚拟环境相关问题

**症状：** 模块找不到，或者版本冲突。

**解决方案：**

```bash
# 确认虚拟环境位置
which python  # 应该显示 .venv/bin/python

# 如果不在虚拟环境中，激活它
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 重新安装依赖
uv pip install fastmcp

# 在 Trae IDE 配置中使用虚拟环境的 Python
{
  "command": "/完整路径/my-first-mcp-server/.venv/bin/python",
  "args": ["server.py"],
  "env": {},
  "cwd": "/完整路径/my-first-mcp-server"
}
```

### 5. Windows 路径问题

**症状：** Windows 下配置文件中的路径报错。

**解决方案（Trae IDE 配置）：**

```json
{
  "command": "C:\\Users\\YourName\\my-first-mcp-server\\.venv\\Scripts\\python.exe",
  "args": ["server.py"],
  "env": {},
  "cwd": "C:\\Users\\YourName\\my-first-mcp-server"
}
```

**注意：**
- Windows 路径中的 `\` 必须转义为 `\\`
- 或者使用正斜杠 `/`（JSON 中也合法）：`"C:/Users/YourName/..."`

### 6. 如何调试 MCP Server？

**方法 1：使用日志**

```python
import logging

# 配置日志输出到文件（不能用 print，会干扰 stdio 通信）
logging.basicConfig(
    filename="mcp_server.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@mcp.tool()
def add(a: int, b: int) -> int:
    logging.info(f"add called with a={a}, b={b}")
    result = a + b
    logging.info(f"add returning {result}")
    return result
```

**方法 2：使用 MCP Inspector**

```bash
# 启动 Inspector
npx @modelcontextprotocol/inspector python server.py
```

Inspector 提供可视化界面，可以查看：
- 所有工具和资源列表
- 手动测试工具调用
- 原始 JSON 请求和响应
- 错误信息详情

## 术语速查表

| 术语 | 简短定义 |
|------|---------|
| **MCP** | Model Context Protocol，AI 的通用连接协议 |
| **Server** | 提供工具和数据的服务端（你开发的） |
| **Client** | 调用 Server 的 AI 工具（如 Trae IDE、Claude） |
| **Tool** | 可被 AI 调用的函数（执行操作） |
| **Resource** | 可被 AI 读取的数据（提供上下文） |
| **Prompt** | 可复用的提示模板 |
| **URI** | 资源的唯一标识符（如 `file://notes/todo.txt`） |
| **JSON-RPC** | MCP 基于的消息协议 |
| **Request** | 客户端向服务端发送的请求消息 |
| **Response** | 服务端返回的响应消息 |
| **Notification** | 单向通知消息（不需要回复） |
| **Capability** | 服务端或客户端声明的能力 |
| **Session** | 一次完整的连接会话（从握手到关闭） |
| **stdio** | 标准输入输出传输方式（本地 Server 默认方式） |
| **Subscription** | 资源订阅机制（资源变化时主动通知） |

## 进阶学习路线

### 阶段 1：扩展当前 Server（1-2 天）

**目标：** 让你的 Server 更实用。

**建议任务：**

1. **添加更多工具**
   ```python
   @mcp.tool()
   def get_weather(city: str) -> str:
       """查询天气（可以先返回模拟数据）"""
       return f"{city} 今天晴天，25℃"

   @mcp.tool()
   def search_web(query: str) -> str:
       """网络搜索（可以调用真实 API）"""
       # 集成 Google Search API 或其他搜索服务
       pass
   ```

2. **实现资源订阅**
   ```python
   # 监控文件变化，自动通知客户端
   # fastmcp 提供了资源订阅的支持
   ```

3. **抽取配置到文件**
   ```python
   # 使用 .env 文件管理配置
   # 使用 YAML/TOML 定义工具和资源
   ```

### 阶段 2：理解更多 MCP 消息类型（2-3 天）

**目标：** 深入理解协议的其他特性。

**学习内容：**

1. **Prompts（提示模板）**
   ```python
   @mcp.prompt()
   def code_review(language: str) -> str:
       """生成代码审查提示"""
       return f"请审查以下 {language} 代码..."
   ```

2. **进度通知（Progress Notifications）**
   - 用于长时间运行的任务
   - 向客户端报告进度

3. **采样（Sampling）**
   - Server 请求 Client 调用 LLM
   - 用于需要 AI 协助的工具

**参考资料：**
- MCP 规范文档：https://modelcontextprotocol.io
- fastmcp 高级用法：https://gofastmcp.com/docs

### 阶段 3：集成真实服务（3-5 天）

**目标：** 让 Server 连接真实的数据和 API。

**项目建议：**

1. **数据库连接**
   ```python
   @mcp.tool()
   def query_users(name: str) -> str:
       """查询用户数据库"""
       # 连接 SQLite/PostgreSQL/MySQL
       pass

   @mcp.resource("database://users/{user_id}")
   def get_user_profile(user_id: int) -> str:
       """读取用户资料"""
       pass
   ```

2. **API 集成**
   ```python
   @mcp.tool()
   async def fetch_github_repo(owner: str, repo: str) -> str:
       """获取 GitHub 仓库信息"""
       # 调用 GitHub API
       pass
   ```

3. **文件系统操作**
   ```python
   @mcp.tool()
   def search_files(pattern: str, directory: str) -> str:
       """搜索文件"""
       # 使用 glob 或 ripgrep
       pass
   ```

### 阶段 4：部署与分享（5-7 天）

**目标：** 让其他人也能使用你的 Server。

**选项 1：发布为 Python 包**
```bash
# 打包为 pip 可安装的包
# 发布到 PyPI
uv build
uv publish
```

**选项 2：使用 FastMCP Cloud**
- fastmcp 提供托管服务
- 无需自己管理服务器

**选项 3：容器化部署**
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastmcp
CMD ["python", "server.py"]
```

**注意：** 远程部署时需要使用 SSE 或 HTTP 传输，而不是 stdio。

### 进阶主题（按需学习）

- **并发处理**：处理多个并发请求
- **错误处理与重试**：优雅处理失败场景
- **测试**：为你的工具编写单元测试
- **日志与监控**：生产环境的可观测性
- **安全性**：权限控制、输入验证、速率限制

## 学习资源

### 官方文档

- **MCP 官网**：https://modelcontextprotocol.io
  - 协议规范
  - 设计理念
  - 最佳实践

- **fastmcp 文档**：https://gofastmcp.com
  - API 参考
  - 高级特性
  - 示例代码

### 社区资源

- **GitHub Discussions**：https://github.com/modelcontextprotocol/specification/discussions
  - 提问和讨论
  - 查看其他人的实现

- **示例仓库**：https://github.com/modelcontextprotocol/servers
  - 官方维护的示例 Server
  - 覆盖各种使用场景

### 开发工具

- **MCP Inspector**：https://github.com/modelcontextprotocol/inspector
  - 可视化调试工具

- **MCP TypeScript SDK**：https://github.com/modelcontextprotocol/typescript-sdk
  - 如果你想用 TypeScript 开发

## 结语

恭喜你完成了 MCP Server 开发入门教程！你现在掌握了：

✅ MCP 的核心概念和价值
✅ 使用 fastmcp 快速开发 Server
✅ 定义工具和资源
✅ 连接客户端并测试
✅ 排查常见问题

**你现在可以：**
1. 为任何 API 或数据源创建 MCP Server
2. 让 AI 工具访问你的自定义功能
3. 构建个性化的 AI 助手工作流

**记住：** MCP 是一个开放标准，生态系统正在快速发展。保持关注官方动态，探索社区创造的新工具和最佳实践。

祝你在 MCP 开发之旅中收获满满！

---

**关键参考来源**
- MCP 核心理念："an open-source standard for connecting AI applications to external systems" ([modelcontextprotocol.io](https://modelcontextprotocol.io))
- fastmcp 定位："Fast, Pythonic way to connect LLMs to tools and data" ([gofastmcp.com](https://gofastmcp.com))
- JSON-RPC 2.0：MCP 的消息协议基础
- stdio 传输：本地 MCP Server 的标准通信方式
- 能力协商：MCP 会话初始化的关键步骤

**问题反馈**
如果你在学习过程中遇到问题：
- 查阅官方文档的 Troubleshooting 部分
- 在 GitHub Discussions 提问
- 查看社区的示例代码

继续探索，享受 MCP 开发的乐趣！

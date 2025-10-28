# MCP Server 项目规则 (FastMCP 框架)

MCP Server 开发的核心规范。专注于使用 **Python FastMCP 2.0+** 框架。

## 1. MCP 核心设计原则

### 1.1 Agent-Centric 设计
**为 AI Agent 设计，而非人类用户**

✅ 好的工具名称:
- `get_user_profile` (任务导向)
- `schedule_event` (整合操作)
- `search_issues` (清晰动词)

❌ 不好的工具名称:
- `get_api_v1_users_by_id` (API 端点风格)
- `post_api_events_create` (技术实现细节)

### 1.2 工作流优先
整合相关操作为完整任务，减少工具调用次数。

✅ 好: `schedule_event()` - 检查可用性、创建事件、发送邀请
❌ 不好: 分离为 `check_availability()`, `create_event()`, `send_invitation()`

### 1.3 上下文优化
- **字符限制**: 25,000 tokens
- **响应选项**: `concise` (简洁) vs `detailed` (详细)
- **标识符**: 使用名称而非 ID

### 1.4 可操作的错误
错误消息必须包含:
1. 具体错误原因
2. 可操作的建议
3. 使用示例

```python
# ✅ 好的错误
from fastmcp.exceptions import ToolError

raise ToolError(
    """Too many results (500+). Try:
1. Use filter='status:active'
2. Narrow date range to last 30 days
3. Add specific keywords

Example: search_issues(query='bug auth', state='open', limit=20)"""
)

# ❌ 不好的错误
raise Exception("Invalid request")
```

---

## 2. FastMCP 框架要求

### 2.1 版本
- 必须使用 **FastMCP 2.0+**
- `fastmcp>=2.0.0` 在依赖中

### 2.2 核心特性
- 使用 `@mcp.tool` 装饰器注册工具
- Pydantic v2 模型用于输入验证
- 所有 I/O 操作使用 `async`/`await`
- 完整的类型提示
- 支持 stdio 和 http 传输协议

---

## 3. 传输协议选择

### 3.1 STDIO 传输（默认）

**适用场景**：
```python
# 本地开发、Claude Desktop 集成、单用户应用
if __name__ == "__main__":
    mcp.run()  # 默认 stdio
```

**特点**：
- 通过标准输入/输出通信
- 客户端管理服务器生命周期
- 无需网络配置
- 适合本地工具和命令行脚本

**何时使用**：
- ✅ 本地开发和测试
- ✅ Claude Desktop 集成
- ✅ 命令行工具
- ✅ 单用户应用
- ❌ 需要远程访问
- ❌ 多客户端场景

### 3.2 Streamable HTTP 传输

**适用场景**：
```python
# 远程访问、多客户端、Web 集成
if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
```

**特点**：
- Web 服务，通过 HTTP 访问
- 支持多客户端同时连接
- 完整的双向通信
- 服务在 `/mcp/` 路径

**何时使用**：
- ✅ 网络可访问性需求
- ✅ 多个并发客户端
- ✅ 与 Web 基础设施集成
- ✅ 远程部署
- ❌ 简单本地工具

### 3.3 决策指南

**开发阶段**：
- 使用 stdio + `fastmcp dev` 进行调试
- MCP Inspector 提供可视化测试界面

**生产部署**：
- 本地/单用户 → stdio
- 远程/多用户 → http

---

## 4. 项目结构

```
mcp-server-{name}/
├── src/
│   └── mcp_server_{name}/
│       ├── server.py           # MCP server 主文件
│       ├── tools/              # 工具实现
│       │   ├── __init__.py
│       │   ├── search.py
│       │   └── content.py
│       └── utils/              # 共享工具
│           ├── __init__.py
│           ├── api_client.py   # API 请求
│           ├── formatters.py   # 响应格式化
│           ├── errors.py       # 错误处理
│           └── pagination.py   # 分页辅助
├── tests/
├── pyproject.toml
└── README.md
```

---

## 5. 工具开发规范

### 5.1 输入验证（Pydantic v2）

```python
from pydantic import BaseModel, Field
from typing import Literal

class ToolInput(BaseModel):
    model_config = {"extra": "forbid"}

    query: str = Field(
        description="Search query. Examples: 'bug', 'feature request'",
        min_length=1,
        max_length=200,
        examples=["bug in auth", "feature: dark mode"]
    )

    format: Literal["json", "markdown"] = Field(
        default="json",
        description="Response format"
    )

    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="Detail level"
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max results (1-100)"
    )
```

### 5.2 工具实现

```python
from fastmcp import FastMCP

mcp = FastMCP("ServiceName MCP Server")

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def search_items(input: ToolInput) -> str:
    """
    Search items with filters.

    Use this tool when you need to find specific items or analyze patterns.
    Do not use this for creating or modifying items.

    Args:
        query: Keywords to search (e.g., "bug", "feature")
        format: Output format - "json" for structured data, "markdown" for readable text
        detail: "concise" returns summary, "detailed" returns full information
        limit: Maximum results to return (1-100)

    Returns:
        Formatted list of items matching the query

    Examples:
        search_items(query="bug", format="json", detail="concise", limit=20)
        search_items(query="feature request", format="markdown", detail="detailed")

    Error Handling:
        - Invalid query: Provide non-empty search terms
        - Too many results: Narrow query or reduce limit
        - Rate limited: Wait before retry (see error message for duration)
        - Authentication failed: Check API_TOKEN environment variable
    """
    from .utils.api_client import make_api_request
    from .utils.formatters import format_response
    from fastmcp.exceptions import ToolError

    try:
        # 1. 使用 API client 获取数据
        data = await make_api_request(
            "search",
            params={"q": input.query, "limit": input.limit}
        )

        # 2. 格式化响应
        response = format_response(
            data,
            format=input.format,
            detail=input.detail
        )

        return response

    except Exception as e:
        raise ToolError(
            f"""Search failed: {str(e)}

Suggestions:
1. Check API_TOKEN environment variable is set
2. Verify network connection
3. Try a simpler query

Example: search_items(query="bug", limit=10)"""
        )
```

### 5.3 工具文档要求

每个工具必须包含：
1. 一行摘要
2. 详细说明
3. 参数描述（含示例）
4. 返回值说明
5. 使用场景（何时用/不用）
6. 错误处理指南
7. 使用示例

### 5.4 工具注解

```python
# 只读操作
annotations = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True
}

# 创建操作
annotations = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,  # 多次调用创建多个
    "openWorldHint": True
}

# 删除操作
annotations = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,   # 删除已删除的无影响
    "openWorldHint": True
}
```

---

## 6. 响应格式

### 6.1 支持 JSON 和 Markdown

```python
import json
from typing import Any, Literal

def format_response(
    data: Any,
    format: Literal["json", "markdown"],
    detail: Literal["concise", "detailed"]
) -> str:
    if format == "json":
        if detail == "concise":
            return json.dumps({
                "title": data["title"],
                "url": data["url"],
                "status": data["status"]
            })
        else:
            return json.dumps(data, indent=2)

    else:  # markdown
        if detail == "concise":
            return f"**{data['title']}** ({data['status']})\n{data['url']}"
        else:
            return f"""# {data['title']}
**Status**: {data['status']}
**URL**: {data['url']}

## Description
{data['body']}"""
```

### 6.2 字符限制和截断

```python
CHARACTER_LIMIT = 25000 * 4  # ~25k tokens

def truncate_response(text: str, max_chars: int = CHARACTER_LIMIT) -> str:
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    return f"""{truncated}

... [Response truncated due to length]

To get complete info:
1. Use more specific filters
2. Request smaller batches
3. Use 'concise' detail level"""
```

---

## 7. 错误处理

### 7.1 使用 FastMCP ToolError

```python
from fastmcp.exceptions import ToolError

# ToolError 消息始终发送给客户端
# 即使 mask_error_details=True
raise ToolError(
    """Authentication failed: Invalid token

Suggestions:
1. Check API_TOKEN environment variable is set
2. Verify token is valid and not expired
3. Ensure token has required permissions

Example:
export API_TOKEN=your_token_here"""
)
```

### 7.2 常见错误模式

**认证失败**：
```python
if not API_TOKEN:
    raise ToolError(
        """API token not configured

Set the API_TOKEN environment variable:
export API_TOKEN=your_token_here"""
    )
```

**速率限制**：
```python
if response.status_code == 429:
    retry_after = response.headers.get("Retry-After", "60")
    raise ToolError(
        f"""Rate limit exceeded

Wait {retry_after} seconds before retrying.
Reduce request frequency or upgrade API plan."""
    )
```

**资源未找到**：
```python
if response.status_code == 404:
    raise ToolError(
        f"""Resource '{resource_id}' not found

Check:
1. Resource name/ID is correct
2. Resource still exists
3. You have permission to access it

Example: get_resource(id="valid-resource-id")"""
    )
```

---

## 8. 性能和限制

### 8.1 分页

```python
from typing import Callable, List, Any

async def paginate_results(
    fetch_fn: Callable,
    per_page: int = 30,
    max_pages: int = 10,
    max_total: int = 1000
) -> List[Any]:
    """处理 API 分页"""
    results = []
    page = 1

    while page <= max_pages and len(results) < max_total:
        page_results = await fetch_fn(page=page, per_page=per_page)
        if not page_results:
            break
        results.extend(page_results)
        page += 1

    return results[:max_total]
```

### 8.2 速率限制处理

```python
import asyncio
from datetime import datetime
from fastmcp.exceptions import ToolError

async def handle_rate_limit(response):
    """处理速率限制"""
    if response.status == 429:
        reset_time = response.headers.get('X-RateLimit-Reset')
        if reset_time:
            wait_seconds = int(reset_time) - int(datetime.now().timestamp())
        else:
            wait_seconds = 60

        raise ToolError(
            f"""Rate limit exceeded

Wait {wait_seconds} seconds before retrying.
Current limit: {response.headers.get('X-RateLimit-Limit', 'unknown')}/hour"""
        )
```

---

## 9. 代码质量

### 9.1 DRY 原则

```python
# ✅ 好：提取共享逻辑
import httpx
from typing import Any, Dict, Optional

async def make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """通用 API 请求函数"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    url = f"{BASE_URL}/{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method, url,
            headers=headers,
            params=params,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

# ❌ 不好：重复代码
async def get_user(user_id: str):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = await httpx.get(f"{BASE_URL}/users/{user_id}", headers=headers)
    return response.json()

async def get_project(project_id: str):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = await httpx.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
    return response.json()
```

### 9.2 类型安全

```python
# 完整的类型提示
from typing import List, Dict, Optional, Literal, Any

async def search_items(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    format: Literal["json", "markdown"] = "json"
) -> str:
    """搜索项目"""
    pass
```

### 9.3 异步操作

```python
# ✅ 所有 I/O 操作必须异步
import httpx

async def fetch_data(url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

---

## 10. 开发和调试

### 10.1 使用 fastmcp dev

```bash
# 使用 MCP Inspector 调试
fastmcp dev src/mcp_server_{name}/server.py

# 指定服务器对象
fastmcp dev src/mcp_server_{name}/server.py:mcp

# 使用额外依赖
fastmcp dev server.py --with pandas --with httpx

# 使用 requirements 文件
fastmcp dev server.py --with-requirements requirements.txt
```

**不要直接运行 `python server.py`** - MCP 服务器会挂起等待 stdio 输入。

### 10.2 MCP Inspector

`fastmcp dev` 启动 MCP Inspector，提供：
- 可视化工具测试界面
- 实时查看工具调用和响应
- 交互式调试
- 通常在 `http://localhost:5173`

### 10.3 安装到客户端

```bash
# 安装到 Claude Desktop
fastmcp install claude-desktop server.py

# 安装到 Claude Code
fastmcp install claude-code server.py --env API_KEY=xxx

# 安装到 Cursor
fastmcp install cursor server.py
```

---

## 11. 测试

### 11.1 单元测试

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_search_items():
    with patch('api_client.make_api_request') as mock:
        mock.return_value = {"items": [{"title": "Test", "id": 1}]}

        result = await search_items(
            ToolInput(query="bug", limit=10)
        )

        assert "Test" in result
        mock.assert_called_once()
```

### 11.2 评估测试

创建 10 个评估问题：
- 独立（不依赖其他问题）
- 只读操作
- 需要多次工具调用（3-5+）
- 真实使用场景
- 答案可验证且稳定

---

## 12. 安全

```python
# ✅ 使用环境变量
import os
API_TOKEN = os.getenv("API_TOKEN")

# ❌ 硬编码
API_TOKEN = "ghp_xxxxxxxxxxxx"
```

- 使用 Pydantic 验证所有输入
- 不在日志中记录 tokens
- 不在错误消息中暴露敏感信息
- 使用 `model_config = {"extra": "forbid"}` 防止额外字段

---

## 13. 主服务器文件模板

```python
# src/mcp_server_{name}/server.py
from fastmcp import FastMCP
from .tools.search import search_items
from .tools.content import get_content
# 导入其他工具...

# 创建 FastMCP 实例
mcp = FastMCP(
    name="ServiceName MCP Server",
    instructions="A MCP server for interacting with ServiceName API"
)

# 工具已通过 @mcp.tool 装饰器自动注册

if __name__ == "__main__":
    # 从规范中确定的传输协议

    # 选项 1: STDIO（默认，用于本地/Claude Desktop）
    mcp.run()

    # 选项 2: HTTP（用于远程访问/多客户端）
    # mcp.run(transport="http", host="127.0.0.1", port=8000)
```

---

## 14. Spec-Driven 开发流程

### 规范阶段
`@MCP Spec Architect`:
1. API 深度调研 → `api-research.md`
2. 工具设计 → `tool-design.md`
3. **传输协议决策** → `transport-decision.md`
4. 完整规范 → `spec.md`

### 实现阶段
`@MCP Implementation Builder`:
1. 创建 FastMCP 项目结构
2. 实现共享基础设施（API client, formatters, errors）
3. 使用 `@mcp.tool` 实现工具
4. 配置传输协议（stdio 或 http）

### 调试阶段
使用 `fastmcp dev` 进行交互式调试：
1. 启动 MCP Inspector
2. 可视化测试工具
3. 实时查看调用和响应

### 评估阶段
`@MCP Evaluator`:
1. 创建 10 个评估问题 → `evaluations.xml`
2. 验证 LLM 能否用 Server 回答问题

### 部署阶段
使用 `fastmcp install` 安装到客户端：
1. 配置环境变量
2. 指定依赖
3. 选择传输协议

---

## 检查清单

**每个工具必须**：
- [ ] 使用 `@mcp.tool` 装饰器
- [ ] Pydantic v2 输入验证
- [ ] 完整的 docstring（用途、参数、返回值、示例、错误处理）
- [ ] 支持 json/markdown 格式
- [ ] 支持 concise/detailed 级别
- [ ] 使用 `ToolError` 提供可操作的错误消息
- [ ] 正确的工具注解
- [ ] 完整的类型提示
- [ ] 异步 I/O 操作（`async`/`await`）

**项目必须包含**：
- [ ] README with 安装和使用说明
- [ ] pyproject.toml 配置
- [ ] API 调研文档
- [ ] 工具设计文档
- [ ] **传输协议决策文档**
- [ ] 完整的规范文档
- [ ] 单元测试
- [ ] 评估测试（10 个问题）
- [ ] 使用 `fastmcp dev` 测试验证

**传输协议**：
- [ ] 明确选择 stdio 或 http
- [ ] 记录选择理由
- [ ] 配置正确的运行方式
- [ ] 文档中说明调试和部署方法

---

**遵循这些规则以确保高质量的 FastMCP Server 实现！**

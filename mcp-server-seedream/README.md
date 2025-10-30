# 即梦 Seedream 4.0 MCP Server

这是一个使用 FastMCP 框架开发的 MCP 服务器，用于连接即梦 Seedream 4.0 图像生成 API。

## 功能特性

- 高质量图像生成
- 支持单图生成和批量生成
- 所有生成的图像默认不带水印
- 支持多种输出格式（JSON/Markdown）
- 支持不同详细程度的输出
- 使用 STDIO 传输协议，适合本地使用

## 安装

### 1. 克隆项目

```bash
git clone [repository-url]
cd mcp-server-seedream
```

### 2. 安装依赖

```bash
# 使用 pip 安装
pip install -e .

# 或者使用 poetry
poetry install
```

### 3. 配置环境变量

创建 `.env` 文件并设置 API 密钥：

```bash
# .env
ARK_API_KEY=your_api_key_here
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

## 使用

### 开发模式运行

使用 FastMCP 的开发工具运行服务器：

```bash
fastmcp dev src/mcp_server_seedream/server.py
```

这将启动 MCP Inspector UI（通常在端口 5173），您可以在其中测试和调试您的工具。

### 环境变量配置

### 方法1：使用 .env 文件（推荐）

1. 复制 `.env.example` 文件为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入您的 API 密钥：
   ```bash
   # .env
   SEEDREAM_API_KEY=your_api_key_here
   ```

### 方法2：使用系统环境变量

运行前设置以下环境变量：

```bash
export SEEDREAM_API_KEY="your_api_key_here"
```

### 环境变量说明

- `SEEDREAM_API_KEY`：您的 Seedream API 密钥（必需）
- `API_BASE_URL`：API 基础 URL，默认为 `https://api.seedream.ai`
- `REQUEST_TIMEOUT`：请求超时时间（秒），可选配置，默认为 30

## 支持的工具

### 1. generate_image

根据文本描述生成单张高质量图像。

**参数：**
- `prompt`: 详细的图像描述文本，支持中英文（1-600字符）
- `size`: 生成图像的尺寸（默认："2048x2048"）
- `response_format`: 返回格式（"url" 或 "b64_json"，默认："url"）
- `optimize_prompt`: 是否优化提示词（默认：True）
- `format`: 输出格式（"json" 或 "markdown"，默认："json"）
- `detail`: 详细程度（"concise" 或 "detailed"，默认："concise"）

### 2. generate_image_group

批量生成多张高质量图像。

**参数：**
- `prompts`: 详细的图像描述文本列表（1-10个提示词，每个1-600字符）
- `size`: 生成图像的尺寸（默认："2048x2048"）
- `response_format`: 返回格式（"url" 或 "b64_json"，默认："url"）
- `optimize_prompt`: 是否优化提示词（默认：True）
- `format`: 输出格式（"json" 或 "markdown"，默认："json"）
- `detail`: 详细程度（"concise" 或 "detailed"，默认："concise"）

## 示例

### 使用 generate_image

```python
from fastmcp import FastMCP

# 连接到服务器
client = FastMCP()

# 生成图像
result = await client.generate_image(
    prompt="一只可爱的小猫在沙发上睡觉",
    format="markdown",
    detail="detailed"
)

print(result)
```

### 使用 generate_image_group

```python
result = await client.generate_image_group(
    prompts=["一只小猫", "一只小狗", "一片森林"],
    size="1K",
    format="json",
    detail="concise"
)

print(result)
```

## 调试

使用 `fastmcp dev` 命令启动开发模式，这将：
1. 自动管理依赖
2. 启动 MCP Inspector UI
3. 提供交互式调试界面
4. 实时显示日志和错误信息

## 错误处理

服务器实现了完善的错误处理机制，包括：
- API 密钥验证
- 提示词长度限制
- 请求频率限制
- 网络错误重试
- 友好的错误提示和建议

## 注意事项

1. 所有生成的图像默认不带水印
2. 单个提示词最长支持600字符
3. 批量生成最多支持10张图像
4. 请确保您的 API 密钥有足够的配额
5. 如遇请求频率限制，请稍后重试

## 许可证

[MIT License](LICENSE)
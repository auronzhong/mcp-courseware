# 认识 MCP：AI 的通用连接标准

## 开始之前的小故事

想象一下，你刚买了一台新电脑，想连接鼠标、键盘、U盘、移动硬盘……如果每个设备都需要不同的接口，你的电脑上就得有几十个不同形状的插孔。幸运的是，我们有了 USB 标准——一个接口，适配所有设备。

AI 世界也面临着同样的问题。每个 AI 工具（比如 ChatGPT、Claude）想要访问你的日历、读取文件、查询数据库时，都需要为每个工具单独编写对接代码。这不仅重复劳动，而且一旦工具升级，所有对接代码都要重写。

**MCP（Model Context Protocol，模型上下文协议）** 就是为解决这个问题而生的——**它是 AI 的 USB 标准**。

## 三个核心问题

### 1. 为什么需要 MCP？

在 MCP 出现之前，开发者面临三大痛点：

**痛点一：工具接入割裂**
- 你为 ChatGPT 写了一个天气查询工具
- 想让 Claude 也用？抱歉，得重写一遍
- 每个 AI 工具都有自己的接入方式，无法复用

**痛点二：可移植性差**
- 用户从一个 AI 助手切换到另一个时，所有配置好的工具和数据连接都得推倒重来
- 就像从 iPhone 换到安卓手机，所有应用都要重新下载

**痛点三：重复适配的噩梦**
- 有 10 个 AI 工具要对接？那就得写 10 套代码
- AI 工具更新了接口？所有代码都要跟着改
- 维护成本呈指数级增长

> 来源：基于 [modelcontextprotocol.io](https://modelcontextprotocol.io) 对 MCP 设计目标的总结

### 2. MCP 的核心价值是什么？

MCP 通过**标准化**解决了上述所有问题：

**价值一：一次接入，到处运行**
```
写一个 MCP Server ──→ 所有支持 MCP 的 AI 工具都能用
     ↓
就像插入 USB 设备，不用管是 Mac 还是 Windows
```

**价值二：工具与 AI 解耦**
- 你的天气查询工具只需遵循 MCP 规范
- 不用关心调用它的是 ChatGPT、Claude 还是未来的新 AI
- AI 工具升级？你的代码一行都不用改

**价值三：更易测试和调试**
- 标准化的消息格式（基于 JSON-RPC 2.0）
- 明确的错误处理机制
- 可以独立测试你的 MCP Server，不依赖具体 AI 工具

> 来源：基于 [modelcontextprotocol.io](https://modelcontextprotocol.io) 对 MCP 优势的说明

### 3. 学完本教程你能做什么?

跟着这个教程，**30-45 分钟内**你将：

- ✅ 理解 MCP 的核心工作原理（用类比和图示，不需要深入协议细节）
- ✅ 用 **fastmcp** 框架搭建一个最小可运行的 MCP Server
- ✅ 实现 2 个工具（Tool）：文本回显和加法计算
- ✅ 实现 1 个资源（Resource）：读取本地文件
- ✅ 用现成的客户端（如 Trae IDE）连接并调用你的 Server

**不需要你：**
- ❌ 有网络编程经验
- ❌ 了解异步编程
- ❌ 理解 JSON-RPC 协议细节
- ❌ 编写任何客户端代码

只需要你：
- ✅ 会运行 Python 脚本
- ✅ 会用命令行执行简单命令
- ✅ 愿意跟着一步步操作

## 术语速览表

在开始之前，快速认识这些核心术语（别担心，后面会详细解释）：

| 术语 | 一句话解释 | 类比 |
|------|-----------|------|
| **MCP** | AI 的通用连接协议 | USB 标准 |
| **Server** | 你开发的服务，提供工具和数据 | U盘（存储设备） |
| **Client** | 调用你服务的 AI 工具 | 电脑（使用设备） |
| **Tool** | 可被 AI 调用的函数 | 计算器功能 |
| **Resource** | 可被 AI 读取的数据 | 文件内容 |
| **Prompt** | 可复用的提示模板 | 快捷短语 |
| **Session** | 一次连接会话 | 插入 USB 到拔出的整个过程 |
| **Capability** | 服务声明自己能做什么 | 设备说明书 |
| **Request** | 客户端向服务端发起的请求 | 你点击"打开文件" |
| **Response** | 服务端返回的结果 | 文件内容显示出来 |
| **Notification** | 单向消息，不需要回复 | 设备状态灯亮起 |

> 来源：基于 [MCP 规范](https://modelcontextprotocol.io) 和 [fastmcp 文档](https://gofastmcp.com) 整理

## 下一步

现在你已经理解了 MCP 的"为什么"，接下来我们将深入了解 MCP 的核心工作机制——别担心，我们会用图示和类比让一切变得简单。

👉 [下一章：核心概念易懂版](./02-mcp-basics-concepts.md)

---

**参考资料**
- MCP 官方网站：https://modelcontextprotocol.io
- fastmcp 框架：https://gofastmcp.com
- MCP 设计理念："an open-source standard for connecting AI applications to external systems" (来自官网首页)

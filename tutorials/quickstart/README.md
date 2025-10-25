# MCP Server 开发快速入门教程

欢迎来到 **模型上下文协议（MCP）Server 开发**入门教程！

## 教程概述

本教程专为**零基础初学者**设计，帮助你在 **30-45 分钟内**理解 MCP 的核心价值，并使用 `fastmcp` 框架成功构建一个可运行的 MCP 服务器。

### 你将学到

- ✅ MCP 协议的核心价值和工作原理
- ✅ 使用 fastmcp 快速开发 MCP Server
- ✅ 实现工具（Tool）和资源（Resource）
- ✅ 连接现成客户端（如 Trae IDE）进行测试
- ✅ 常见问题排查和进阶学习路线

### 学习前提

只需要你：
- ✅ 会基本的电脑操作
- ✅ 会运行 Python 脚本
- ✅ 会使用命令行执行简单命令

**不需要：**
- ❌ 网络编程经验
- ❌ 异步编程知识
- ❌ JSON-RPC 协议背景

## 教程结构

本教程分为 5 个章节，建议按顺序阅读：

### [第 1 章：认识 MCP](./01-what-and-why-mcp.md)
**阅读时间：5-8 分钟**

通过故事化场景了解：
- 为什么需要 MCP？
- MCP 解决了什么问题？
- 学完教程你能做什么？
- 核心术语速览表

### [第 2 章：核心概念易懂版](./02-mcp-basics-concepts.md)
**阅读时间：10-15 分钟**

用图示和类比理解：
- Client 和 Server 的角色
- 消息模型（Request/Response/Notification）
- 会话生命周期（握手 → 交互 → 结束）
- 核心组件（Tool、Resource、Prompt）
- 能力协商机制
- 完整的工具调用流程

**亮点：** 包含 6 个 Mermaid 图表，图文并茂！

### [第 3 章：最小 MCP Server - 复制就能跑](./03-fastmcp-quickstart.md)
**实操时间：10-15 分钟**

手把手教你：
- 环境准备（uv + fastmcp）
- 编写第一个 MCP Server（完整代码）
- 实现 2 个工具：`echo` 和 `add`
- 实现 1 个资源：读取本地文件
- 运行并验证

**亮点：** 可直接复制运行的完整代码，带详细注释！

### [第 4 章：扩展功能并连接客户端](./04-extend-and-use.md)
**实操时间：10-15 分钟**

实战演练：
- 扩展资源功能（支持动态读取文件）
- 配置 Trae IDE 连接你的 Server
- 实际调用工具和读取资源
- 理解完整的调用流程

**亮点：** 包含配置示例和测试清单！

### [第 5 章：FAQ 与进阶路线](./05-faq-and-next.md)
**阅读时间：5-10 分钟**

扫除障碍，指明方向：
- 6 个常见问题及解决方案
- 术语速查表
- 4 阶段进阶学习路线
- 官方资源和社区链接

## 快速开始

```bash
# 克隆或下载教程代码
git clone <仓库地址>
cd tutorials/quickstart

# 开始学习
# 按顺序阅读 01 到 05 的 Markdown 文件
```

## 教程特色

1. **零门槛**：面向绝对初学者，用类比和图示解释所有概念
2. **实战导向**：30 分钟内就能运行起第一个 MCP Server
3. **只讲 Server 开发**：不涉及 Client 开发和复杂协议细节
4. **只用 fastmcp**：极大简化开发复杂度
5. **图文并茂**：6 个 Mermaid 图表辅助理解
6. **来源明确**：所有内容基于官方文档，标注来源

## 学习成果验收

完成本教程后，你应该能够：

- [ ] 解释 MCP 的核心价值（用"USB 标准"类比）
- [ ] 说清楚 Tool 和 Resource 的区别
- [ ] 独立编写一个包含工具和资源的 MCP Server
- [ ] 配置客户端连接你的 Server
- [ ] 成功调用 2 个工具、读取 1 个资源
- [ ] 排查基本的配置和路径问题

## 技术栈

- **Python 3.10+**
- **fastmcp** - MCP Server 开发框架
- **uv** - Python 环境管理工具
- **Trae IDE** - MCP 客户端（可选其他支持 MCP 的工具，如 Claude Desktop）

## 参考资料

- MCP 官方网站：https://modelcontextprotocol.io
- fastmcp 框架：https://gofastmcp.com
- MCP 规范：基于 JSON-RPC 2.0
- uv 工具：https://astral.sh/uv

## 版权与许可

本教程基于 MCP 官方文档和 fastmcp 文档创作，遵循开放标准精神。

教程内容引用来源：
- "an open-source standard for connecting AI applications to external systems" - modelcontextprotocol.io
- "Fast, Pythonic way to connect LLMs to tools and data" - gofastmcp.com

## 反馈与贡献

如有问题或建议，欢迎：
- 提交 Issue
- 参与 MCP 社区讨论：https://github.com/modelcontextprotocol/specification/discussions

祝学习愉快！🚀

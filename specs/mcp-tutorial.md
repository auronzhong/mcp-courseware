# 教程要求

## 核心目标

创建一个关于**模型上下文协议 (MCP) Server 开发**的入门教程。本教程的目标帮助一个**编程初学者背景**的读者，在最短时间内理解 MCP 的核心价值，并使用 `fastmcp` 框架成功构建一个可以运行的 MCP 服务器。

## 关键约束 (必须遵守)

1.  **受众：** 绝对的零基础初学者（例如，产品经理、设计师或任何 AI 爱好者）。假设读者可能刚刚才学会如何运行一个 Python 脚本。
2.  **技术栈：** **只使用 `fastmcp`**。所有开发示例必须基于 `fastmcp`，因为它极大地简化了协议的复杂性。总是使用 uv 做 python 环境管理。
3.  **范围：** **只讲 Server 开发**。完全不要提及 Client 端的开发、协议的二进制细节、网络握手或复杂的概念。
4.  **内容取舍：** 所有与快速上手无关的章节**尽量删除**，包括但不限于：安全合规、可观测性 (Observability)、性能调优、多种部署方式（如 Docker, K8s）、运维、高级流控等。
5.  **核心资料来源：** 教程内容必须基于以下来源：
    - 官方文档: https://modelcontextprotocol.io/
    - https://modelcontextprotocol.io/llms.txt
    - https://gofastmcp.com/llms.txt

---

## 1. 风格与语言

- 全程使用简体中文。
- 语气与风格： 亲切耐心、教程体，避免术语堆砌；每个概念先给类比再给准确定义，再配最小代码示例。
  参考类比示例：
  • MCP 就像“通用插座标准”：只要符合标准，不同厂商的工具都能“即插即用”。
  • 能力协商（capabilities） 像“会前自我介绍”：先说清楚我会什么、能提供什么，再开始协作。
  • Resource 订阅 像“关注网盘文件夹”：文件一变更就自动收到提醒。
- 读者预设： 会基本电脑操作；不要求读者具备网络协议或异步编程背景。

## 3. Mermaid 图表 (简化)

使用 Mermaid 图表进行可视化, 为所有关键流程和复杂概念配上 Mermaid 图表，图文并茂地进行解释，辅助非技术读者理解。

## 4. 输出格式

- 请将所有内容生成为 Markdown (.md) 格式。
- 请将教程组织到 `tutorials/quickstart/` 文件夹下。
- 拆分为多个文件.

输出结构（5 个 Markdown 文件）

1. quickstart/01-what-and-why-mcp.md（认识 MCP）
   • 用故事化场景回答三个问题：
   1）为什么需要 MCP？（工具接入割裂、可移植性差、对不同模型/客户端重复适配）
   2）MCP 的核心价值？（标准化对接、一次接入多端复用、更易测试调试）
   3）学完本教程你能做什么？（本地起一个最小 MCP Server，并被客户端调用）
   • 一页术语速览表：Client、Server、Tool、Resource、Prompt、Session、Capability、Request/Response/Notification。
   • 在段落末尾标注来源（官网/ llms.txt），只引用必要原话或做意译。

2. quickstart/02-mcp-basics-concepts.md（核心概念易懂版）
   • 以图 + 类比 + 少量术语讲清：
   • 消息模型（基于 JSON-RPC 2.0 的 request/response/notification）
   • 能力协商（capabilities）与会话（session）
   • Tools（可调用函数）、Resources（可列举/读取/订阅）、Prompts（可复用提示）
   • 必须包含以下 Mermaid 图（简洁即可）：
   1）握手与能力协商时序图（sequenceDiagram）
   2）工具调用全链路时序图（sequenceDiagram）
   3）对象关系图（graph TD：Client、Server、Tool、Resource、Prompt 等）
   • 每个小节末尾标注对应官方文档/llms-full.txt 出处。

3. quickstart/03-fastmcp-quickstart.md — 复制就能跑：最小 MCP Server

目标：一步跑通。
必须包含：
• 环境准备命令。
• 唯一示例 server.py：
• Tool：echo(text)、add(a,b)（各 1 个最小实现）。
• Resource：读取本地 notes/hello.txt。
• 启动入口与启动日志（python server.py）。
• 代码仅加必要注释（标注对应 MCP 概念处+来源），不讲协议字段细节。
• 常见报错 3 条以内（端口、路径、依赖）。
代码要求：
• 先给完整最小版本（可直接运行），再逐段解释关键行。
• 所有请求/响应的字段名、错误结构需与规范吻合，并在注释处标注来源。

4. quickstart/04-extend-and-use.md — 小步扩展 & 用现成客户端连接

目标：在“能跑”的基础上做一点点增强，并用现成客户端验证闭环。
必须包含：
• 在 server.py 上小改动：
• 让 Resource 支持按路径读取一份文件。
• “如何连接现成客户端”（不写 UI 细节，仅 3–5 行步骤）： 1. 运行 python server.py 2. 在 Trae 添加你的本地 MCP Server 3. 试调用 echo / add，读取 hello.txt
• 一句话提示：客户端只是实现之一，我们专注服务端。

5. quickstart/05-faq-and-next.md — FAQ、进阶路线与术语速查

目标：扫清入门阶段的阻碍并给到下一步方向。
必须包含：
• FAQ（≤6 条，极简回答）：连不上 / 读不到文件 / 参数错误 / 虚拟环境 / 版本问题 / Windows 路径。
• 进阶清单（3–4 项）：并发更多工具、资源订阅、把配置抽到文件、了解更多消息类型。
• 术语速查表（10 行内，术语 → 一句话释义）。
• 统一的参考链接区：官方文档关键小节与 llms.txt。
来源标注：在参考链接区按条目标注来源名与定位提示。

⸻

验收标准 1. 读者可在 30–45 分钟内完成：安装 → 运行 server.py → 用现成客户端成功调用 2 个 Tool、读取 1 个 Resource。 2. 全文无冗余协议细节；代码仅 1 份可跑示例 + 小扩展。 3. 每处规范性内容都有简短来源。 4. 读者读完能说清：MCP 做什么、核心对象是什么、如何用 fastmcp 起一个可被客户端调用的 Server。

⸻

请读取 Trae 文档：https://docs.trae.ai/ide/model-context-protocol 然后将教程中配置和使用 MCP server 的示例统一改成 Trae IDE。

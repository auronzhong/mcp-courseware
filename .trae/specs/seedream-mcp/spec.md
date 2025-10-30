# 即梦Seedream 4.0 MCP Server 规范

## 1. Server 概述

### 1.1 名称与用途
**名称**: Seedream-Image-Generator MCP Server

**用途**: 为AI Agent提供即梦Seedream 4.0模型的图像生成能力，包括文生图、图生图、多图融合和组图生成等功能，简化API交互，优化Agent使用体验。

### 1.2 目标集成服务
火山引擎即梦Seedream 4.0 API
- 支持多种图像生成模式
- 提供高质量、高分辨率图像输出
- 灵活的参数配置选项

### 1.3 主要使用场景
- AI创意助手：为内容创作提供图像生成支持
- 设计辅助工具：帮助设计师快速生成概念图和变体
- 视觉内容生成：为文章、报告、演示文稿创建插图
- 图像修改与优化：基于参考图生成修改版本
- 多图生成：创建相关联的图像集合

### 1.4 传输协议选择

**选择**: STDIO

**理由**:
- 适用于本地开发和测试场景
- 实现简单，无需处理HTTP服务器复杂性
- 适合单用户使用场景
- 与Claude Desktop等客户端集成更简便
- 减少网络配置和安全管理的复杂性

## 2. 工具规范

### 2.1 generate_image (文生图)

**Tool Name**: generate_image

**Purpose**: 根据文本描述生成高质量图像，支持丰富的参数配置

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "详细的图像描述文本，支持中英文",
      "maxLength": 600,
      "required": true
    },
    "size": {
      "type": "string",
      "description": "生成图像的尺寸，如'2048x2048'或'1K'/'2K'/'4K'",
      "default": "2048x2048",
      "required": false
    },
    "response_format": {
      "type": "string",
      "description": "返回格式，可选'url'、'b64_json'或'local_file'（自动下载到本地并返回文件路径）",
      "enum": ["url", "b64_json", "local_file"],
      "default": "local_file",
      "required": false
    },
    "download_dir": {
      "type": "string",
      "description": "当response_format为'local_file'时，指定图片下载目录路径",
      "default": "./generated_images",
      "required": false
    },
    "optimize_prompt": {
      "type": "boolean",
      "description": "是否优化提示词",
      "default": true,
      "required": false
    }
  }
}
```

**Output Format**: JSON

**Response Options**:
- **concise**:
  ```json
  {
    "success": true,
    "image_url": "https://生成的图片URL",
    "local_path": "/path/to/saved/image.jpg",  // 当response_format为'local_file'时返回
    "token_usage": 1500
  }
  ```
- **detailed**:
  ```json
  {
    "success": true,
    "image_url": "https://生成的图片URL",  // 当response_format为'url'或'b64_json'时返回
    "local_path": "/path/to/saved/image.jpg",  // 当response_format为'local_file'时返回
    "image_size": "2048x2048",
    "token_usage": 1500,
    "created_at": "2024-01-01T12:00:00Z",
    "model_used": "doubao-seedream-4-0-250828",
    "processing_time_ms": 4200,
    "downloaded": true  // 当response_format为'local_file'时为true
  }
  ```

**Error Handling**:
- `INVALID_PROMPT`: 提示词格式不正确或包含敏感内容
  - 建议: 调整提示词内容，避免敏感词汇
- `INVALID_SIZE`: 尺寸参数不在支持范围内
  - 建议: 使用标准尺寸值如2048x2048或1K/2K/4K
- `RATE_LIMIT_EXCEEDED`: API调用频率超限
  - 建议: 减少请求频率，稍后再试
- `AUTHENTICATION_ERROR`: API密钥无效或过期
  - 建议: 检查并更新API密钥

**Tool Annotations**:
- `readOnlyHint`: false
- `destructiveHint`: false
- `idempotentHint`: false
- `openWorldHint`: true

### 2.2 generate_image_group (生成组图)

**Tool Name**: generate_image_group

**Purpose**: 生成一组内容相关的图像，适用于需要多角度展示同一主题的场景

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "详细的组图主题描述",
      "maxLength": 600,
      "required": true
    },
    "max_images": {
      "type": "integer",
      "description": "最多生成的图片数量",
      "minimum": 1,
      "maximum": 15,
      "default": 5,
      "required": false
    },
    "size": {
      "type": "string",
      "description": "生成图像的尺寸",
      "default": "2048x2048",
      "required": false
    },
    "response_format": {
      "type": "string",
      "description": "返回格式，可选'url'、'b64_json'或'local_file'（自动下载到本地并返回文件路径）",
      "enum": ["url", "b64_json", "local_file"],
      "default": "local_file",
      "required": false
    },
    "download_dir": {
      "type": "string",
      "description": "当response_format为'local_file'时，指定图片下载目录路径",
      "default": "./generated_images",
      "required": false
    }
  }
}
```

**Output Format**: JSON

**Response Options**:
- **concise**:
  ```json
  {
    "success": true,
    "images": ["https://图片1URL", "https://图片2URL"],  // 当response_format为'url'或'b64_json'时返回
    "local_paths": ["/path/to/saved/image1.jpg", "/path/to/saved/image2.jpg"],  // 当response_format为'local_file'时返回
    "total_images": 2,
    "token_usage": 3200
  }
  ```
- **detailed**:
  ```json
  {
    "success": true,
    "images": [
      {
        "image_url": "https://第一张图片URL",  // 当response_format为'url'或'b64_json'时返回
        "local_path": "/path/to/saved/image1.jpg",  // 当response_format为'local_file'时返回
        "image_size": "2048x2048",
        "downloaded": true  // 当response_format为'local_file'时为true
      },
      {
        "image_url": "https://第二张图片URL",  // 当response_format为'url'或'b64_json'时返回
        "local_path": "/path/to/saved/image2.jpg",  // 当response_format为'local_file'时返回
        "image_size": "2048x2048",
        "downloaded": true  // 当response_format为'local_file'时为true
      }
    ],
    "total_images": 2,
    "token_usage": 3200,
    "created_at": "2024-01-01T12:00:00Z",
    "model_used": "doubao-seedream-4-0-250828",
    "processing_time_ms": 12500,
    "download_dir": "/path/to/saved/images/"  // 当response_format为'local_file'时返回
  }
  ```

**Error Handling**:
- `MAX_IMAGES_OUT_OF_RANGE`: 图片数量超出有效范围
  - 建议: 设置1-15之间的数量
- `PARTIAL_FAILURE`: 部分图片生成失败
  - 建议: 使用成功生成的图片，或稍后重试

**Tool Annotations**:
- `readOnlyHint`: false
- `destructiveHint`: false
- `idempotentHint`: false
- `openWorldHint`: true



## 3. 共享基础设施

### 3.1 API 请求辅助函数
- **httpClient**: 用于发送HTTP请求到Seedream API
- **requestBuilder**: 构建符合API要求的请求参数
- **responseParser**: 解析API响应并转换为标准格式

### 3.2 错误处理工具
- **errorHandler**: 统一处理API错误并生成可操作的错误信息
- **retryStrategy**: 实现指数退避重试机制
- **validationErrorBuilder**: 生成参数验证错误信息

### 3.3 响应格式化函数
- **formatResponse**: 根据response_type格式化API响应
- **truncateLongText**: 截断过长的文本以控制响应大小
- **convertToBase64**: 将图像URL转换为Base64编码（如果需要）
- **downloadImage**: 下载图像到本地文件系统并返回文件路径

### 3.4 认证/令牌管理
- **apiKeyManager**: 安全存储和管理API密钥
- **tokenRefresh**: 处理令牌过期和刷新
- **authHeaderBuilder**: 构建认证请求头

## 4. 非功能需求

### 4.1 字符限制策略
- 响应内容默认限制: 25,000 tokens
- 超长响应自动转换为concise模式
- Base64图像数据优先使用URL替代以节省空间

### 4.2 速率限制处理
- 实现客户端和服务器端速率限制
- 请求频率超限自动队列化
- 提供速率限制状态信息

### 4.3 超时策略
- 连接超时: 30秒
- 读取超时: 60秒
- 图像生成超时: 120秒
- 超时自动重试（最多3次）

### 4.4 大规模使用支持
- 支持千级用户并发访问
- 请求队列管理和优先级排序
- 资源使用监控和告警

## 5. 部署配置

### 5.1 传输协议
- **类型**: STDIO
- **输入**: 标准输入（JSON格式）
- **输出**: 标准输出（JSON格式）

### 5.2 环境变量需求
- `ARK_API_KEY`: 火山引擎API密钥（必需）
- `API_BASE_URL`: API基础URL（可选，默认https://ark.cn-beijing.volces.com）
- `RESPONSE_MAX_TOKENS`: 响应最大token数（可选，默认25000）
- `DEFAULT_DOWNLOAD_DIR`: 默认图片下载目录（可选，默认"./generated_images"）

### 5.3 依赖列表
- Node.js 16+
- Express.js
- axios
- dotenv
- helmet
- express-rate-limit
- winston

## 6. 评估场景

### 场景1: 创意概念开发
**任务**: 为新产品创建一组概念图

1. 使用`configure_model_settings`设置默认参数
2. 使用`generate_image`生成初始概念草图
3. 使用`generate_image_from_reference`改进概念图
4. 使用`generate_image_group`生成多个变体
5. 使用`check_usage`查看资源消耗

### 场景2: 内容创作配图
**任务**: 为博客文章创建相关插图

1. 使用`generate_image`根据文章主题生成插图
2. 使用`generate_image_group`创建不同风格的版本
3. 选择最佳版本，使用`generate_image_from_reference`进行最后的调整

### 场景3: 图像风格转换
**任务**: 将多张照片转换为特定艺术风格

1. 使用`generate_image_from_multiple_references`上传多张参考照片
2. 提供详细的风格描述提示词
3. 获取融合风格的新图像

### 场景4: 产品多角度展示
**任务**: 创建产品的多角度视图

1. 使用`generate_image`创建产品主视图
2. 使用`generate_image_group`生成产品的多个角度视图
3. 使用`generate_image_from_reference`对特定视图进行细节优化

### 场景5: 故事板创建
**任务**: 为短视频创建故事板

1. 使用`generate_image_group`生成故事的关键场景
2. 使用`generate_image_from_reference`细化每个场景
3. 按顺序排列图像形成完整故事板

### 场景6: 角色设计迭代
**任务**: 设计并迭代角色形象

1. 使用`generate_image`创建初始角色设计
2. 使用`generate_image_from_reference`进行风格和细节调整
3. 使用`generate_image_group`生成角色的不同姿势和表情

### 场景7: 环境概念设计
**任务**: 设计游戏或电影场景

1. 使用`generate_image`创建基础环境概念
2. 使用`generate_image_from_reference`添加特定元素
3. 使用`generate_image_group`创建不同天气/时间条件下的同一环境

### 场景8: 图像修复和增强
**任务**: 修复旧照片并增强质量

1. 使用`generate_image_from_reference`上传需要修复的照片
2. 提供详细的修复和增强要求
3. 获取修复后的高质量图像

### 场景9: 虚拟试衣间概念
**任务**: 创建不同服装搭配效果图

1. 使用`generate_image_from_reference`上传模特照片
2. 使用`generate_image_from_multiple_references`融合服装元素
3. 为不同服装组合生成效果图

### 场景10: 教育插图创作
**任务**: 为教材创建教学插图

1. 使用`configure_model_settings`设置适合教育内容的参数
2. 使用`generate_image`创建清晰的教学概念图
3. 使用`generate_image_group`创建展示过程或步骤的系列图

## 7. 规范完整性检查清单

- [x] 明确每个工具的目的和价值
- [x] 包含详细的输入/输出设计
- [x] 定义清晰的错误处理策略
- [x] 考虑Agent的上下文限制
- [x] 提供真实的使用场景
- [x] 遵循MCP最佳实践
- [x] 明确传输协议选择及理由
- [x] 包含部署配置说明
- [x] 提供工具之间的协同关系
- [x] 定义非功能需求
- [x] 设计有效的错误信息
- [x] 考虑认证和安全性
- [x] 提供评估场景
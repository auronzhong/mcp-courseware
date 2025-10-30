# 即梦 Seedream 4.0 MCP Server 工具设计

## 1. 工具选择与优先级

基于对即梦Seedream 4.0 API的深入研究和用户需求，我们选择了以下核心工具：

### 优先级 1（核心功能）
1. **generate_image** - 文生图功能，根据文本描述生成高质量图像
2. **generate_image_group** - 生成组图功能，生成一组相关图像

## 2. 工具详细设计

### 2.1 generate_image (文生图)

**目的和价值**：
- 提供最基础的文本到图像生成功能
- 支持丰富的提示词描述，生成高质量图像
- 所有生成的图像默认不带水印

**输入设计**：
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

**输出设计**：
- **concise**：
  ```json
  {
    "success": true,
    "image_url": "https://生成的图片URL",
    "local_path": "/path/to/saved/image.jpg",  // 当response_format为'local_file'时返回
    "token_usage": 1500
  }
  ```

- **detailed**：
  ```json
  {
    "success": true,
    "image_url": "https://生成的图片URL",  // 当response_format为'url'或'b64_json'时返回
    "local_path": "/path/to/saved/image.jpg",  // 当response_format为'local_file'时返回
    "image_size": "2048x2048",
    "token_usage": 1500,
    "created_at": "2024-01-01T12:00:00Z",
    "model_used": "doubao-seedream-4-0-250828",
    "processing_time_ms": 4500,
    "watermark": false,
    "downloaded": true  // 当response_format为'local_file'时为true
  }
  ```

### 2.2 generate_image_group (生成组图)

**目的和价值**：
- 生成一组与主题相关的图像集合
- 提供多角度、多风格的同一主题展示
- 适用于故事板、角色设计、场景规划等场景
- 所有生成的图像默认不带水印

**输入设计**：
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
```

## 3. 工具协同关系

### 3.1 主要工作流

1. **单图像生成**
   - 使用 `generate_image` 生成单张高质量图像

2. **组图生成**
   - 使用 `generate_image_group` 生成一组相关图像
   - 适用于需要多角度展示同一主题的场景

### 3.2 工具依赖关系

- 两个生成工具共享相同的错误处理机制
- 输出格式保持一致，便于处理和集成
- 都基于即梦Seedream 4.0 API，确保生成质量一致

## 4. 设计原则考量

### 4.1 Agent-Centric 设计

- 工具名称反映具体任务，而非技术实现
- 参数设计简洁明了，减少认知负担
- 提供合理的默认值，减少不必要的参数指定
- 输出格式结构化，便于 Agent 解析和使用

### 4.2 工作流优先

- 工具设计围绕常见工作流展开
- 提供端到端的功能支持，从提示词输入到本地图片文件的完整流程
- 所有生成的图像默认不带水印，符合用户需求
- 自动下载功能简化了用户操作，无需手动保存图片

### 4.3 上下文优化

- 提供 concise/detailed 两种响应格式，适应不同上下文需求
- 精简输出内容，只包含核心信息
- 使用人类可读的标识符和描述
- 控制响应大小，避免上下文窗口过载

### 4.4 可操作的错误

- 错误信息具体明确，指出问题所在
- 提供解决建议和下一步操作指导
- 错误码设计有意义，便于诊断
- 对常见错误进行专门处理和引导

### 4.5 一致性设计

- 所有工具使用一致的参数命名和格式
- 输出结构统一，便于 Agent 处理
- 错误处理机制保持一致
- 功能描述和文档风格统一

## 5. 技术实现说明

### 5.1 STDIO 传输模式
- 使用标准输入输出进行通信
- 输入为 JSON 格式的请求
- 输出为 JSON 格式的响应
- 简化实现，专注于核心功能

### 5.2 水印设置
- 所有生成图像默认不带水印
- API 调用时自动设置 watermark=false
- 用户界面不提供水印选项，确保一致性

### 5.3 自动下载功能实现
- **下载机制**：当response_format设置为'local_file'时，自动从API返回的URL下载图片
- **文件管理**：
  - 使用时间戳和随机数生成唯一文件名
  - 自动创建不存在的下载目录
  - 支持自定义下载路径
- **错误处理**：针对下载过程中可能出现的网络问题、权限问题等提供专门的错误处理
- **性能优化**：异步下载机制，不阻塞主要功能流程
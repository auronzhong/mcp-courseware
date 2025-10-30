# 即梦seedream 4.0 API 研究报告

## 1. API概述

即梦seedream 4.0是火山引擎提供的高质量图像生成模型API，支持多种生成模式，包括文生图、图生图、多图融合和组图生成等功能。该API提供灵活的参数配置，能够生成高分辨率、高质量的AI图像。

## 2. 认证方式

- **认证类型**: Bearer Token认证
- **请求头格式**: `Authorization: Bearer $ARK_API_KEY`
- **API Key获取**: 需要通过火山引擎控制台获取API Key
- **API Key管理**: API Key需要妥善保管，避免泄露

## 3. 关键端点列表

### 3.1 图片生成API

- **端点URL**: `POST https://ark.cn-beijing.volces.com/api/v3/images/generations`
- **方法**: POST
- **内容类型**: application/json
- **功能**: 生成图像，支持文生图、图生图、多图融合和组图生成

## 4. 数据模型

### 4.1 请求参数

#### 必填参数
- `model`: string - 模型ID或推理接入点(Endpoint ID)，如"doubao-seedream-4-0-250828"
- `prompt`: string - 生成图像的提示词，支持中英文，建议不超过300个汉字或600个英文单词

#### 可选参数
- `image`: string/array - 输入图片信息，支持URL或Base64编码
  - 支持格式: jpeg、png
  - 图片大小: 不超过10MB
  - 总像素: 不超过6000×6000 px
  - doubao-seedream-4.0支持1-10张参考图

- `size`: string - 生成图像尺寸
  - 方式1: 指定分辨率(1K、2K、4K)
  - 方式2: 指定宽高像素值，如"2048x2048"
  - 默认值: "2048x2048"
  - 总像素范围: [1280x720, 4096x4096]

- `seed`: integer - 随机数种子，控制生成内容随机性，范围[-1, 2147483647]，默认-1
  - 注意：仅doubao-seedream-3.0-t2i和doubao-seededit-3.0-i2i支持

- `sequential_image_generation`: string - 组图功能控制
  - "auto": 自动判断是否返回组图
  - "disabled": 关闭组图功能，仅生成一张图
  - 默认值: "disabled"
  - 注意：仅doubao-seedream-4.0支持

- `sequential_image_generation_options`: object - 组图功能配置
  - `max_images`: integer - 最多可生成图片数量，范围[1, 15]，默认15
  - 注意：仅当sequential_image_generation为auto时生效

- `stream`: boolean - 是否开启流式输出
  - true: 流式输出，即时返回每张图片
  - false: 非流式输出，等待全部生成后返回
  - 默认值: false
  - 注意：仅doubao-seedream-4.0支持

- `guidance_scale`: float - 模型输出与提示词一致程度
  - 范围: [1, 10]
  - 默认值: doubao-seedream-3.0-t2i为2.5，doubao-seededit-3.0-i2i为5.5
  - 注意：doubao-seedream-4.0不支持

- `response_format`: string - 生成图像返回格式
  - "url": 返回图片下载链接(24小时内有效)
  - "b64_json": 返回Base64编码的图像数据
  - 默认值: "url"
  
## 4.3 MCP扩展功能

### 图片自动下载功能
MCP服务器扩展了原生API的功能，增加了图片自动下载能力：

- **自动下载模式**: MCP服务器可以将生成的图片自动下载到本地文件系统
- **配置选项**:
  - `response_format`: 增加"local_file"选项，启用自动下载
  - `download_dir`: 指定下载目录路径
- **实现机制**:
  1. 首先使用API获取图片URL
  2. 然后自动下载图片到指定目录
  3. 返回本地文件路径而不仅是URL
- **文件命名**: 使用时间戳和随机数生成唯一文件名
- **目录创建**: 自动创建不存在的下载目录

- `watermark`: boolean - 是否添加水印
  - true: 添加"AI生成"水印
  - false: 不添加水印
  - 默认值: true

- `optimize_prompt_options`: object - 提示词优化配置
  - `mode`: string - 优化模式
    - "standard": 标准模式，质量更高但耗时较长
    - "fast": 快速模式，耗时更短但质量一般
  - 默认值: "standard"
  - 注意：仅doubao-seedream-4.0支持

### 4.2 响应参数

#### 非流式响应
- `model`: string - 本次请求使用的模型ID
- `created`: integer - 请求创建时间戳(秒)
- `data`: array - 输出图像信息
  - 成功时包含url/b64_json和size信息
  - 失败时包含error对象，包含code和message
- `usage`: object - 请求用量信息
  - `generated_images`: integer - 成功生成的图片张数
  - `output_tokens`: integer - 生成图片花费的token数量
  - `total_tokens`: integer - 本次请求消耗的总token数量
- `error`: object - 如请求发生错误，包含错误信息

## 5. 支持的模型

1. **doubao-seedream-4.0**
   - 支持文生图、图生图、多图融合、组图生成
   - 支持流式输出
   - 支持提示词优化

2. **doubao-seedream-3.0-t2i**
   - 仅支持文生图
   - 支持seed参数
   - 支持guidance_scale参数

3. **doubao-seededit-3.0-i2i**
   - 仅支持图生图
   - 仅支持单图输入
   - 支持seed参数
   - 支持guidance_scale参数

## 5. MCP工作流增强

### 5.1 工作流优化
- **端到端体验**: 从提示词输入到本地图片文件的完整流程
- **批处理支持**: 组图生成时自动批量下载多张图片
- **文件管理**: 提供统一的下载目录管理

## 6. 限制和约束

### 6.1 图片限制
- 输入图片格式: jpeg、png
- 输入图片宽高比范围: [1/3, 3]
- 输入图片宽高长度(px) > 14
- 输入图片大小: 不超过10MB
- 输入图片总像素: 不超过6000×6000 px

### 6.2 生成限制
- 生成图片总像素范围: [1280x720, 4096x4096]
- 生成图片宽高比范围: [1/16, 16]
- 组图模式最多生成15张图片
- 多图输入最多支持10张参考图
- 输入图片数量+生成图片数量 ≤15张

### 6.3 其他限制
- 提示词长度: 建议不超过300个汉字或600个英文单词
- 图片URL有效期: 24小时
- 认证要求: 所有API调用需要有效的API Key

## 7. 错误处理

### 7.1 API错误
API可能返回的错误包括：
- 认证错误: API Key无效或过期
- 参数错误: 请求参数格式不正确或超出范围
- 内容审核错误: 提示词或生成内容不符合规范
- 服务器错误: 内部服务异常

### 7.2 MCP扩展错误
自动下载功能可能遇到的错误：
- `DOWNLOAD_ERROR`: 图片下载失败（网络问题或权限不足）
- `DISK_SPACE_ERROR`: 磁盘空间不足
- `PERMISSION_ERROR`: 无权限写入目标目录

## 8. 计费

- 计费方式: 按生成的图片数量计费
- 仅对成功生成的图片计费
- token计算逻辑: sum(图片长*图片宽)/256，取整
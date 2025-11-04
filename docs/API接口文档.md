# 图像相似度中间件服务API接口文档

本文档详细描述了图像相似度中间件服务提供的所有API接口，包括接口功能、请求参数、响应格式和使用示例。

## 基础信息

- 服务默认端口：`5000`
- 基础URL：`http://服务器IP:5000`
- 支持的图像输入方式：
  - 网络URL
  - Base64编码字符串
  - 本地文件路径（仅用于测试环境）

## 1. 健康检查接口

### 接口路径
`GET /api/health`

### 功能描述
检查服务是否正常运行。

### 请求参数
无

### 响应格式
```json
{
  "status": "ok",
  "timestamp": 1633046400.0
}
```

### 使用示例
```bash
curl http://localhost:5000/api/health
```

## 2. 单张对比图相似度计算接口

### 接口路径
`POST /api/image/similarity/single`

### 功能描述
计算两张图像之间的相似度，返回相似度分数。

### 请求参数
JSON格式，包含以下字段：
- `original_image`：原图（URL字符串或包含base64/path的对象）
- `compare_image`：对比图（URL字符串或包含base64/path的对象）

#### 请求示例（使用URL）
```json
{
  "original_image": "https://example.com/original.jpg",
  "compare_image": "https://example.com/compare.jpg"
}
```

#### 请求示例（使用Base64）
```json
{
  "original_image": {
    "base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA..." // 图像的Base64编码字符串
  },
  "compare_image": {
    "base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA..." // 图像的Base64编码字符串
  }
}
```

### 响应格式
成功时：
```json
{
  "similarity": 0.95,  // 相似度分数，范围0-1，值越大表示相似度越高
  "timestamp": 1633046400.0
}
```

失败时：
```json
{
  "error": "错误描述",
  "timestamp": 1633046400.0
}
```

### 使用示例
```bash
curl -X POST http://localhost:5000/api/image/similarity/single \
  -H "Content-Type: application/json" \
  -d '{"original_image": "https://example.com/original.jpg", "compare_image": "https://example.com/compare.jpg"}'
```

## 3. 多张对比图相似度计算接口

### 接口路径
`POST /api/image/similarity/multiple`

### 功能描述
计算一张原图与多张对比图之间的相似度，返回每张对比图的相似度分数。

### 请求参数
JSON格式，包含以下字段：
- `original_image`：原图（URL字符串或包含base64/path的对象）
- `compare_images`：对比图列表，每个元素是包含image字段的对象

#### 请求示例
```json
{
  "original_image": "https://example.com/original.jpg",
  "compare_images": [
    {
      "image": "https://example.com/compare1.jpg"
    },
    {
      "image": {
        "base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
      }
    },
    {
      "image": {
        "path": "/path/to/compare3.jpg"
      }
    }
  ]
}
```

### 响应格式
```json
{
  "results": [
    {
      "index": 0,
      "similarity": 0.95
    },
    {
      "index": 1,
      "similarity": 0.82
    },
    {
      "index": 2,
      "error": "图像数据不存在或格式错误"
    }
  ],
  "timestamp": 1633046400.0
}
```

### 使用示例
```bash
curl -X POST http://localhost:5000/api/image/similarity/multiple \
  -H "Content-Type: application/json" \
  -d '{"original_image": "https://example.com/original.jpg", "compare_images": [{"image": "https://example.com/compare1.jpg"}, {"image": "https://example.com/compare2.jpg"}]}'
```

## 4. 结合大模型对话的图像相似度计算接口

### 接口路径
`POST /api/image/similarity/llm`

### 功能描述
计算两张图像之间的相似度，并使用大模型生成关于这两张图像的比较分析。

### 请求参数
JSON格式，包含以下字段：
- `original_image`：原图（URL字符串或包含base64/path的对象）
- `compare_image`：对比图（URL字符串或包含base64/path的对象）
- `question`：用户问题，关于两张图像的比较

#### 请求示例
```json
{
  "original_image": "https://example.com/original.jpg",
  "compare_image": "https://example.com/compare.jpg",
  "question": "这两张图有什么相似之处和不同之处？"
}
```

### 响应格式
```json
{
  "similarity": 0.85,
  "original_image_description": "一张展示红色汽车的图片",
  "compare_image_description": "一张展示蓝色汽车的图片",
  "llm_response": "这两张图片都展示了汽车，相似度较高(0.85)。主要区别在于汽车的颜色，一张是红色，另一张是蓝色...",
  "timestamp": 1633046400.0
}
```

### 使用示例
```bash
curl -X POST http://localhost:5000/api/image/similarity/llm \
  -H "Content-Type: application/json" \
  -d '{"original_image": "https://example.com/original.jpg", "compare_image": "https://example.com/compare.jpg", "question": "这两张图有什么相似之处？"}'
```

## 图像数据格式规范

### URL格式
直接提供图像的完整URL：
```json
"image": "https://example.com/image.jpg"
```

### Base64格式
提供图像的Base64编码字符串：
```json
"image": {
  "base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA..." // 不包含data:image/jpeg;base64,前缀
}
```

### 本地文件路径格式（仅测试环境）
提供图像的本地文件路径：
```json
"image": {
  "path": "/path/to/image.jpg"
}
```

## 错误码说明

| 错误码 | 说明 | 可能原因 |
|-------|------|--------|
| 400 | 请求参数错误 | 图像数据格式错误、缺少必填参数 |
| 500 | 服务器内部错误 | 处理过程中发生异常 |

## 性能说明

- 单张图像相似度计算：通常在1-3秒内完成
- 多张图像相似度计算：时间与图像数量成正比
- LLM接口：受大模型响应时间影响，通常在3-10秒内完成

首次调用时会加载CLIP模型，可能需要额外的初始化时间。

## 最佳实践

1. **批量处理**：对于多张图像的相似度比较，优先使用`multiple`接口以提高效率
2. **图像预处理**：在发送到服务前，可以适当压缩图像以减少传输时间
3. **异步调用**：对于LLM接口，建议使用异步方式调用以提高用户体验
4. **错误处理**：实现完善的错误处理机制，特别是对图像格式的验证

## 安全建议

- 在生产环境中，建议限制API的访问来源
- 考虑设置请求频率限制，防止滥用
- 对于敏感图像数据，建议使用HTTPS传输

---

*本文档最后更新时间：2024年10月21日*
# 图像特征提取与相似度计算中间件

这是一个基于Python和CLIP模型的图像特征提取与相似度计算中间件服务，提供简单易用的API接口，支持图片文件和图片URL的处理。

## 功能特性

- **单张图片对比**：计算两张图片的相似度
- **多张图片对比**：计算一张原图与多张对比图的相似度
- **结合大模型**：支持与大语言模型集成，分析图片相似度并回答相关问题
- **多种输入方式**：支持图片URL、Base64编码和本地文件路径（仅测试环境）

## 安装与启动

请严格按照以下步骤安装：

### 1. 安装PyTorch（必须先安装）
根据您的系统选择：
```bash
# 对于支持CUDA的NVIDIA显卡
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 对于仅使用CPU的系统
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. 安装其他依赖
```bash
pip install -r requirements.txt
```

### 3. 启动服务

#### 开发环境启动
```bash
python app.py
```

#### Linux生产环境部署

server.sh脚本已针对Linux生产环境进行了优化，提供了完整的服务生命周期管理功能：

```bash
# 首先添加执行权限
chmod +x server.sh

# 启动服务（脚本会自动检测并使用venv虚拟环境）
./server.sh start

# 停止服务
./server.sh stop

# 查看服务状态
./server.sh status

# 重启服务
./server.sh restart

# 查看日志
./server.sh logs
```

##### 高级功能：部署为系统服务

对于长期运行的生产环境，建议将服务部署为systemd系统服务：

```bash
# 生成systemd服务配置文件
./server.sh sysd

# 按照脚本提示的步骤安装服务
# 1. 复制服务配置文件到系统目录
# 2. 重新加载systemd配置
# 3. 设置服务开机自启
# 4. 启动服务
```

##### 生产环境特性

优化后的脚本包含以下生产环境特性：
- **自动环境检测**：检查Python版本和端口占用情况
- **日志轮转**：自动管理日志文件大小，防止磁盘空间耗尽
- **权限管理**：正确设置日志和PID文件的权限
- **详细日志**：所有操作都有日志级别标记，便于问题排查
- **systemd集成**：支持一键生成为系统服务配置

**注意**：脚本会自动检测项目目录中的`venv`虚拟环境并优先使用其中的Python解释器，确保使用正确的依赖环境运行服务。

详细安装说明请参考：
- [安装指南](docs/安装指南.md) - 通用安装说明
- [Linux部署指南](docs/Linux部署指南.md) - Linux生产环境详细部署文档
- [API接口文档](docs/API接口文档.md) - 完整的API接口说明

## 前端用户界面

本服务提供了直观的Web用户界面，支持以下功能：

### 功能特点
- **单张图片对比**：上传两张图片并计算它们的相似度
- **多张图片对比**：上传一张原图和多张对比图，批量计算相似度并排序
- **AI智能分析**：上传图片并提出问题，获取AI对图片的分析和比较结果
- **可视化结果**：使用进度条和颜色直观展示相似度分数
- **响应式设计**：支持在桌面和移动设备上使用

### 访问方式
启动服务后，在浏览器中访问：
```
http://服务器IP:5000/
```

### 使用说明
1. 上传图片：点击对应的上传按钮选择本地图片
2. 查看预览：上传后可在预览区域查看图片
3. 执行操作：点击相应的按钮（计算相似度/获取AI分析）
4. 查看结果：结果将显示在页面下方，包括相似度分数和分析内容

服务将默认运行在 `http://0.0.0.0:5000`

## API接口

服务提供了以下核心API接口：

1. **健康检查**：`GET /api/health`
2. **单张对比图相似度计算**：`POST /api/image/similarity/single`
3. **多张对比图相似度计算**：`POST /api/image/similarity/multiple`
4. **结合大模型的图像相似度分析**：`POST /api/image/similarity/llm`

**完整的API接口文档**：请查看 [API接口文档](docs/API接口文档.md)，其中包含详细的请求参数说明、响应格式示例、使用方法和最佳实践指南。

## 配置说明

通过修改 `config.py` 文件可以配置应用的各项参数：

- `SECRET_KEY`：应用密钥，生产环境中应更改为随机密钥
- `MAX_CONTENT_LENGTH`：最大上传文件大小
- `LLM_CONFIG`：大语言模型配置，包括API类型、密钥等

默认情况下，LLM集成使用模拟响应。如果要使用实际的大语言模型API，请修改配置。

## 部署说明

### 开发环境

直接运行 `python app.py` 即可启动开发服务器。

### 生产环境

建议使用Gunicorn或uWSGI作为WSGI服务器，并配置Nginx作为反向代理。

**使用Gunicorn的示例**：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 扩展说明

### 添加新的大语言模型支持

1. 在 `llm_integration.py` 中扩展 `_call_external_api` 方法
2. 在配置文件中添加对应的API配置

### 自定义相似度计算

可以修改 `similarity_calculator.py` 中的 `calculate_similarity` 方法实现自定义的相似度计算逻辑。
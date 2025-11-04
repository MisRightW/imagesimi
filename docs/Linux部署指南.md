# Linux环境部署指南

本文档提供了在Linux服务器上部署图像相似度中间件服务的详细步骤和最佳实践。

## 系统要求

- Linux操作系统 (Ubuntu 20.04+/CentOS 8+ 推荐)
- Python 3.8+
- 至少2GB内存
- 至少5GB磁盘空间

## 1. 环境准备

### 更新系统软件包

```bash
# Ubuntu/Debian系统
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL系统
sudo yum update -y
```

### 安装必要的依赖

```bash
# Ubuntu/Debian系统
sudo apt install -y python3 python3-venv python3-pip git curl

# CentOS/RHEL系统
sudo yum install -y python3 python3-venv python3-pip git curl
```

## 2. 项目部署

### 创建项目目录

```bash
# 创建项目目录
mkdir -p /opt/imagesimi
cd /opt/imagesimi

# 获取项目文件（复制项目文件到此处）
```

### 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 安装依赖

```bash
# 安装PyTorch (选择合适的版本)
# CPU版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 或CUDA版本（如果服务器有NVIDIA GPU）
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装其他依赖
pip install -r requirements.txt
```

## 3. 运行服务

### 方法一：使用server.sh脚本（推荐）

```bash
# 添加执行权限
chmod +x server.sh

# 启动服务
./server.sh start
```

### 方法二：部署为systemd系统服务（长期运行）

```bash
# 生成systemd配置文件
./server.sh sysd

# 复制服务配置到系统目录
sudo cp image-similarity-service.service /etc/systemd/system/

# 重新加载systemd配置
sudo systemctl daemon-reload

# 设置开机自启
sudo systemctl enable image-similarity-service.service

# 启动服务
sudo systemctl start image-similarity-service.service

# 查看服务状态
sudo systemctl status image-similarity-service.service
```

## 4. 服务管理

### 使用server.sh脚本管理

```bash
# 查看服务状态
./server.sh status

# 重启服务
./server.sh restart

# 停止服务
./server.sh stop

# 查看日志
./server.sh logs
```

### 使用systemctl管理（如果部署为系统服务）

```bash
# 查看服务状态
sudo systemctl status image-similarity-service.service

# 重启服务
sudo systemctl restart image-similarity-service.service

# 停止服务
sudo systemctl stop image-similarity-service.service

# 查看日志
sudo journalctl -u image-similarity-service.service -f
```

## 5. 防火墙配置

如果服务需要从外部访问，请配置防火墙开放相应端口（默认为5000）：

```bash
# Ubuntu/Debian (使用ufw)
sudo ufw allow 5000/tcp

# CentOS/RHEL (使用firewalld)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## 6. 性能优化

### 调整服务参数

编辑`config.py`文件可以调整服务参数：

```bash
# 编辑配置文件
nano config.py

# 调整配置参数
```

### 日志管理

脚本会自动进行日志轮转，但您也可以设置日志保留策略：

```bash
# 编辑server.sh文件，调整日志轮转参数
MAX_LOG_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5    # 保留5个备份文件
```

## 7. 监控和维护

### 定期检查服务状态

```bash
# 简单检查服务是否运行
if ./server.sh status; then
    echo "服务正常运行"
else
    echo "服务异常，正在重启..."
    ./server.sh restart
fi
```

您可以将此命令添加到crontab中定期执行：

```bash
# 编辑crontab
crontab -e

# 添加以下行，每5分钟检查一次
*/5 * * * * /opt/imagesimi/server.sh status || /opt/imagesimi/server.sh restart
```

### 常见问题排查

1. **服务无法启动**
   - 检查端口是否被占用：`lsof -i :5000`
   - 查看日志文件：`./server.sh logs`

2. **内存占用过高**
   - 调整CLIP模型参数
   - 增加服务器内存

3. **响应缓慢**
   - 考虑使用CUDA加速（如果有GPU）
   - 优化并发请求处理

## 8. 升级服务

当需要升级服务时：

```bash
# 停止服务
./server.sh stop

# 备份旧文件
cp -r /opt/imagesimi /opt/imagesimi_backup_$(date +%Y%m%d)

# 复制新文件到项目目录

# 安装新依赖（如果有）
source venv/bin/activate
pip install -r requirements.txt

# 启动服务
./server.sh start
```

## 9. 安全注意事项

- 定期更新依赖包：`pip install --upgrade -r requirements.txt`
- 设置适当的文件权限：`chmod -R 755 /opt/imagesimi`
- 考虑配置HTTPS（可使用Nginx或Apache作为反向代理）
- 限制API访问来源（可使用防火墙或反向代理配置）

---

本文档提供了基本的部署指南，实际部署时请根据您的系统环境和需求进行调整。如有问题，请参考脚本输出的日志信息进行排查。
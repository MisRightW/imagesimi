#!/bin/bash

# 图像相似度中间件服务 - Linux生产环境运行脚本

# 设置环境变量
APP_NAME="image-similarity-service"
APP_SCRIPT="app.py"
LOG_DIR="./logs"
LOG_FILE="${LOG_DIR}/${APP_NAME}.log"
PID_FILE="${LOG_DIR}/${APP_NAME}.pid"
MAX_LOG_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# 检测虚拟环境 (Linux)
VENV_DIR="./venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

# 使用虚拟环境中的Python或系统Python
PYTHON="python3"  # Linux上优先使用python3
if [ -f "${VENV_PYTHON}" ]; then
    PYTHON="${VENV_PYTHON}"
    echo "[INFO] 检测到虚拟环境: ${VENV_DIR}"
fi

# 检查系统环境
check_environment() {
    echo "[INFO] 检查系统环境..."
    # 检查Python版本
    PYTHON_VERSION=$(${PYTHON} --version 2>&1)
    echo "[INFO] Python版本: ${PYTHON_VERSION}"
    
    # 检查端口是否被占用
    local port=5000  # 默认端口
    if lsof -Pi :${port} -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "[WARNING] 端口 ${port} 已被占用，请检查是否有其他服务在运行"
    fi
}

# 日志轮转功能
rotate_logs() {
    if [ -f "${LOG_FILE}" ] && [ $(stat -c%s "${LOG_FILE}") -ge ${MAX_LOG_SIZE} ]; then
        echo "[INFO] 执行日志轮转..."
        # 创建带时间戳的备份文件
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        cp "${LOG_FILE}" "${LOG_FILE}.${timestamp}"
        # 清空当前日志文件
        echo "日志轮转于 $(date)" > "${LOG_FILE}"
        # 删除过多的备份文件
        ls -1tr "${LOG_FILE}".* 2>/dev/null | head -n -${LOG_BACKUP_COUNT} | xargs -r rm
    fi
}

# 确保日志目录存在
if [ ! -d "${LOG_DIR}" ]; then
    mkdir -p "${LOG_DIR}"
    echo "[INFO] 创建日志目录: ${LOG_DIR}"
fi

# 设置文件权限
chmod 755 "${LOG_DIR}"

# 启动服务
start() {
    echo "[INFO] 正在启动 ${APP_NAME} 服务..."
    
    # 检查服务是否已运行
    if [ -f "${PID_FILE}" ] && ps -p $(cat "${PID_FILE}") > /dev/null 2>&1; then
        echo "[INFO] 服务已经在运行 (PID: $(cat "${PID_FILE}"))"
        return 1
    fi
    
    # 检查环境
    check_environment
    
    # 执行日志轮转
    rotate_logs
    
    # 设置环境变量 - 生产模式
    export FLASK_ENV=production
    export FLASK_APP=${APP_SCRIPT}
    export PYTHONUNBUFFERED=1  # 禁用输出缓冲
    
    # 以后台方式启动服务，并将输出重定向到日志文件
    nohup ${PYTHON} ${APP_SCRIPT} > "${LOG_FILE}" 2>&1 &
    
    # 保存进程ID到PID文件
    echo $! > "${PID_FILE}"
    
    # 设置PID文件权限
    chmod 644 "${PID_FILE}"
    
    # 检查服务是否成功启动
    sleep 2
    if ps -p $(cat "${PID_FILE}") > /dev/null 2>&1; then
        echo "[SUCCESS] 服务已成功启动!"
        echo "[INFO] PID: $(cat "${PID_FILE}")"
        echo "[INFO] 日志: ${LOG_FILE}"
        return 0
    else
        echo "[ERROR] 服务启动失败，请检查日志: ${LOG_FILE}"
        rm -f "${PID_FILE}"
        return 1
    fi
}

# 停止服务
stop() {
    echo "正在停止 ${APP_NAME} 服务..."
    
    if [ ! -f "${PID_FILE}" ]; then
        echo "服务未运行 (没有找到PID文件)"
        return 1
    fi
    
    PID=$(cat "${PID_FILE}")
    
    # 检查进程是否存在
    if ps -p ${PID} > /dev/null 2>&1; then
        # 先尝试优雅关闭（发送SIGTERM信号）
        kill ${PID}
        
        # 等待进程结束，最多等待10秒
        COUNTER=0
        while ps -p ${PID} > /dev/null 2>&1 && [ ${COUNTER} -lt 10 ]; do
            echo "等待服务关闭... (${COUNTER}/10)"
            sleep 1
            COUNTER=$((COUNTER+1))
        done
        
        # 如果进程仍在运行，强制终止
        if ps -p ${PID} > /dev/null 2>&1; then
            echo "强制终止服务进程..."
            kill -9 ${PID}
        fi
        
        # 移除PID文件
        rm -f "${PID_FILE}"
        echo "服务已停止"
        return 0
    else
        echo "服务未运行，但PID文件存在 (可能是异常退出)"
        rm -f "${PID_FILE}"
        return 1
    fi
}

# 查看服务状态
status() {
    if [ ! -f "${PID_FILE}" ]; then
        echo "服务未运行"
        return 1
    fi
    
    PID=$(cat "${PID_FILE}")
    
    if ps -p ${PID} > /dev/null 2>&1; then
        echo "服务正在运行"
        echo "PID: ${PID}"
        echo "日志: ${LOG_FILE}"
        return 0
    else
        echo "服务未运行，但PID文件存在 (可能是异常退出)"
        return 1
    fi
}

# 查看日志
tail_logs() {
    if [ ! -f "${LOG_FILE}" ]; then
        echo "日志文件不存在: ${LOG_FILE}"
        return 1
    fi
    
    echo "查看日志文件: ${LOG_FILE}"
    tail -f "${LOG_FILE}"
}

# 重启服务
restart() {
    stop
    start
}

# 显示帮助信息
show_help() {
    echo "============================================="
    echo "  图像相似度中间件服务 - Linux生产环境脚本  "
    echo "============================================="
    echo "使用方法: $0 {start|stop|status|restart|logs|sysd}"
    echo "  start   - 启动服务"
    echo "  stop    - 停止服务"
    echo "  status  - 查看服务状态"
    echo "  restart - 重启服务"
    echo "  logs    - 查看日志"
    echo "  sysd    - 生成systemd服务配置"
    echo "  help    - 显示帮助信息"
    echo ""
    echo "注意: 脚本会自动检测并使用./venv虚拟环境"
    echo "============================================="
}

# 生成systemd服务配置
generate_systemd() {
    echo "[INFO] 生成systemd服务配置..."
    
    local service_file="${APP_NAME}.service"
    local current_dir=$(pwd)
    local service_content=""
    
    service_content="[Unit]
Description=Image Similarity Middleware Service
After=network.target

[Service]
Type=simple
WorkingDirectory=${current_dir}
ExecStart=${current_dir}/${PYTHON} ${current_dir}/${APP_SCRIPT}
Environment=\"FLASK_ENV=production\"
Environment=\"FLASK_APP=${APP_SCRIPT}\"
Environment=\"PYTHONUNBUFFERED=1\"
Restart=on-failure
RestartSec=5s
User=$(whoami)

[Install]
WantedBy=multi-user.target"
    
    echo "${service_content}" > "${service_file}"
    echo "[SUCCESS] systemd服务配置已生成: ${service_file}"
    echo "[INFO] 要安装为系统服务，请执行:"
    echo "  sudo cp ${service_file} /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable ${APP_NAME}.service"
    echo "  sudo systemctl start ${APP_NAME}.service"
    return 0
}

# 根据命令行参数执行相应的功能
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        restart
        ;;
    logs)
        tail_logs
        ;;
    sysd)
        generate_systemd
        ;;
    help)
        show_help
        ;;
    *)
        echo "[ERROR] 未知命令: $1"
        show_help
        exit 1
        ;;
esac

exit $?
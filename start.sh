#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务配置
BACKEND_PORT=5001
FRONTEND_PORT=3001
BACKEND_URL="http://localhost:$BACKEND_PORT"
FRONTEND_URL="http://localhost:$FRONTEND_PORT"
BACKEND_PID=""
FRONTEND_PID=""
BACKEND_PID_FILE="/tmp/backend.pid"
FRONTEND_PID_FILE="/tmp/frontend.pid"

echo -e "${BLUE}🚀 启动系统资源监控项目...${NC}"

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}⚠️  正在停止所有服务...${NC}"
    
    # 停止后端服务
    if [ ! -z "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}🛑 停止后端服务 (PID: $BACKEND_PID)${NC}"
        kill "$BACKEND_PID" 2>/dev/null
        sleep 2
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            kill -9 "$BACKEND_PID" 2>/dev/null
        fi
    fi
    
    # 停止前端服务
    if [ ! -z "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}🛑 停止前端服务 (PID: $FRONTEND_PID)${NC}"
        kill "$FRONTEND_PID" 2>/dev/null
        sleep 2
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill -9 "$FRONTEND_PID" 2>/dev/null
        fi
    fi
    
    # 清理PID文件
    rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
    
    # 强制清理端口
    BACKEND_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo -e "${YELLOW}🧹 清理后端端口 $BACKEND_PORT${NC}"
        echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
    fi
    
    FRONTEND_PIDS=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo -e "${YELLOW}🧹 清理前端端口 $FRONTEND_PORT${NC}"
        echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ 端口 $port 已被占用，无法启动 $service_name${NC}"
        echo -e "${YELLOW}📋 占用端口 $port 的进程信息：${NC}"
        lsof -Pi :$port -sTCP:LISTEN
        echo -e "${RED}💡 请手动释放端口后重新运行${NC}"
        return 1
    else
        echo -e "${GREEN}✅ 端口 $port 可用${NC}"
        return 0
    fi
}

# 健康检查函数
health_check() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}🔍 等待 $service_name 启动...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name 启动成功！${NC}"
            return 0
        fi
        
        echo -ne "${YELLOW}⏳ 尝试 $attempt/$max_attempts...\r${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "\n${RED}❌ $service_name 启动失败或超时${NC}"
    return 1
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}📋 检查依赖...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装${NC}"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装${NC}"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未安装${NC}"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ curl 未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 启动后端服务
start_backend() {
    echo -e "\n${BLUE}🔧 启动后端服务...${NC}"
    
    # 检查端口
    if ! check_port $BACKEND_PORT "后端服务"; then
        echo -e "${RED}❌ 后端服务启动失败：端口被占用${NC}"
        return 1
    fi
    
    # 检查目录
    if [ ! -d "backend" ]; then
        echo -e "${RED}❌ backend 目录不存在${NC}"
        return 1
    fi
    
    cd backend
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}📦 创建Python虚拟环境...${NC}"
        if ! python3 -m venv venv; then
            echo -e "${RED}❌ 虚拟环境创建失败${NC}"
            cd ..
            return 1
        fi
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    if ! pip install -r requirements.txt >/dev/null 2>&1; then
        echo -e "${RED}❌ 后端依赖安装失败${NC}"
        cd ..
        return 1
    fi
    
    # 启动后端（后台运行）
    echo -e "${BLUE}🚀 启动Flask服务器...${NC}"
    python app.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    
    cd ..
    
    # 检查后端是否成功启动
    if ! health_check "$BACKEND_URL/api/health" "后端服务"; then
        echo -e "${RED}❌ 后端服务启动失败${NC}"
        return 1
    fi
    
    echo -e "${GREEN}📍 后端地址: $BACKEND_URL${NC}"
    return 0
}

# 启动前端服务
start_frontend() {
    echo -e "\n${BLUE}🎨 启动前端服务...${NC}"
    
    # 检查端口
    if ! check_port $FRONTEND_PORT "前端服务"; then
        echo -e "${RED}❌ 前端服务启动失败：端口被占用${NC}"
        return 1
    fi
    
    # 检查目录
    if [ ! -d "frontend" ]; then
        echo -e "${RED}❌ frontend 目录不存在${NC}"
        return 1
    fi
    
    cd frontend
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦 安装前端依赖...${NC}"
        if ! npm install; then
            echo -e "${RED}❌ 前端依赖安装失败${NC}"
            cd ..
            return 1
        fi
    fi
    
    # 启动前端（后台运行）
    echo -e "${BLUE}🚀 启动Vue开发服务器...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
    
    cd ..
    
    # 检查前端是否成功启动
    if ! health_check "$FRONTEND_URL" "前端服务"; then
        echo -e "${RED}❌ 前端服务启动失败${NC}"
        return 1
    fi
    
    echo -e "${GREEN}📍 前端地址: $FRONTEND_URL${NC}"
    return 0
}

# 主执行流程
check_dependencies

# 启动后端服务
if ! start_backend; then
    echo -e "${RED}❌ 后端服务启动失败，终止启动流程${NC}"
    cleanup
    exit 1
fi

# 启动前端服务
if ! start_frontend; then
    echo -e "${RED}❌ 前端服务启动失败，终止启动流程${NC}"
    cleanup
    exit 1
fi

# 显示启动完成信息
echo -e "\n${GREEN}🎉 项目启动完成！${NC}"
echo -e "${GREEN}📱 前端地址: $FRONTEND_URL${NC}"
echo -e "${GREEN}🔧 后端API: $BACKEND_URL${NC}"
echo -e "${YELLOW}👤 默认账户:${NC}"
echo -e "${YELLOW}   管理员: admin / admin123${NC}"
echo -e "${YELLOW}   用户: user / user123${NC}"
echo -e "\n${YELLOW}💡 按 Ctrl+C 停止所有服务${NC}"

# 保持脚本运行，定期检查服务状态
while true; do
    # 检查后端服务状态
    if ! curl -s "$BACKEND_URL/api/health" >/dev/null 2>&1; then
        echo -e "\n${RED}❌ 后端服务异常，停止所有服务${NC}"
        cleanup
        exit 1
    fi
    
    # 检查前端服务状态
    if ! curl -s "$FRONTEND_URL" >/dev/null 2>&1; then
        echo -e "\n${RED}❌ 前端服务异常，停止所有服务${NC}"
        cleanup
        exit 1
    fi
    
    sleep 10
done
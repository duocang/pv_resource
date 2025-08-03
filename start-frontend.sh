#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 前端配置
FRONTEND_PORT=3001
FRONTEND_URL="http://localhost:$FRONTEND_PORT"
FRONTEND_PID_FILE="/tmp/frontend.pid"

echo -e "${BLUE}🎨 启动前端服务...${NC}"

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}⚠️  正在清理前端服务...${NC}"
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo -e "${YELLOW}🛑 停止前端服务 (PID: $FRONTEND_PID)${NC}"
            kill "$FRONTEND_PID" 2>/dev/null
            sleep 2
            if kill -0 "$FRONTEND_PID" 2>/dev/null; then
                echo -e "${RED}⚠️  强制停止前端服务${NC}"
                kill -9 "$FRONTEND_PID" 2>/dev/null
            fi
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # 清理可能占用端口的进程
    FRONTEND_PIDS=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo -e "${YELLOW}🧹 清理端口 $FRONTEND_PORT 上的进程${NC}"
        echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ 清理完成${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ 端口 $port 已被占用${NC}"
        echo -e "${YELLOW}📋 占用端口 $port 的进程信息：${NC}"
        lsof -Pi :$port -sTCP:LISTEN
        echo -e "${RED}💡 请手动释放端口 $port 后重新运行脚本${NC}"
        echo -e "${YELLOW}提示：可以使用以下命令查看和处理：${NC}"
        echo -e "${YELLOW}  查看进程: lsof -Pi :$port${NC}"
        echo -e "${YELLOW}  停止进程: kill <PID>${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ 端口 $port 可用${NC}"
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
            echo -e "${GREEN}🌐 访问地址: $url${NC}"
            return 0
        fi
        
        echo -ne "${YELLOW}⏳ 尝试 $attempt/$max_attempts...\r${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "\n${RED}❌ $service_name 启动失败或超时${NC}"
    return 1
}

# 进入前端目录
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ frontend 目录不存在${NC}"
    exit 1
fi

cd frontend

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装，请先安装Node.js${NC}"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm 未安装，请先安装npm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js 和 npm 已安装${NC}"

# 检查端口
check_port $FRONTEND_PORT "前端服务"

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 安装前端依赖...${NC}"
    if ! npm install; then
        echo -e "${RED}❌ 依赖安装失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖已存在，跳过安装${NC}"
fi

# 启动前端开发服务器
echo -e "${BLUE}🚀 启动Vue开发服务器...${NC}"
echo -e "${BLUE}📍 前端地址: $FRONTEND_URL${NC}"
echo -e "${YELLOW}💡 按 Ctrl+C 停止服务${NC}"
echo ""

# 后台启动前端服务并获取PID
npm run dev &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

echo -e "${GREEN}🎯 前端服务已启动 (PID: $FRONTEND_PID)${NC}"

# 健康检查
if health_check "$FRONTEND_URL" "前端服务"; then
    echo -e "${GREEN}🎉 前端服务启动完成！${NC}"
    echo -e "${GREEN}🌐 访问地址: $FRONTEND_URL${NC}"
    echo -e "${YELLOW}💡 按 Ctrl+C 停止服务${NC}"
    echo ""
    
    # 等待前端进程
    wait $FRONTEND_PID
else
    echo -e "${RED}❌ 前端服务启动失败${NC}"
    cleanup
    exit 1
fi
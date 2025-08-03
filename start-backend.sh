#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 后端配置
BACKEND_PORT=5001
BACKEND_URL="http://localhost:$BACKEND_PORT"
BACKEND_PID_FILE="/tmp/backend.pid"

echo -e "${BLUE}🔧 启动后端服务...${NC}"

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}⚠️  正在清理后端服务...${NC}"
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "${YELLOW}🛑 停止后端服务 (PID: $BACKEND_PID)${NC}"
            kill "$BACKEND_PID" 2>/dev/null
            sleep 2
            if kill -0 "$BACKEND_PID" 2>/dev/null; then
                echo -e "${RED}⚠️  强制停止后端服务${NC}"
                kill -9 "$BACKEND_PID" 2>/dev/null
            fi
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # 清理可能占用端口的进程
    BACKEND_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo -e "${YELLOW}🧹 清理端口 $BACKEND_PORT 上的进程${NC}"
        echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
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
    local max_attempts=15
    local attempt=1
    
    echo -e "${BLUE}🔍 等待 $service_name 启动...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url/api/health" >/dev/null 2>&1; then
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

# 进入后端目录
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ backend 目录不存在${NC}"
    exit 1
fi

cd backend

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装，请先安装Python3${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python3 已安装${NC}"

# 检查端口
check_port $BACKEND_PORT "后端服务"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 创建Python虚拟环境...${NC}"
    if ! python3 -m venv venv; then
        echo -e "${RED}❌ 虚拟环境创建失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 虚拟环境创建完成${NC}"
else
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}🔄 激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
echo -e "${BLUE}📦 安装Python依赖...${NC}"
if ! pip install -r requirements.txt >/dev/null 2>&1; then
    echo -e "${RED}❌ 依赖安装失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 启动后端服务
echo -e "${BLUE}🚀 启动Flask服务器...${NC}"
echo -e "${BLUE}📍 后端地址: $BACKEND_URL${NC}"
echo -e "${BLUE}🔍 API文档: $BACKEND_URL/api/health${NC}"
echo -e "${YELLOW}💡 按 Ctrl+C 停止服务${NC}"
echo ""

# 后台启动后端服务并获取PID
python app.py &
BACKEND_PID=$!
echo $BACKEND_PID > "$BACKEND_PID_FILE"

echo -e "${GREEN}🎯 后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 健康检查
if health_check "$BACKEND_URL" "后端服务"; then
    echo -e "${GREEN}🎉 后端服务启动完成！${NC}"
    echo -e "${GREEN}🌐 访问地址: $BACKEND_URL${NC}"
    echo -e "${YELLOW}💡 按 Ctrl+C 停止服务${NC}"
    echo ""
    
    # 等待后端进程
    wait $BACKEND_PID
else
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    cleanup
    exit 1
fi
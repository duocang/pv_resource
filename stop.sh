#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🛑 停止系统资源监控项目服务...${NC}"

# 项目配置
BACKEND_PORT=5001
FRONTEND_PORT=3001
PROJECT_DIR="/mnt/primary/pv_resource"

# 基于端口清理后端服务
echo -e "${BLUE}🔍 检查后端端口 $BACKEND_PORT...${NC}"
BACKEND_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo -e "${YELLOW}📋 后端端口 $BACKEND_PORT 占用进程：${NC}"
    lsof -i:$BACKEND_PORT
    echo -e "${YELLOW}🧹 清理后端端口 $BACKEND_PORT${NC}"
    echo "$BACKEND_PIDS" | xargs kill -TERM 2>/dev/null
    sleep 2
    # 如果进程还在，强制杀掉
    REMAINING_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
    if [ ! -z "$REMAINING_PIDS" ]; then
        echo -e "${RED}⚠️  强制终止残留进程${NC}"
        echo "$REMAINING_PIDS" | xargs kill -9 2>/dev/null
    fi
    echo -e "${GREEN}✅ 后端服务已停止${NC}"
else
    echo -e "${BLUE}ℹ️  后端端口 $BACKEND_PORT 未被占用${NC}"
fi

# 基于端口清理前端服务
echo -e "${BLUE}🔍 检查前端端口 $FRONTEND_PORT...${NC}"
FRONTEND_PIDS=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo -e "${YELLOW}📋 前端端口 $FRONTEND_PORT 占用进程：${NC}"
    lsof -i:$FRONTEND_PORT
    echo -e "${YELLOW}🧹 清理前端端口 $FRONTEND_PORT${NC}"
    echo "$FRONTEND_PIDS" | xargs kill -TERM 2>/dev/null
    sleep 2
    # 如果进程还在，强制杀掉
    REMAINING_PIDS=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
    if [ ! -z "$REMAINING_PIDS" ]; then
        echo -e "${RED}⚠️  强制终止残留进程${NC}"
        echo "$REMAINING_PIDS" | xargs kill -9 2>/dev/null
    fi
    echo -e "${GREEN}✅ 前端服务已停止${NC}"
else
    echo -e "${BLUE}ℹ️  前端端口 $FRONTEND_PORT 未被占用${NC}"
fi

# 清理PID文件
echo -e "${BLUE}🧹 清理PID文件...${NC}"
rm -f /tmp/backend.pid /tmp/frontend.pid

echo -e "${GREEN}🎉 所有服务已停止${NC}"
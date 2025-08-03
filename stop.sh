#!/bin/bash

echo "🛑 停止系统资源监控项目服务..."

# 查找并停止Flask进程
FLASK_PID=$(ps aux | grep "python app.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$FLASK_PID" ]; then
    kill $FLASK_PID
    echo "✅ 后端服务已停止 (PID: $FLASK_PID)"
else
    echo "ℹ️  未找到运行中的后端服务"
fi

# 查找并停止Vue开发服务器进程
VUE_PID=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
if [ ! -z "$VUE_PID" ]; then
    kill $VUE_PID
    echo "✅ 前端服务已停止 (PID: $VUE_PID)"
else
    echo "ℹ️  未找到运行中的前端服务"
fi

# 停止可能的Node.js进程
NODE_PID=$(ps aux | grep "node.*vite" | grep -v grep | awk '{print $2}')
if [ ! -z "$NODE_PID" ]; then
    kill $NODE_PID
    echo "✅ Node.js服务已停止 (PID: $NODE_PID)"
fi

echo "🎉 所有服务已停止"
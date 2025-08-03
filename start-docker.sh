#!/bin/bash

echo "🐳 使用Docker启动系统资源监控项目..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装Docker Compose"
    exit 1
fi

# 构建并启动容器
echo "🔨 构建并启动Docker容器..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查容器状态
echo "📋 检查容器状态..."
docker-compose ps

echo ""
echo "🎉 Docker部署完成！"
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:5000"
echo "👤 默认账户:"
echo "   管理员: admin / admin123"
echo "   用户: user / user123"
echo ""
echo "💡 管理命令:"
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
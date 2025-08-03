

pv_resource/
├── frontend/                 # Vue3 前端
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
├── backend/                  # Flask 后端
│   ├── app.py
│   ├── auth.py
│   ├── system_monitor.py
│   └── requirements.txt
├── docker-compose.yml        # Docker 部署配置
└── README.md
# 系统资源监控网站

一个基于Vue3和Flask的实时系统资源监控网站，可以监控CPU、内存、磁盘和网络使用情况。

## 功能特性

- 🔐 用户登录认证
- 📊 实时系统资源监控
- 📈 可视化图表展示
- 🔄 自动数据更新
- 📱 响应式设计
- 🐳 Docker容器化部署

## 技术栈

### 前端
- Vue 3
- Element Plus
- ECharts
- Vue Router
- Pinia
- Axios

### 后端
- Python Flask
- psutil (系统信息获取)
- Flask-JWT-Extended (JWT认证)
- Flask-CORS (跨域支持)

## 快速开始

### 方式一：Docker部署（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd pv_resource
```

2. 使用Docker Compose启动
```bash
docker-compose up -d
```

3. 访问应用
- 前端：http://localhost:3001
- 后端API：http://localhost:5001

### 方式二：本地开发

#### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动后端服务
```bash
python app.py
```

#### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

## 默认账户

- 管理员：admin / admin123
- 普通用户：user / user123

## API接口

### 认证接口
- `POST /api/login` - 用户登录
- `GET /api/health` - 健康检查

### 系统监控接口
- `GET /api/system-status` - 获取当前系统状态
- `GET /api/system-history` - 获取历史数据

## 监控指标

- **CPU**: 使用率、核心数、频率
- **内存**: 总量、已用、可用、使用率、交换分区
- **磁盘**: 总量、已用、可用、使用率、读写速度
- **网络**: 发送/接收字节数、数据包数
- **系统**: 负载平均值、启动时间

## 配置说明

### 后端配置
- JWT密钥：修改 `app.py` 中的 `JWT_SECRET_KEY`
- 监控间隔：修改 `system_monitor.py` 中的采集间隔
- 用户账户：修改 `auth.py` 中的用户信息

### 前端配置
- API地址：修改 `vite.config.js` 中的代理配置
- 更新间隔：修改 `Dashboard.vue` 中的定时器间隔

## 部署注意事项

1. **权限要求**：监控系统资源需要适当的权限，Docker部署时使用了 `privileged: true`
2. **安全性**：生产环境请修改默认密码和JWT密钥
3. **性能**：可根据需要调整数据采集和更新频率
4. **存储**：当前版本数据存储在内存中，重启后历史数据会丢失

## 扩展功能

- [ ] 数据持久化存储
- [ ] 告警功能
- [ ] 多服务器监控
- [ ] 更多系统指标
- [ ] 用户权限管理
- [ ] 数据导出功能

## 许可证

MIT License
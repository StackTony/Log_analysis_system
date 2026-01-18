# 日志自动分析系统

## 项目概述

日志自动分析系统是一个基于Python和Vue.js的前后端一体化应用，旨在实现多用户同时访问，自动分析特定命令收集的日志，比对配置的检查项，生成分析报告，并管理案例库。系统具备智能案例合并与检查项自动更新能力，支持日志数据的灵活拓展。

## 核心功能

### 用户管理
- 多用户支持，基于角色的权限控制（管理员/普通用户）
- JWT认证机制，确保系统安全

### 日志收集
- 支持通过命令收集日志（如grep、tail等）
- 支持上传日志文件
- 支持通过API接口接收日志数据

### 日志分析
- 自动比对日志与已配置的检查项
- 支持正则表达式和关键词匹配规则
- 异步分析，提高系统性能

### 案例库管理
- 自动案例合并与新增
- 支持案例查询、更新、删除和合并
- 智能识别新的检查项并自动收录

### 分析报告
- 生成详细的分析报告
- 支持报告导出功能（PDF/Excel）

## 技术栈

### 后端
- Python 3.8+
- Flask：Web框架
- Flask-JWT-Extended：JWT认证
- SQLAlchemy：ORM框架
- PyMongo：MongoDB操作
- Celery：异步任务处理
- Redis：消息代理

### 前端
- Vue.js 3：前端框架
- Element Plus：UI组件库
- Vuex 4：状态管理
- Vue Router：路由管理
- Axios：HTTP客户端

### 数据库
- MySQL 8.0：存储结构化数据
- MongoDB 5.0：存储日志数据

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+
- MySQL 8.0+
- MongoDB 5.0+
- Redis 6.0+

### 后端部署

1. 进入后端目录
   ```bash
   cd log_analysis_backend
   ```

2. 创建虚拟环境
   ```bash
   python -m venv venv
   ```

3. 激活虚拟环境
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux
   source venv/bin/activate
   ```

4. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

5. 配置环境变量
   ```bash
   # 创建.env文件并配置数据库连接、JWT密钥等
   ```

6. 初始化数据库
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

7. 启动Redis服务

8. 启动Celery worker
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

9. 启动Flask应用
   ```bash
   flask run
   ```

### 前端部署

1. 进入前端目录
   ```bash
   cd log_analysis_frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 启动开发服务器
   ```bash
   npm run serve
   ```

4. 访问应用
   ```bash
   http://localhost:8080
   ```

## 项目结构

### 后端结构
```
log_analysis_backend/
├── app/                 # 应用核心代码
│   ├── models/          # 数据模型
│   ├── api/             # API路由
│   ├── services/        # 业务逻辑
│   ├── utils/           # 工具函数
│   └── tasks/           # Celery任务
├── migrations/          # 数据库迁移文件
├── tests/               # 测试文件
├── run.py               # 应用入口
└── requirements.txt     # 依赖包列表
```

### 前端结构
```
log_analysis_frontend/
├── src/                 # 源代码
│   ├── components/      # 通用组件
│   ├── views/           # 页面组件
│   ├── router/          # 路由配置
│   ├── store/           # 状态管理
│   └── api/             # API请求
├── public/              # 静态资源
└── package.json         # 项目配置
```

## 详细文档

- [需求分析文档](./requirements_analysis.md)
- [技术实现方案](./tech_implementation.md)

## 开发计划

详见技术实现方案中的项目开发计划部分。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request。

## 联系方式

如有问题，请联系项目维护者。
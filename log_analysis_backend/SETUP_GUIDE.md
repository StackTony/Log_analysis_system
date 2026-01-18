# 日志分析系统后端环境配置指南

## 1. 环境准备

### 1.1 安装Python

确保您的系统已安装Python 3.8或更高版本。您可以从[Python官方网站](https://www.python.org/downloads/)下载并安装Python。

安装完成后，验证Python版本：

```bash
python --version  # 或 python3 --version
pip --version    # 或 pip3 --version
```

### 1.2 安装数据库

#### MySQL

安装MySQL数据库，并确保服务已启动。您可以从[MySQL官方网站](https://dev.mysql.com/downloads/)下载并安装。

创建数据库：

```sql
CREATE DATABASE log_analysis;
```

#### MongoDB

安装MongoDB数据库，并确保服务已启动。您可以从[MongoDB官方网站](https://www.mongodb.com/try/download/community)下载并安装。

#### Redis

安装Redis数据库，并确保服务已启动。您可以从[Redis官方网站](https://redis.io/download)下载并安装。

## 2. 项目配置

### 2.1 安装依赖

在项目根目录下执行以下命令安装Python依赖：

```bash
cd log_analysis_backend
pip install -r requirements.txt  # 或 pip3 install -r requirements.txt
```

### 2.2 配置环境变量

编辑项目根目录下的`.env`文件，配置数据库连接信息和其他必要参数：

```env
# Flask配置
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/log_analysis

# MongoDB配置
MONGODB_URI=mongodb://localhost:27017/log_analysis

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-here

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 服务配置
HOST=0.0.0.0
PORT=5000

# DeepSeek API配置（用于AI分析）
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

请将上述配置中的占位符（如`your-secret-key-here`）替换为实际的值。

## 3. 数据库初始化

### 3.1 初始化MySQL数据库

执行数据库迁移命令：

```bash
# 初始化迁移仓库（首次执行）
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade
```

### 3.2 初始化MongoDB集合

MongoDB会在首次使用时自动创建集合，无需手动初始化。

## 4. 服务启动

### 4.1 启动后端服务

在项目根目录下执行以下命令启动Flask应用：

```bash
python run.py  # 或 python3 run.py
```

服务将在`http://localhost:5000`上运行。

### 4.2 启动Celery worker

在另一个终端窗口中执行以下命令启动Celery worker：

```bash
celery -A app.tasks.celery worker --loglevel=info
```

### 4.3 启动前端服务

在项目根目录下执行以下命令启动前端开发服务器：

```bash
cd log_analysis_frontend
npm run dev
```

前端服务将在`http://localhost:5173`上运行。

## 5. 使用说明

### 5.1 API文档

后端API接口采用RESTful风格，主要接口如下：

#### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新Token
- `POST /api/auth/logout` - 用户登出

#### 日志接口
- `POST /api/logs/collect` - 收集日志（命令执行）
- `POST /api/logs/upload` - 上传日志文件
- `POST /api/logs/receive` - 接收日志数据
- `GET /api/logs` - 获取日志列表
- `GET /api/logs/<log_id>` - 获取日志详情

#### 分析接口
- `POST /api/analysis/start` - 开始分析日志
- `GET /api/analysis/<analysis_id>` - 获取分析结果
- `GET /api/analysis/report/<report_id>` - 获取分析报告
- `POST /api/analysis/report/export` - 导出分析报告

### 5.2 AI分析功能

系统集成了DeepSeek API，提供以下AI分析功能：

- 日志分析：识别异常模式和潜在问题
- 日志摘要：提取关键信息
- 异常检测：检测日志中的异常模式
- 自然语言查询：使用自然语言查询日志内容

要使用AI分析功能，需要在`.env`文件中配置有效的DeepSeek API密钥。

## 6. 故障排除

### 6.1 数据库连接问题

- 确保MySQL、MongoDB和Redis服务已启动
- 检查`.env`文件中的数据库连接配置是否正确
- 确保数据库用户有足够的权限

### 6.2 依赖安装问题

- 确保使用的是Python 3.8或更高版本
- 尝试使用`--user`参数安装依赖：`pip install --user -r requirements.txt`
- 对于Linux系统，可能需要安装额外的系统依赖：
  ```bash
  sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
  ```

### 6.3 服务启动问题

- 检查端口是否被占用
- 确保所有环境变量都已正确配置
- 查看日志输出以获取详细错误信息

## 7. 性能优化

为确保系统能够支持30人同时访问且时延小于10s，建议：

- 使用生产环境部署（`FLASK_CONFIG=production`）
- 配置适当的数据库连接池
- 使用Gunicorn或uWSGI作为WSGI服务器
- 启用缓存机制
- 对大日志文件进行分片处理

## 8. 安全建议

- 生产环境中使用HTTPS
- 定期更新依赖库
- 实施访问控制和权限管理
- 对敏感数据进行加密存储
- 定期备份数据库

---

如果您在配置过程中遇到任何问题，请参考上述故障排除部分或联系系统管理员。
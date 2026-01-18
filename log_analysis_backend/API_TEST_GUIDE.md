# API测试指南

## 1. 测试环境准备

在测试API之前，请确保：

1. 后端服务已成功启动（默认端口：5000）
2. 前端服务已成功启动（默认端口：5173/5174）
3. 数据库已正确初始化

## 2. 认证接口测试

### 2.1 用户注册

**请求方式**: POST
**URL**: `http://localhost:5000/api/auth/register`
**请求体**:
```json
{
  "username": "testuser",
  "password": "password123",
  "email": "test@example.com",
  "role": "user"
}
```

**成功响应**:
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "created_at": "2023-04-15T08:30:00Z",
    "updated_at": "2023-04-15T08:30:00Z"
  }
}
```

### 2.2 用户登录

**请求方式**: POST
**URL**: `http://localhost:5000/api/auth/login`
**请求体**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**成功响应**:
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

### 2.3 刷新Token

**请求方式**: POST
**URL**: `http://localhost:5000/api/auth/refresh`
**请求头**:
```
Authorization: Bearer {refresh_token}
```

**成功响应**:
```json
{
  "message": "Token refreshed successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2.4 用户登出

**请求方式**: POST
**URL**: `http://localhost:5000/api/auth/logout`
**请求头**:
```
Authorization: Bearer {access_token}
```

**成功响应**:
```json
{
  "message": "Logout successful"
}
```

## 3. 日志接口测试

### 3.1 收集日志（命令执行）

**请求方式**: POST
**URL**: `http://localhost:5000/api/logs/collect`
**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```
**请求体**:
```json
{
  "command": "tail -n 100 /var/log/syslog"
}
```

**成功响应**:
```json
{
  "message": "Log collected successfully",
  "log_id": "6078567890abcdef12345678",
  "log_content": "...日志内容...",
  "command": "tail -n 100 /var/log/syslog"
}
```

### 3.2 上传日志文件

**请求方式**: POST
**URL**: `http://localhost:5000/api/logs/upload`
**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```
**请求体**:
```
file: [选择日志文件]
```

**成功响应**:
```json
{
  "message": "Log uploaded successfully",
  "log_id": "6078567890abcdef12345678",
  "filename": "syslog.txt",
  "file_path": "/path/to/uploads/syslog.txt"
}
```

### 3.3 接收日志数据

**请求方式**: POST
**URL**: `http://localhost:5000/api/logs/receive`
**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```
**请求体**:
```json
{
  "log_content": "...日志内容...",
  "additional_info": {
    "source": "server1",
    "type": "error"
  }
}
```

**成功响应**:
```json
{
  "message": "Log received successfully",
  "log_id": "6078567890abcdef12345678"
}
```

### 3.4 获取日志列表

**请求方式**: GET
**URL**: `http://localhost:5000/api/logs?page=1&per_page=10`
**请求头**:
```
Authorization: Bearer {access_token}
```

**成功响应**:
```json
{
  "logs": [
    {
      "_id": "6078567890abcdef12345678",
      "content": "...日志内容...",
      "source": "command",
      "collection_time": "2023-04-15T08:30:00Z",
      "user_id": 1,
      "metadata": {
        "command": "tail -n 100 /var/log/syslog",
        "ip": "127.0.0.1",
        "timestamp": "2023-04-15T08:30:00Z"
      },
      "created_at": "2023-04-15T08:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### 3.5 获取日志详情

**请求方式**: GET
**URL**: `http://localhost:5000/api/logs/6078567890abcdef12345678`
**请求头**:
```
Authorization: Bearer {access_token}
```

**成功响应**:
```json
{
  "log": {
    "_id": "6078567890abcdef12345678",
    "content": "...日志内容...",
    "source": "command",
    "collection_time": "2023-04-15T08:30:00Z",
    "user_id": 1,
    "metadata": {
      "command": "tail -n 100 /var/log/syslog",
      "ip": "127.0.0.1",
      "timestamp": "2023-04-15T08:30:00Z"
    },
    "created_at": "2023-04-15T08:30:00Z"
  }
}
```

## 4. 分析接口测试

### 4.1 开始分析日志

**请求方式**: POST
**URL**: `http://localhost:5000/api/analysis/start`
**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```
**请求体**:
```json
{
  "log_id": "6078567890abcdef12345678"
}
```

**成功响应**:
```json
{
  "report_id": 1,
  "log_id": "6078567890abcdef12345678",
  "match_count": 2,
  "matches": [
    {
      "check_item_id": 1,
      "check_item_name": "内存不足警告",
      "check_item_severity": "high",
      "matches": ["Out of memory"]
    },
    {
      "check_item_id": 2,
      "check_item_name": "CPU使用率过高",
      "check_item_severity": "medium",
      "matches": ["CPU usage exceeds 90%"]
    }
  ],
  "ai_analysis": "...AI分析结果...",
  "ai_summary": "...日志摘要...",
  "ai_anomalies": "...异常检测结果...",
  "analysis_time": "2023-04-15T08:35:00Z"
}
```

### 4.2 获取分析结果

**请求方式**: GET
**URL**: `http://localhost:5000/api/analysis/1`
**请求头**:
```
Authorization: Bearer {access_token}
```

**成功响应**:
```json
{
  "report": {
    "id": 1,
    "user_id": 1,
    "log_id": "6078567890abcdef12345678",
    "analysis_time": "2023-04-15T08:35:00Z",
    "result_summary": "匹配到 2 个检查项\n\nAI摘要：...",
    "status": "success",
    "created_at": "2023-04-15T08:35:00Z"
  },
  "log_content": "...日志内容...",
  "cases": [
    {
      "id": 1,
      "check_item_id": 1,
      "log_id": "6078567890abcdef12345678",
      "log_content": "...日志内容...",
      "analysis_result": "匹配规则：Out of memory\n\n匹配内容：['Out of memory']\n\nAI分析：...",
      "status": "pending",
      "processed_by": 1,
      "created_at": "2023-04-15T08:35:00Z",
      "updated_at": "2023-04-15T08:35:00Z"
    }
  ]
}
```

### 4.3 获取分析报告

**请求方式**: GET
**URL**: `http://localhost:5000/api/analysis/report/1`
**请求头**:
```
Authorization: Bearer {access_token}
```

**成功响应**:
```json
{
  "report": {
    "id": 1,
    "user_id": 1,
    "log_id": "6078567890abcdef12345678",
    "analysis_time": "2023-04-15T08:35:00Z",
    "result_summary": "匹配到 2 个检查项\n\nAI摘要：...",
    "status": "success",
    "created_at": "2023-04-15T08:35:00Z"
  },
  "log_content": "...日志内容...",
  "cases": [
    {
      "id": 1,
      "check_item_id": 1,
      "log_id": "6078567890abcdef12345678",
      "log_content": "...日志内容...",
      "analysis_result": "匹配规则：Out of memory\n\n匹配内容：['Out of memory']\n\nAI分析：...",
      "status": "pending",
      "processed_by": 1,
      "created_at": "2023-04-15T08:35:00Z",
      "updated_at": "2023-04-15T08:35:00Z"
    }
  ],
  "ai_analysis": "...AI分析结果...",
  "ai_summary": "...日志摘要...",
  "ai_anomalies": "...异常检测结果..."
}
```

### 4.4 导出分析报告

**请求方式**: POST
**URL**: `http://localhost:5000/api/analysis/report/export`
**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```
**请求体**:
```json
{
  "report_id": 1,
  "format": "pdf"
}
```

**成功响应**:
```json
{
  "message": "Report export functionality not yet implemented",
  "report_id": 1,
  "format": "pdf"
}
```

## 5. 测试工具

您可以使用以下工具测试API：

1. **Postman**: 一个功能强大的API测试工具
2. **curl**: 命令行工具，适合自动化测试
3. **Insomnia**: 另一个流行的API测试工具

## 6. 常见问题

### 6.1 认证失败

如果您收到401 Unauthorized错误，请检查：
- Access token是否有效
- Token是否过期
- 请求头中的Authorization格式是否正确

### 6.2 权限不足

如果您收到403 Forbidden错误，请检查：
- 用户角色是否具有足够的权限
- 是否尝试访问其他用户的资源

### 6.3 资源未找到

如果您收到404 Not Found错误，请检查：
- 资源ID是否正确
- 资源是否已被删除

### 6.4 请求参数错误

如果您收到400 Bad Request错误，请检查：
- 请求体格式是否正确
- 是否缺少必填字段
- 字段值是否符合要求

## 7. 性能测试

为了确保系统能够支持30人同时访问，您可以使用以下工具进行性能测试：

1. **JMeter**: 一个开源的性能测试工具
2. **Locust**: 一个用Python编写的负载测试工具
3. **Postman Collections Runner**: 可以批量运行测试用例

在性能测试中，建议关注以下指标：
- 响应时间（确保平均响应时间小于10秒）
- 并发用户数（确保能支持30人同时访问）
- 错误率（确保错误率低于1%）

---

使用此测试指南，您可以全面测试日志分析系统的所有API接口，确保系统能够正常运行并满足用户需求。
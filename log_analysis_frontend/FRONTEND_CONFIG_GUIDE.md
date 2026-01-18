# 前端环境配置指南

## 1. 环境准备

### 1.1 安装Node.js

确保您的系统已安装Node.js 16或更高版本。您可以从[Node.js官方网站](https://nodejs.org/)下载并安装Node.js。

安装完成后，验证Node.js版本：

```bash
node --version
npm --version
```

## 2. 项目配置

### 2.1 安装依赖

在项目根目录下执行以下命令安装前端依赖：

```bash
cd log_analysis_frontend
npm install
```

### 2.2 配置API地址

前端API配置位于`src/services/api.js`文件中，默认配置为：

```javascript
const api = axios.create({
  baseURL: 'http://localhost:5000/api', // 后端API基础URL
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})
```

如果后端服务运行在不同的地址或端口上，请修改`baseURL`配置。

### 2.3 配置CORS

为了确保前后端能够正常通信，后端需要配置CORS（跨域资源共享）。在生产环境中，建议在后端配置CORS，而不是在前端使用代理。

## 3. 服务启动

### 3.1 启动开发服务器

在项目根目录下执行以下命令启动前端开发服务器：

```bash
npm run dev
```

前端服务将在`http://localhost:5173`或可用的端口上运行。

### 3.2 构建生产版本

在项目根目录下执行以下命令构建生产版本：

```bash
npm run build
```

构建完成后，生产文件将生成在`dist`目录中。

### 3.3 预览生产版本

在项目根目录下执行以下命令预览生产版本：

```bash
npm run preview
```

## 4. 前后端通信测试

### 4.1 检查API连接

在浏览器中打开前端应用，打开开发者工具（按F12），切换到Network选项卡，然后执行以下操作：

1. 登录应用
2. 收集或上传日志
3. 分析日志

检查网络请求是否成功，响应是否符合预期。

### 4.2 常见问题

#### 4.2.1 跨域错误

如果您在浏览器控制台中看到跨域错误（如"Access-Control-Allow-Origin"），请检查：

- 后端是否正确配置了CORS
- 前端API基础URL是否正确
- 网络连接是否正常

#### 4.2.2 API请求失败

如果API请求失败，请检查：

- 后端服务是否已启动
- 后端服务是否在正确的端口上运行
- 请求URL是否正确
- 请求参数是否符合要求

#### 4.2.3 认证失败

如果您收到401 Unauthorized错误，请检查：
- 用户是否已登录
- Token是否有效
- 请求头中的Authorization格式是否正确

## 5. 性能优化

### 5.1 前端性能优化

- 使用Vue的懒加载功能，提高初始加载速度
- 优化图片资源，减少页面加载时间
- 使用缓存策略，减少网络请求
- 优化组件渲染，避免不必要的重渲染

### 5.2 API请求优化

- 批量处理API请求，减少请求次数
- 使用分页加载，避免一次性加载大量数据
- 实现请求缓存，避免重复请求
- 使用异步请求，提高页面响应速度

## 6. 浏览器兼容性

前端应用使用Vue 3和Vite开发，支持以下浏览器：

- Chrome (最新2个版本)
- Firefox (最新2个版本)
- Safari (最新2个版本)
- Edge (最新2个版本)

## 7. 调试技巧

### 7.1 浏览器开发者工具

使用浏览器开发者工具进行调试：

- **Network**：查看API请求和响应
- **Console**：查看错误信息和日志
- **Elements**：查看和修改DOM元素
- **Sources**：调试JavaScript代码

### 7.2 Vue DevTools

安装Vue DevTools浏览器扩展，用于调试Vue组件：

- [Chrome扩展](https://chrome.google.com/webstore/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
- [Firefox扩展](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

## 8. 部署建议

### 8.1 开发环境

- 使用Vue CLI或Vite开发服务器
- 配置热重载，提高开发效率
- 启用调试模式，方便排查问题

### 8.2 生产环境

- 使用Nginx或Apache部署前端应用
- 启用Gzip压缩，减少文件大小
- 配置HTTPS，确保数据安全
- 启用缓存策略，提高访问速度

---

使用此配置指南，您可以正确配置前端环境，确保前后端能够正常通信，并优化前端应用的性能。
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api', // 后端API基础URL
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          break
        case 403:
          // 禁止访问
          alert('您没有权限执行此操作')
          break
        case 404:
          // 资源不存在
          alert('请求的资源不存在')
          break
        case 500:
          // 服务器错误
          alert('服务器内部错误，请稍后重试')
          break
        default:
          alert(`请求失败: ${error.response.data.message || error.response.statusText}`)
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      alert('网络错误，请检查网络连接')
    } else {
      // 请求配置错误
      alert(`请求错误: ${error.message}`)
    }
    return Promise.reject(error)
  }
)

export default api
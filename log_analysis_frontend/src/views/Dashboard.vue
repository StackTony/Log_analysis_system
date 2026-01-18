<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>欢迎使用日志自动分析系统</h1>
      <div class="user-info">
        <span>你好，{{ user?.username }}</span>
        <button @click="handleLogout" class="logout-button">退出登录</button>
      </div>
    </div>
    
    <div class="dashboard-stats">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total_reports || 0 }}</div>
          <div class="stat-label">总分析报告</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total_cases || 0 }}</div>
          <div class="stat-label">案例库数量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total_check_items || 0 }}</div>
          <div class="stat-label">检查项数量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total_users || 0 }}</div>
          <div class="stat-label">系统用户</div>
        </div>
      </div>
    </div>
    
    <div class="dashboard-content">
      <div class="recent-reports">
        <h2>最近分析报告</h2>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="recentReports.length === 0" class="no-data">
          暂无分析报告
        </div>
        <div v-else class="reports-list">
          <div v-for="report in recentReports" :key="report.id" class="report-item">
            <div class="report-info">
              <div class="report-title">{{ report.title }}</div>
              <div class="report-time">{{ formatDate(report.created_at) }}</div>
            </div>
            <div class="report-status" :class="report.status">
              {{ report.status === 'success' ? '完成' : report.status === 'error' ? '失败' : '处理中' }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="quick-actions">
        <h2>快速操作</h2>
        <div class="actions-list">
          <router-link to="/log-analysis" class="action-card">
            <div class="action-icon">🔍</div>
            <div class="action-text">分析日志</div>
          </router-link>
          <router-link to="/case-library" class="action-card">
            <div class="action-icon">📚</div>
            <div class="action-text">查看案例库</div>
          </router-link>
          <router-link to="/reports" class="action-card">
            <div class="action-icon">📊</div>
            <div class="action-text">查看报告</div>
          </router-link>
          <div v-if="user?.role === 'admin'" class="action-card">
            <router-link to="/check-items" class="action-text">
              <div class="action-icon">⚙️</div>
              <div class="action-text">管理检查项</div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('user')))
const stats = ref({})
const recentReports = ref([])
const loading = ref(false)

const handleLogout = () => {
  // 清除localStorage
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  // 跳转到登录页
  router.push('/login')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const fetchDashboardData = async () => {
  loading.value = true
  try {
    // 获取仪表盘统计数据
    const statsResponse = await api.get('/dashboard/stats')
    stats.value = statsResponse.data
    
    // 获取最近的分析报告
    const reportsResponse = await api.get('/reports?limit=5')
    recentReports.value = reportsResponse.data
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eaeaea;
}

.dashboard-header h1 {
  color: #333;
  font-size: 24px;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  color: #555;
}

.logout-button {
  padding: 8px 15px;
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.logout-button:hover {
  background-color: #f78989;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 40px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.recent-reports, .quick-actions {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.recent-reports h2, .quick-actions h2 {
  color: #333;
  font-size: 18px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.report-info .report-title {
  font-weight: 500;
  color: #333;
}

.report-info .report-time {
  font-size: 12px;
  color: #999;
  margin-top: 3px;
}

.report-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.report-status.success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.report-status.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.report-status.processing {
  background-color: #f0f5ff;
  color: #409eff;
}

.actions-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.action-card:hover {
  background-color: #f0f5ff;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.action-text {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.loading, .no-data {
  text-align: center;
  color: #999;
  padding: 20px;
}

@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
  
  .dashboard-stats {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}
</style>
<template>
  <div class="case-library-container">
    <div class="page-header">
      <h1>案例库管理</h1>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索案例..."
          @input="debouncedSearch"
        >
        <select v-model="filterCheckItem">
          <option value="">所有检查项</option>
          <option v-for="item in checkItems" :key="item.id" :value="item.id">
            {{ item.name }}
          </option>
        </select>
      </div>
    </div>
    
    <div class="case-stats">
      <div class="stat-item">
        <span class="stat-number">{{ cases.length }}</span>
        <span class="stat-label">总案例数</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ uniqueCheckItems.length }}</span>
        <span class="stat-label">关联检查项</span>
      </div>
    </div>
    
    <div class="case-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="cases.length === 0" class="no-data">
        暂无案例数据
      </div>
      <div v-else class="cases-grid">
        <div 
          v-for="caseItem in filteredCases" 
          :key="caseItem.id" 
          class="case-card"
        >
          <div class="case-header">
            <h3 class="case-title">{{ caseItem.title }}</h3>
            <div class="case-severity" :class="caseItem.severity">
              {{ caseItem.severity === 'high' ? '高' : caseItem.severity === 'medium' ? '中' : '低' }}
            </div>
          </div>
          
          <div class="case-meta">
            <div class="meta-item">
              <span class="meta-label">检查项：</span>
              <span class="meta-value">{{ getCheckItemName(caseItem.check_item_id) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">创建时间：</span>
              <span class="meta-value">{{ formatDate(caseItem.created_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">更新时间：</span>
              <span class="meta-value">{{ formatDate(caseItem.updated_at) }}</span>
            </div>
          </div>
          
          <div class="case-description">
            <p>{{ caseItem.description }}</p>
          </div>
          
          <div class="case-content">
            <div class="content-header">
              <strong>案例内容</strong>
              <button 
                @click="caseItem.showFull = !caseItem.showFull"
                class="toggle-button"
              >
                {{ caseItem.showFull ? '收起' : '展开' }}
              </button>
            </div>
            <div 
              class="content-body" 
              :class="{ 'show-full': caseItem.showFull }"
            >
              <pre>{{ caseItem.case_content }}</pre>
            </div>
          </div>
          
          <div class="case-actions">
            <button @click="viewCaseDetails(caseItem.id)" class="action-button view">
              查看详情
            </button>
            <button @click="editCase(caseItem.id)" class="action-button edit">
              编辑
            </button>
            <button @click="deleteCase(caseItem.id)" class="action-button delete">
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="cases.length > 0" class="pagination">
      <button 
        @click="currentPage--" 
        :disabled="currentPage === 1"
        class="page-button"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
      </span>
      <button 
        @click="currentPage++" 
        :disabled="currentPage === totalPages"
        class="page-button"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const cases = ref([])
const checkItems = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterCheckItem = ref('')
const currentPage = ref(1)
const pageSize = 10

// 防抖搜索
let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchCases()
  }, 300)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const getCheckItemName = (checkItemId) => {
  const checkItem = checkItems.value.find(item => item.id === checkItemId)
  return checkItem ? checkItem.name : '未知检查项'
}

const uniqueCheckItems = computed(() => {
  const checkItemIds = [...new Set(cases.value.map(c => c.check_item_id))]
  return checkItemIds.map(id => checkItems.value.find(item => item.id === id)).filter(Boolean)
})

const filteredCases = computed(() => {
  return cases.value.filter(caseItem => {
    const matchesSearch = caseItem.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                         caseItem.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCheckItem = !filterCheckItem.value || caseItem.check_item_id === filterCheckItem.value
    return matchesSearch && matchesCheckItem
  })
})

const paginatedCases = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredCases.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredCases.value.length / pageSize)
})

const fetchCases = async () => {
  loading.value = true
  try {
    const response = await api.get('/cases')
    cases.value = response.data.map(caseItem => ({
      ...caseItem,
      showFull: false
    }))
  } catch (error) {
    console.error('获取案例列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchCheckItems = async () => {
  try {
    const response = await api.get('/check-items')
    checkItems.value = response.data
  } catch (error) {
    console.error('获取检查项列表失败:', error)
  }
}

const viewCaseDetails = (caseId) => {
  // 跳转到案例详情页
  router.push(`/cases/${caseId}`)
}

const editCase = (caseId) => {
  // 跳转到案例编辑页
  router.push(`/cases/${caseId}/edit`)
}

const deleteCase = async (caseId) => {
  if (confirm('确定要删除这个案例吗？')) {
    try {
      await api.delete(`/cases/${caseId}`)
      cases.value = cases.value.filter(c => c.id !== caseId)
      alert('案例删除成功')
    } catch (error) {
      console.error('删除案例失败:', error)
      alert('删除案例失败：' + (error.response?.data?.message || error.message))
    }
  }
}

onMounted(() => {
  fetchCheckItems()
  fetchCases()
})
</script>

<style scoped>
.case-library-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  color: #333;
  margin: 0;
}

.search-bar {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-bar input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 300px;
}

.search-bar select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 150px;
}

.case-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 25px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.case-list {
  margin-bottom: 20px;
}

.loading, .no-data {
  text-align: center;
  padding: 50px 0;
  color: #999;
}

.cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.case-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.case-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px 20px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #eaeaea;
}

.case-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.case-severity {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.case-severity.high {
  background-color: #fef0f0;
  color: #f56c6c;
}

.case-severity.medium {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.case-severity.low {
  background-color: #f0f9eb;
  color: #67c23a;
}

.case-meta {
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  margin-bottom: 5px;
  font-size: 13px;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-label {
  color: #999;
  min-width: 80px;
}

.meta-value {
  color: #666;
}

.case-description {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.case-description p {
  margin: 0;
  color: #555;
  line-height: 1.5;
  font-size: 14px;
}

.case-content {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.content-header strong {
  color: #333;
  font-size: 14px;
}

.toggle-button {
  background: none;
  border: none;
  color: #409eff;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
}

.toggle-button:hover {
  text-decoration: underline;
}

.content-body {
  max-height: 100px;
  overflow: hidden;
  position: relative;
}

.content-body.show-full {
  max-height: none;
}

.content-body::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));
  pointer-events: none;
}

.content-body.show-full::after {
  display: none;
}

.content-body pre {
  margin: 0;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
  overflow-x: auto;
  color: #333;
}

.case-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  background-color: #f9f9f9;
}

.action-button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button.view {
  background-color: #409eff;
  color: white;
}

.action-button.view:hover {
  background-color: #66b1ff;
}

.action-button.edit {
  background-color: #e6a23c;
  color: white;
}

.action-button.edit:hover {
  background-color: #ebb563;
}

.action-button.delete {
  background-color: #f56c6c;
  color: white;
}

.action-button.delete:hover {
  background-color: #f78989;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.page-button {
  padding: 8px 15px;
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-button:hover:not(:disabled) {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.page-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-bar input {
    width: auto;
  }
  
  .cases-grid {
    grid-template-columns: 1fr;
  }
}
</style>
<template>
  <div class="check-item-container">
    <div class="page-header">
      <h1>检查项管理</h1>
      <button @click="showAddModal = true" class="add-button">
        + 新增检查项
      </button>
    </div>
    
    <div class="search-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="搜索检查项..."
        @input="debouncedSearch"
      >
      <select v-model="filterSeverity">
        <option value="">所有严重程度</option>
        <option value="high">高</option>
        <option value="medium">中</option>
        <option value="low">低</option>
      </select>
    </div>
    
    <div class="check-item-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="checkItems.length === 0" class="no-data">
        暂无检查项数据
      </div>
      <div v-else class="items-table-container">
        <table class="items-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>描述</th>
              <th>匹配模式</th>
              <th>严重程度</th>
              <th>关联案例数</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredCheckItems" :key="item.id">
              <td>{{ item.name }}</td>
              <td>{{ item.description }}</td>
              <td class="pattern-column">
                <pre>{{ item.pattern }}</pre>
              </td>
              <td>
                <span class="severity-badge" :class="item.severity">
                  {{ item.severity === 'high' ? '高' : item.severity === 'medium' ? '中' : '低' }}
                </span>
              </td>
              <td>{{ item.case_count || 0 }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td class="actions-column">
                <button @click="editCheckItem(item)" class="action-button edit">
                  编辑
                </button>
                <button @click="deleteCheckItem(item.id)" class="action-button delete">
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 新增/编辑模态框 -->
    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? '编辑检查项' : '新增检查项' }}</h3>
          <button @click="closeModal" class="close-button">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveCheckItem">
            <div class="form-group">
              <label for="name">检查项名称</label>
              <input 
                type="text" 
                id="name" 
                v-model="currentItem.name" 
                required
                placeholder="请输入检查项名称"
              >
            </div>
            <div class="form-group">
              <label for="description">描述</label>
              <textarea 
                id="description" 
                v-model="currentItem.description" 
                required
                rows="3"
                placeholder="请输入检查项描述"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="pattern">匹配模式 (正则表达式)</label>
              <input 
                type="text" 
                id="pattern" 
                v-model="currentItem.pattern" 
                required
                placeholder="例如：ERROR.*\b(exception|error)\b"
              >
            </div>
            <div class="form-group">
              <label for="severity">严重程度</label>
              <select id="severity" v-model="currentItem.severity" required>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeModal" class="cancel-button">
                取消
              </button>
              <button type="submit" class="save-button" :disabled="saving">
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const checkItems = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const filterSeverity = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)

const currentItem = ref({
  name: '',
  description: '',
  pattern: '',
  severity: 'high'
})

// 防抖搜索
let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    // 本地过滤，不需要重新请求接口
  }, 300)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const filteredCheckItems = computed(() => {
  return checkItems.value.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                         item.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesSeverity = !filterSeverity.value || item.severity === filterSeverity.value
    return matchesSearch && matchesSeverity
  })
})

const fetchCheckItems = async () => {
  loading.value = true
  try {
    const response = await api.get('/check-items')
    checkItems.value = response.data
  } catch (error) {
    console.error('获取检查项列表失败:', error)
    alert('获取检查项列表失败：' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const addCheckItem = () => {
  showAddModal.value = true
  showEditModal.value = false
  resetCurrentItem()
}

const editCheckItem = (item) => {
  showEditModal.value = true
  showAddModal.value = false
  currentItem.value = { ...item }
}

const deleteCheckItem = async (itemId) => {
  if (confirm('确定要删除这个检查项吗？删除后关联的案例也会受到影响。')) {
    try {
      await api.delete(`/check-items/${itemId}`)
      checkItems.value = checkItems.value.filter(item => item.id !== itemId)
      alert('检查项删除成功')
    } catch (error) {
      console.error('删除检查项失败:', error)
      alert('删除检查项失败：' + (error.response?.data?.message || error.message))
    }
  }
}

const saveCheckItem = async () => {
  saving.value = true
  try {
    if (showEditModal.value) {
      // 更新检查项
      await api.put(`/check-items/${currentItem.value.id}`, currentItem.value)
      // 更新本地数据
      const index = checkItems.value.findIndex(item => item.id === currentItem.value.id)
      if (index !== -1) {
        checkItems.value[index] = { ...currentItem.value }
      }
      alert('检查项更新成功')
    } else {
      // 新增检查项
      const response = await api.post('/check-items', currentItem.value)
      checkItems.value.push(response.data)
      alert('检查项新增成功')
    }
    closeModal()
  } catch (error) {
    console.error('保存检查项失败:', error)
    alert('保存检查项失败：' + (error.response?.data?.message || error.message))
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  resetCurrentItem()
}

const resetCurrentItem = () => {
  currentItem.value = {
    name: '',
    description: '',
    pattern: '',
    severity: 'high'
  }
}

onMounted(() => {
  fetchCheckItems()
})
</script>

<style scoped>
.check-item-container {
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

.add-button {
  padding: 10px 20px;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.add-button:hover {
  background-color: #85ce61;
}

.search-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
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
  min-width: 120px;
}

.check-item-list {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading, .no-data {
  text-align: center;
  padding: 50px 0;
  color: #999;
}

.items-table-container {
  overflow-x: auto;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
}

.items-table th, .items-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eaeaea;
}

.items-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.items-table td {
  color: #666;
}

.pattern-column {
  max-width: 250px;
}

.pattern-column pre {
  margin: 0;
  padding: 5px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  overflow-x: auto;
  max-height: 80px;
}

.severity-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.severity-badge.high {
  background-color: #fef0f0;
  color: #f56c6c;
}

.severity-badge.medium {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.severity-badge.low {
  background-color: #f0f9eb;
  color: #67c23a;
}

.actions-column {
  white-space: nowrap;
}

.action-button {
  padding: 6px 12px;
  margin-right: 5px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button.edit {
  background-color: #409eff;
  color: white;
}

.action-button.edit:hover {
  background-color: #66b1ff;
}

.action-button.delete {
  background-color: #f56c6c;
  color: white;
}

.action-button.delete:hover {
  background-color: #f78989;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.close-button:hover {
  background-color: #f5f7fa;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.cancel-button {
  padding: 10px 20px;
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.cancel-button:hover {
  background-color: #e9eef3;
}

.save-button {
  padding: 10px 20px;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.save-button:hover:not(:disabled) {
  background-color: #85ce61;
}

.save-button:disabled {
  background-color: #a0d787;
  cursor: not-allowed;
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
  
  .items-table {
    font-size: 13px;
  }
  
  .items-table th, .items-table td {
    padding: 8px 10px;
  }
  
  .pattern-column {
    max-width: 150px;
  }
}
</style>
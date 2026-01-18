<template>
  <div class="log-analysis-container">
    <h1>日志分析</h1>
    
    <div class="analysis-tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-item"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </div>
    </div>
    
    <div class="analysis-content">
      <!-- 命令输入 -->
      <div v-if="activeTab === 'command'" class="input-section">
        <div class="form-group">
          <label for="command">收集命令</label>
          <input 
            type="text" 
            id="command" 
            v-model="commandInput" 
            placeholder="例如：tail -n 1000 /var/log/syslog"
          >
        </div>
        <div class="form-group">
          <label for="host">目标主机</label>
          <input 
            type="text" 
            id="host" 
            v-model="hostInput" 
            placeholder="例如：192.168.1.100"
          >
        </div>
        <div class="form-group">
          <label for="user">用户名</label>
          <input 
            type="text" 
            id="user" 
            v-model="userInput" 
            placeholder="SSH用户名"
          >
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="passwordInput" 
            placeholder="SSH密码"
          >
        </div>
      </div>
      
      <!-- 文件上传 -->
      <div v-else-if="activeTab === 'file'" class="input-section">
        <div class="form-group">
          <label for="file-upload">上传日志文件</label>
          <input 
            type="file" 
            id="file-upload" 
            ref="fileInput"
            @change="handleFileChange"
            accept=".log,.txt,.gz"
          >
          <div v-if="selectedFile" class="file-info">
            已选择：{{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </div>
        </div>
      </div>
      
      <!-- API输入 -->
      <div v-else-if="activeTab === 'api'" class="input-section">
        <div class="form-group">
          <label for="api-log">日志内容</label>
          <textarea 
            id="api-log" 
            v-model="apiLogInput" 
            placeholder="在此粘贴日志内容或输入API返回的日志数据"
            rows="10"
          ></textarea>
        </div>
      </div>
      
      <!-- 分析选项 -->
      <div class="analysis-options">
        <div class="option-group">
          <label>
            <input type="checkbox" v-model="options.aiAnalysis" checked>
            <span>启用AI分析</span>
          </label>
        </div>
        <div class="option-group">
          <label>
            <input type="checkbox" v-model="options.saveToCaseLibrary">
            <span>保存到案例库</span>
          </label>
        </div>
      </div>
      
      <!-- 分析按钮 -->
      <div class="analysis-actions">
        <button 
          @click="startAnalysis" 
          class="analysis-button" 
          :disabled="loading || !canStartAnalysis"
        >
          {{ loading ? '分析中...' : '开始分析' }}
        </button>
      </div>
      
      <!-- 分析进度 -->
      <div v-if="loading" class="analysis-progress">
        <div class="progress-bar">
          <div class="progress" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="progress-text">{{ progressText }}</div>
      </div>
      
      <!-- 分析结果 -->
      <div v-if="analysisResult" class="analysis-results">
        <h2>分析结果</h2>
        
        <!-- 分析报告基本信息 -->
        <div class="report-info">
          <div class="report-item">
            <span class="label">报告标题：</span>
            <span class="value">{{ analysisResult.title }}</span>
          </div>
          <div class="report-item">
            <span class="label">分析时间：</span>
            <span class="value">{{ formatDate(analysisResult.created_at) }}</span>
          </div>
          <div class="report-item">
            <span class="label">分析状态：</span>
            <span class="value status" :class="analysisResult.status">
              {{ analysisResult.status === 'success' ? '完成' : analysisResult.status === 'error' ? '失败' : '处理中' }}
            </span>
          </div>
        </div>
        
        <!-- 匹配的检查项 -->
        <div class="matched-items" v-if="analysisResult.matched_check_items && analysisResult.matched_check_items.length > 0">
          <h3>匹配的检查项</h3>
          <div class="items-list">
            <div 
              v-for="item in analysisResult.matched_check_items" 
              :key="item.id" 
              class="item-card"
            >
              <div class="item-header">
                <div class="item-name">{{ item.name }}</div>
                <div class="item-severity" :class="item.severity">
                  {{ item.severity === 'high' ? '高' : item.severity === 'medium' ? '中' : '低' }}
                </div>
              </div>
              <div class="item-description">{{ item.description }}</div>
              <div class="item-pattern">
                <strong>匹配模式：</strong>{{ item.pattern }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- AI分析结果 -->
        <div v-if="analysisResult.ai_analysis" class="ai-analysis">
          <h3>AI分析洞察</h3>
          <div class="ai-summary">
            <strong>日志摘要：</strong>{{ analysisResult.ai_analysis.summary }}
          </div>
          <div class="ai-anomalies" v-if="analysisResult.ai_analysis.anomalies && analysisResult.ai_analysis.anomalies.length > 0">
            <strong>异常检测：</strong>
            <ul>
              <li v-for="(anomaly, index) in analysisResult.ai_analysis.anomalies" :key="index">
                {{ anomaly }}
              </li>
            </ul>
          </div>
          <div class="ai-recommendations" v-if="analysisResult.ai_analysis.recommendations && analysisResult.ai_analysis.recommendations.length > 0">
            <strong>优化建议：</strong>
            <ul>
              <li v-for="(recommendation, index) in analysisResult.ai_analysis.recommendations" :key="index">
                {{ recommendation }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../services/api'

const tabs = [
  { id: 'command', label: '命令收集' },
  { id: 'file', label: '文件上传' },
  { id: 'api', label: 'API输入' }
]

const activeTab = ref('command')
const loading = ref(false)
const progress = ref(0)
const progressText = ref('')
const analysisResult = ref(null)

// 命令输入
const commandInput = ref('')
const hostInput = ref('')
const userInput = ref('')
const passwordInput = ref('')

// 文件上传
const fileInput = ref(null)
const selectedFile = ref(null)

// API输入
const apiLogInput = ref('')

// 分析选项
const options = ref({
  aiAnalysis: true,
  saveToCaseLibrary: true
})

const handleFileChange = (event) => {
  if (event.target.files && event.target.files.length > 0) {
    selectedFile.value = event.target.files[0]
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const canStartAnalysis = computed(() => {
  if (activeTab.value === 'command') {
    return commandInput.value && hostInput.value && userInput.value
  } else if (activeTab.value === 'file') {
    return selectedFile.value
  } else if (activeTab.value === 'api') {
    return apiLogInput.value.trim()
  }
  return false
})

const startAnalysis = async () => {
  loading.value = true
  progress.value = 0
  progressText.value = '准备分析...'
  analysisResult.value = null
  
  try {
    let logData
    
    // 根据不同的输入方式获取日志数据
    if (activeTab.value === 'command') {
      // 命令收集日志
      progressText.value = '执行命令收集日志...'
      const commandResponse = await api.post('/log/collect', {
        command: commandInput.value,
        host: hostInput.value,
        username: userInput.value,
        password: passwordInput.value
      })
      logData = commandResponse.data.log_content
      progress.value = 30
    } else if (activeTab.value === 'file') {
      // 文件上传日志
      progressText.value = '上传日志文件...'
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      
      const uploadResponse = await api.post('/log/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      logData = uploadResponse.data.log_content
      progress.value = 30
    } else if (activeTab.value === 'api') {
      // API输入日志
      logData = apiLogInput.value
      progress.value = 30
    }
    
    // 执行日志分析
    progressText.value = '分析日志数据...'
    const analysisResponse = await api.post('/log/analyze', {
      log_data: logData,
      options: {
        ai_analysis: options.value.aiAnalysis,
        save_to_case_library: options.value.saveToCaseLibrary
      }
    })
    
    progress.value = 100
    progressText.value = '分析完成！'
    analysisResult.value = analysisResponse.data
  } catch (error) {
    console.error('日志分析失败:', error)
    progressText.value = '分析失败：' + (error.response?.data?.message || error.message)
  } finally {
    // 延迟关闭加载状态，让用户看到完成状态
    setTimeout(() => {
      loading.value = false
    }, 1000)
  }
}
</script>

<style scoped>
.log-analysis-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.log-analysis-container h1 {
  color: #333;
  margin-bottom: 20px;
}

.analysis-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eaeaea;
}

.tab-item {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: #666;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.analysis-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.input-section {
  margin-bottom: 25px;
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
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
}

.file-info {
  margin-top: 10px;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
}

.analysis-options {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.option-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #555;
}

.analysis-actions {
  margin-bottom: 25px;
}

.analysis-button {
  padding: 12px 30px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.analysis-button:hover:not(:disabled) {
  background-color: #66b1ff;
}

.analysis-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.analysis-progress {
  margin-bottom: 25px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress {
  height: 100%;
  background-color: #409eff;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.analysis-results {
  margin-top: 30px;
}

.analysis-results h2 {
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
}

.report-info {
  margin-bottom: 25px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.report-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.report-item:last-child {
  margin-bottom: 0;
}

.report-item .label {
  font-weight: 500;
  color: #555;
  min-width: 80px;
}

.report-item .value {
  color: #333;
}

.report-item .status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.report-item .status.success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.report-item .status.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.report-item .status.processing {
  background-color: #f0f5ff;
  color: #409eff;
}

.matched-items h3 {
  color: #333;
  margin-bottom: 15px;
}

.items-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 15px;
}

.item-card {
  padding: 15px;
  background-color: white;
  border: 1px solid #eaeaea;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.item-name {
  font-weight: 500;
  color: #333;
}

.item-severity {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.item-severity.high {
  background-color: #fef0f0;
  color: #f56c6c;
}

.item-severity.medium {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.item-severity.low {
  background-color: #f0f9eb;
  color: #67c23a;
}

.item-description {
  color: #666;
  margin-bottom: 10px;
  font-size: 14px;
}

.item-pattern {
  font-family: monospace;
  font-size: 13px;
  color: #333;
  background-color: #f9f9f9;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
}

.ai-analysis {
  margin-top: 30px;
  padding: 20px;
  background-color: #f0f5ff;
  border-radius: 4px;
}

.ai-analysis h3 {
  color: #333;
  margin-bottom: 15px;
}

.ai-summary {
  margin-bottom: 20px;
  line-height: 1.6;
}

.ai-anomalies,
.ai-recommendations {
  margin-bottom: 20px;
}

.ai-anomalies ul,
.ai-recommendations ul {
  padding-left: 20px;
  line-height: 1.6;
}

.ai-anomalies li,
.ai-recommendations li {
  margin-bottom: 5px;
}
</style>
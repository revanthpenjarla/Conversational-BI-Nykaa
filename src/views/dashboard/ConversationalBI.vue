<template>
  <div class="d-flex flex-column">
    <!-- Upload Section -->
    <CRow class="mb-4">
      <CCol :md="12">
        <CCard class="shadow-sm border-0 rounded-4">
          <CCardBody class="d-flex justify-content-between align-items-center">
            <div>
              <h5 class="mb-1 fw-bold">Data Source</h5>
              <p class="text-muted mb-0 small" v-if="uploadedFilename">
                Currently loaded: <strong>{{ uploadedFilename }}</strong> ({{ uploadedRowCount }} rows)
              </p>
              <p class="text-muted mb-0 small" v-else>
                Upload a CSV to start analyzing your own data.
              </p>
            </div>
            <div class="d-flex align-items-center">
              <input type="file" ref="fileInput" @change="handleFileUpload" accept=".csv,.xlsx,.xls" class="d-none" />
              <CButton color="primary" @click="$refs.fileInput?.click()" :disabled="uploading" class="fw-bold px-4 rounded-pill">
                <CIcon icon="cil-cloud-upload" class="me-2"/>
                {{ uploading ? 'Uploading...' : 'Upload Data' }}
              </CButton>
            </div>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>

  <CRow>
    <!-- LEFT SIDE - Chat Panel -->
    <CCol :lg="4">
      <CCard class="mb-4 h-100 shadow-sm border-0" style="border-radius: 12px; transition: all 0.3s ease;">
        <CCardHeader class="bg-primary text-white" style="border-top-left-radius: 12px; border-top-right-radius: 12px;">
          <h5 class="mb-0 fw-bold d-flex align-items-center">
            <span class="fs-4 me-2">🧠</span> Ask AI
          </h5>
        </CCardHeader>
        <CCardBody class="d-flex flex-column bg-body" style="height: 650px;">
          <!-- Chat History -->
          <div class="flex-grow-1 mb-4 overflow-auto pe-2 chat-container" style="max-height: 520px;">
            <div v-if="chatHistory.length === 0" class="d-flex flex-column align-items-center justify-content-center h-100 text-muted">
              <CIcon icon="cil-speech" size="3xl" class="mb-3 opacity-50" />
              <p class="fs-5 text-center px-4">Type a question to start exploring your data!</p>
            </div>
            
            <div 
              v-for="(msg, index) in chatHistory" 
              :key="index" 
              class="mb-3 p-3 shadow-sm chat-message"
              :class="msg.role === 'user' ? 'bg-primary text-white ms-4' : 'bg-secondary text-white me-4'"
              :style="{ 
                borderRadius: msg.role === 'user' ? '16px 16px 0 16px' : '16px 16px 16px 0',
                transition: 'all 0.3s ease'
              }"
            >
              <div class="small fw-bold mb-1" :class="msg.role === 'user' ? 'text-end text-light' : 'text-light opacity-75'">
                {{ msg.role === 'user' ? 'You' : 'Nykaa AI' }}
              </div>
              <div :class="msg.role === 'user' ? 'text-end' : ''">{{ msg.text }}</div>
            </div>
            
            <div v-if="loading" class="d-flex align-items-center mb-3 p-3 bg-info bg-opacity-10 me-4 shadow-sm" style="border-radius: 16px 16px 16px 0;">
              <CSpinner size="sm" color="primary" class="me-3" /> 
              <span class="text-primary fw-bold pulse-text">AI is analyzing your data...</span>
            </div>
          </div>
          
          <CAlert color="danger" v-if="error" class="mb-3 py-2 small shadow-sm rounded-3">{{ error }}</CAlert>

          <!-- Input Box -->
          <div class="mt-auto">
            <CInputGroup class="shadow-sm rounded-3 overflow-hidden">
              <CFormInput 
                v-model="prompt" 
                :placeholder="hasData ? 'Ask your data a question...' : 'Upload a dataset to begin...'" 
                @keyup.enter="askAI"
                :disabled="loading || !hasData"
                class="border-0 shadow-none py-2 px-3 focus-ring-0"
              />
              <CButton color="primary" @click="askAI" :disabled="loading || !prompt.trim() || !hasData" class="px-4 border-0">
                <CIcon icon="cil-send" v-if="!loading" class="me-1"/>
                <span class="fw-bold">{{ loading ? '...' : 'Send' }}</span>
              </CButton>
            </CInputGroup>
          </div>
        </CCardBody>
      </CCard>
    </CCol>

    <!-- RIGHT SIDE - Dashboard Panel -->
    <CCol :lg="8">
      <CCard class="mb-4 h-100 shadow-sm border-0" style="border-radius: 12px;">
        <CCardHeader class="bg-dark text-white d-flex justify-content-between align-items-center" style="border-top-left-radius: 12px; border-top-right-radius: 12px;">
          <h5 class="mb-0 fw-bold">Dashboard Visuals</h5>
          <CBadge color="info" shape="rounded-pill" class="px-3 py-2" v-if="currentChartType">{{ currentChartType.toUpperCase() }}</CBadge>
        </CCardHeader>
        <CCardBody class="d-flex flex-column bg-body overflow-auto" style="max-height: 650px;">
          
          <div v-if="!currentChartTitle" class="flex-grow-1 d-flex flex-column align-items-center justify-content-center text-muted h-100 py-5">
            <div class="fs-1 mb-3 bg-light rounded-circle p-4 shadow-sm">📊</div>
            <div class="fs-4">Your generated charts will appear here.</div>
            <p class="mt-2 opacity-75">Ask a question to see your data visualized.</p>
          </div>

          <div v-else class="flex-grow-1 fade-in">
            <h4 class="text-center mb-4 text-dark fw-bold">{{ currentChartTitle }}</h4>
            
            <!-- Chart Container -->
            <div class="chart-wrapper mx-auto mb-5 p-3 rounded-4 shadow-sm" style="background: transparent !important; border: none; height: 400px; min-height: 250px; width: 100%; position: relative;">
              <canvas id="myChart" style="height: 100%; width: 100%;"></canvas>
            </div>
            
            <CRow>
              <CCol :md="12" class="mb-4">
                 <CCard class="shadow-sm border-0 rounded-4">
                  <CCardBody>
                     <h6 class="fw-bold mb-3 d-flex align-items-center">
                        <CIcon icon="cil-list" class="me-2 text-primary"/> Raw Data
                     </h6>
                    <div style="max-height: 400px; overflow-y: auto;" class="rounded-3 border">
                      <CTable hover striped small align="middle" class="mb-0 bg-body">
                        <CTableHead class="bg-body-secondary position-sticky top-0 z-1">
                          <CTableRow>
                            <CTableHeaderCell v-for="col in columns" :key="col" class="py-3 px-3 border-bottom">{{ col }}</CTableHeaderCell>
                          </CTableRow>
                        </CTableHead>
                        <CTableBody>
                          <CTableRow v-for="(row, i) in tableData" :key="i">
                            <CTableDataCell v-for="col in columns" :key="col" class="px-3">{{ row[col] }}</CTableDataCell>
                          </CTableRow>
                        </CTableBody>
                      </CTable>
                    </div>
                  </CCardBody>
                 </CCard>
              </CCol>

              <CCol :md="12" v-if="currentInsight" class="mb-4">
                 <CAlert color="info" class="shadow-sm border-0 rounded-4 m-0">
                   <h6 class="fw-bold mb-2 d-flex align-items-center" style="color: #0c5460;">
                      <CIcon icon="cil-lightbulb" class="me-2"/> AI Observation
                   </h6>
                   <p class="mb-0" style="color: #0c5460;">{{ currentInsight }}</p>
                 </CAlert>
              </CCol>

              <CCol :md="12" v-if="currentSummary">
                 <CCard class="shadow-sm border-0 rounded-4 mb-4">
                   <CCardBody>
                     <h6 class="fw-bold mb-3 d-flex align-items-center">
                        <CIcon icon="cil-info" class="me-2 text-primary"/> Query Explanation
                     </h6>
                     <p class="text-muted mb-0">{{ currentSummary }}</p>
                   </CCardBody>
                 </CCard>
              </CCol>

              <CCol :md="12">
                 <CCard class="shadow-sm border-0 rounded-4">
                   <CCardBody>
                     <div class="d-flex justify-content-between align-items-center mb-3">
                       <h6 class="fw-bold mb-0 d-flex align-items-center">
                          <CIcon icon="cil-code" class="me-2 text-primary"/> Generated SQL
                       </h6>
                       <div class="d-flex align-items-center">
                         <CButton color="secondary" variant="ghost" size="sm" @click="copySql" class="me-3 p-1" title="Copy SQL">
                            <CIcon icon="cil-copy" />
                         </CButton>
                         <CBadge color="success" shape="rounded-pill" v-if="isVerified">
                            <CIcon icon="cil-check-circle" class="me-1"/> Verified by SQL Agent
                         </CBadge>
                       </div>
                     </div>
                    <!-- Generated SQL Snippet -->
                    <div v-if="currentSql" class="p-3 bg-dark text-light border border-secondary shadow-sm" style="border-radius: 12px;">
                      <pre class="mb-0"><code class="text-light" style="white-space: pre-wrap; font-family: 'Courier New', Courier, monospace; font-size: 0.9rem;">{{ currentSql }}</code></pre>
                    </div>
                   </CCardBody>
                 </CCard>
              </CCol>
            </CRow>
          </div>

        </CCardBody>
      </CCard>
    </CCol>
  </CRow>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

// Chat Panel State
const sessionId = ref('')
const prompt = ref('')
const loading = ref(false)
const error = ref('')
const chatHistory = ref([])

// Dashboard Panel State
const currentChartType = ref('')
const currentChartTitle = ref('')
const currentSql = ref('')
const currentSummary = ref('')
const currentInsight = ref('')
const isVerified = ref(false)
const columns = ref([])
const tableData = ref([])

// CSV Upload State
const fileInput = ref(null)
const uploading = ref(false)
const uploadedFilename = ref('')
const uploadedRowCount = ref(0)
const hasData = ref(false)

// Generate persistent session string once on load
onMounted(() => {
  const storedSession = localStorage.getItem('nykaa_session_id')
  if (storedSession) {
    sessionId.value = storedSession
  } else {
    sessionId.value = 'session_' + Math.random().toString(36).substring(2, 10)
    localStorage.setItem('nykaa_session_id', sessionId.value)
  }
})

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await axios.post('http://127.0.0.1:8000/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    if (res.data.success) {
      uploadedFilename.value = res.data.filename
      uploadedRowCount.value = res.data.row_count
      hasData.value = true
      
      // Reset chat
      sessionId.value = 'session_' + Math.random().toString(36).substring(2, 10)
      localStorage.setItem('nykaa_session_id', sessionId.value)
      const successMsg = res.data.format_msg || 'File loaded successfully!'
      chatHistory.value = [{ role: 'ai', text: `${successMsg} You can now ask questions about your data.` }]
      
      // Clear charts and data ("garbage" cleanup per user request)
      currentChartTitle.value = ''
      currentSql.value = ''
      currentSummary.value = ''
      currentInsight.value = ''
      tableData.value = []
      columns.value = []
      if (window.myChartInstance) {
        window.myChartInstance.destroy()
        window.myChartInstance = null
      }
    } else {
      error.value = res.data.error || 'Failed to upload CSV'
    }
  } catch (err) {
    error.value = 'Error uploading file'
    console.error(err)
  } finally {
    uploading.value = false
    event.target.value = '' // reset input
  }
}

// Copy SQL action
const copySql = () => {
  if (currentSql.value) {
    navigator.clipboard.writeText(currentSql.value)
  }
}

const askAI = async () => {
  const userText = prompt.value.trim()
  if (!userText) return

  // 1. Update Chat
  chatHistory.value.push({ role: 'user', text: userText })
  prompt.value = ''
  error.value = ''
  loading.value = true

  try {
    // 2. Make API Call
    const res = await axios.post('http://127.0.0.1:8000/generate-dashboard', {
      prompt: userText,
      session_id: sessionId.value
    })

    if (res.data.success) {
      chatHistory.value.push({ role: 'ai', text: 'Here is your dashboard based on the data.' })
      
      // 3. Update Dashboard Panel
      currentChartTitle.value = userText
      currentSql.value = res.data.sql
      currentSummary.value = res.data.explanation || res.data.summary || ''
      currentInsight.value = res.data.insight || ''
      isVerified.value = !!(res.data.verified || res.data.sql_verified || res.data.sql_verified === true || res.data.success === true && res.data.verified !== false) // Basic mapping to allow any truthy verifications
      columns.value = res.data.columns || []
      tableData.value = res.data.data || []
      
      const typeStr = res.data.chart_type?.toLowerCase() || 'bar'
      currentChartType.value = ['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(typeStr) ? typeStr : 'bar'

      if (window.myChartInstance) {
        window.myChartInstance.destroy()
        window.myChartInstance = null
      }

      if (!tableData.value || tableData.value.length === 0) {
        chatHistory.value.push({ role: 'ai', text: 'No results found. Try asking about a different campaign or date.' })
      } else {
        const hasEnoughCols = columns.value && columns.value.length >= 2
        let isSecondColNumeric = false
        
        if (hasEnoughCols) {
          const yAxisCol = columns.value[1]
          isSecondColNumeric = tableData.value.some(row => !isNaN(parseFloat(row[yAxisCol])))
        }

        if (!hasEnoughCols || !isSecondColNumeric) {
          chatHistory.value.push({ role: 'ai', text: 'Could not generate chart. Try rephrasing your question.' })
        } else {
          const xAxisObj = columns.value[0]
          const yAxisObj = columns.value[1]

          const validData = tableData.value.filter(row => !isNaN(parseFloat(row[yAxisObj])))
          const extractedLabels = validData.map(row => row[xAxisObj])
          const extractedValues = validData.map(row => parseFloat(row[yAxisObj]))

          nextTick(() => {
            if (window.myChartInstance) {
              window.myChartInstance.destroy()
            }
            const ctx = document.getElementById('myChart')
            if (ctx) {
              window.myChartInstance = new Chart(ctx.getContext('2d'), {
                type: currentChartType.value,
                data: {
                  labels: extractedLabels,
                  datasets: [{
                    label: yAxisObj,
                    data: extractedValues,
                    backgroundColor: [
                      '#6366f1','#8b5cf6','#ec4899','#f43f5e','#f97316'
                    ]
                  }]
                },
                options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: true }
                  }
                }
              })
            }
          })
        }
      }
    } else {
      error.value = res.data.error || 'The API encountered an error.'
      chatHistory.value.push({ role: 'ai', text: 'Nykaa AI: Sorry, could not process your query. Please try again.' })
    }
  } catch (err) {
    error.value = 'Failed to connect to backend on port 8000. Is FastAPI running?'
    chatHistory.value.push({ role: 'ai', text: error.value })
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-container::-webkit-scrollbar {
  width: 6px;
}
.chat-container::-webkit-scrollbar-track {
  background: transparent;
}
.chat-container::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,0.1);
  border-radius: 10px;
}
.pulse-text {
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

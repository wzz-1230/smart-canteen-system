<template>
  <div class="log-analysis">
    <!-- 顶部整体分析按钮 -->
    <el-row :gutter="20" class="row-overall">
      <el-col :span="24">
        <el-card shadow="hover" class="overall-card">
          <div class="overall-inner">
            <div class="overall-left">
              <el-icon :size="32" color="#409EFF"><MagicStick /></el-icon>
              <div class="overall-info">
                <div class="overall-title">系统日志 AI 智能分析</div>
                <div class="overall-sub">整合请求趋势、类型分布、登录情况，一键生成全面的系统运行分析报告</div>
              </div>
            </div>
            <el-button
              type="primary"
              size="large"
              :loading="analyzing.overall"
              @click="analyzeOverall"
              class="overall-btn">
              <el-icon><MagicStick /></el-icon>
              <span>&nbsp;一键 AI 整体分析</span>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-inner">
            <div class="icon-box icon-blue">
              <el-icon :size="28"><DataLine /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">总请求</div>
              <div class="text-value">{{ formatNumber(summary.total_request) }}</div>
              <div class="text-sub">累计请求数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-inner">
            <div class="icon-box icon-green">
              <el-icon :size="28"><CircleCheck /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">成功请求</div>
              <div class="text-value text-success">{{ formatNumber(summary.success_request) }}</div>
              <div class="text-sub">
                成功率 {{ summary.success_request && summary.total_request
                  ? ((summary.success_request / summary.total_request) * 100).toFixed(2)
                  : '0.00' }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-inner">
            <div class="icon-box icon-red">
              <el-icon :size="28"><CircleClose /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">失败请求</div>
              <div class="text-value text-danger">{{ formatNumber(summary.failed_request) }}</div>
              <div class="text-sub">
                失败率 {{ summary.failed_request && summary.total_request
                  ? ((summary.failed_request / summary.total_request) * 100).toFixed(2)
                  : '0.00' }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-inner">
            <div class="icon-box icon-orange">
              <el-icon :size="28"><Timer /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">平均响应</div>
              <div class="text-value text-warning">{{ summary.avg_response_time }} ms</div>
              <div class="text-sub">平均响应时间</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" v-loading="loading">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><TrendCharts /></el-icon>
                <span>&nbsp;请求趋势（近7天）</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeTrend" :loading="analyzing.trend">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" v-loading="loading">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><PieChart /></el-icon>
                <span>&nbsp;请求类型分布</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeTypes" :loading="analyzing.types">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="typeChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover" v-loading="loading">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><DataLine /></el-icon>
                <span>&nbsp;登录成功率对比（近7天）</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeLogin" :loading="analyzing.login">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="loginChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="table-row">
      <el-col :span="24">
        <el-card shadow="hover" v-loading="loading">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Document /></el-icon>
                <span>&nbsp;最近操作日志</span>
              </div>
            </div>
          </template>
          <el-table :data="recentLogs" border stripe style="width: 100%" max-height="400px">
            <el-table-column prop="logTime" label="时间" width="200" />
            <el-table-column label="操作" width="140">
              <template #default="scope">
                <el-tag size="small" :type="getLogTagType(scope.row.operation)">{{ scope.row.operation }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="module" label="模块" width="160" />
            <el-table-column prop="userName" label="用户名" width="140" />
            <el-table-column label="状态" width="120">
              <template #default="scope">
                <el-tag :type="isSuccessStatus(scope.row.status) ? 'success' : 'danger'" size="small">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="备注" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI 分析结果弹窗（增强版） -->
    <el-dialog
      v-model="aiResultDialog.visible"
      :title="aiResultDialog.title"
      width="780px"
      top="5vh"
      :close-on-click-modal="false">
      <div class="ai-content">
        <div class="ai-header">
          <el-icon :size="36" color="#409EFF"><MagicStick /></el-icon>
          <div class="ai-header-text">
            <div class="ai-title">AI 智能分析报告</div>
            <div class="ai-subtitle">基于实时数据分析 · {{ currentTimeStr }}</div>
          </div>
          <div class="ai-header-tag">
            <el-tag :type="aiResultDialog.dataType === 'overall' ? 'danger' : 'primary'" size="small">
              {{ aiResultDialog.dataType === 'overall' ? '整体分析' : '单项分析' }}
            </el-tag>
          </div>
        </div>

        <div class="ai-toolbar" v-if="aiResultDialog.content && !aiLoading">
          <el-button size="small" @click="copyAnalysis">
            <el-icon><DocumentCopy /></el-icon>
            <span>&nbsp;复制内容</span>
          </el-button>
          <el-button size="small" type="success" @click="exportAsMarkdown">
            <el-icon><Download /></el-icon>
            <span>&nbsp;导出 Markdown</span>
          </el-button>
          <el-button size="small" type="warning" @click="exportAsText">
            <el-icon><Document /></el-icon>
            <span>&nbsp;导出 TXT</span>
          </el-button>
          <el-button size="small" type="info" @click="printAnalysis">
            <el-icon><Printer /></el-icon>
            <span>&nbsp;打印报告</span>
          </el-button>
        </div>

        <div class="ai-body" :class="{ 'ai-loading': aiLoading }" v-loading="aiLoading">
          <div v-if="aiResultDialog.content" class="ai-markdown-content" v-html="renderedMarkdown"></div>
          <el-empty v-else-if="!aiLoading" description="暂无分析结果，请点击 AI 分析按钮生成报告" />
        </div>
      </div>
      <template #footer>
        <el-button @click="aiResultDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { DataLine, CircleCheck, CircleClose, Timer, TrendCharts, PieChart, Document, MagicStick, DocumentCopy, Download, Printer } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getLogAnalysisSummary, getLogTrend, getLogTypeDistribution, getLogLoginStats } from '@/api/visualization'
import { aiAnalyze } from '@/api/ai'

const loading = ref(false)
const aiLoading = ref(false)
const summary = ref({
  total_request: 0,
  success_request: 0,
  failed_request: 0,
  avg_response_time: 0,
  total_login: 0,
  success_login: 0,
  failed_login: 0
})
const recentLogs = ref([])
const trendData = ref([])
const typeData = ref([])
const loginData = ref([])
const trendChartRef = ref(null)
const typeChartRef = ref(null)
const loginChartRef = ref(null)
let trendChart = null
let typeChart = null
let loginChart = null

const analyzing = reactive({ trend: false, types: false, login: false, overall: false })
const aiResultDialog = reactive({ visible: false, title: 'AI 智能分析', content: '', dataType: '' })

const currentTimeStr = computed(() => {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`
})

const renderedMarkdown = computed(() => {
  if (!aiResultDialog.content) return ''
  return renderMarkdown(aiResultDialog.content)
})

// 轻量级 Markdown 渲染函数（与食堂销售看板相同）
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  html = html.replace(/^######\s+(.+)$/gm, '<h6 class="md-h6">$1</h6>')
  html = html.replace(/^#####\s+(.+)$/gm, '<h5 class="md-h5">$1</h5>')
  html = html.replace(/^####\s+(.+)$/gm, '<h4 class="md-h4">$1</h4>')
  html = html.replace(/^###\s+(.+)$/gm, '<h3 class="md-h3">$1</h3>')
  html = html.replace(/^##\s+(.+)$/gm, '<h2 class="md-h2">$1</h2>')
  html = html.replace(/^#\s+(.+)$/gm, '<h1 class="md-h1">$1</h1>')

  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/`([^`]+)`/g, '<code class="md-code">$1</code>')

  html = html.replace(/^[-*+]\s+(.+)$/gm, '<li class="md-li">$1</li>')
  html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<li class="md-li md-li-num"><span class="md-num">$1.</span> $2</li>')
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, (match) => {
    return `<ul class="md-ul">${match}</ul>`
  })

  html = html.replace(/^>\s+(.+)$/gm, '<blockquote class="md-quote">$1</blockquote>')
  html = html.replace(/^---\s*$/gm, '<hr class="md-hr" />')
  html = html.replace(/\n{2,}/g, '</p><p class="md-p">')
  html = html.replace(/\n/g, '<br/>')

  if (!html.startsWith('<h') && !html.startsWith('<ul') && !html.startsWith('<blockquote') && !html.startsWith('<p')) {
    html = '<p class="md-p">' + html + '</p>'
  }
  return html
}

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return String(num).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const getLogTagType = (operation) => {
  const map = { '登录': 'success', '新增': 'primary', '修改': 'warning', '删除': 'danger', '查询': 'info', '导出': 'info' }
  return map[operation] || 'info'
}

const isSuccessStatus = (status) => {
  if (!status) return false
  const successValues = ['成功', 'success', 'SUCCESS', 1, '1', true]
  return successValues.includes(status)
}

const loadSummary = async () => {
  const res = await getLogAnalysisSummary()
  if (res && res.data) {
    summary.value = {
      total_request: Number(res.data.total_request || 0),
      success_request: Number(res.data.success_request || 0),
      failed_request: Number(res.data.failed_request || 0),
      avg_response_time: Number(res.data.avg_response_time || 0),
      total_login: Number(res.data.total_login || 0),
      success_login: Number(res.data.success_login || 0),
      failed_login: Number(res.data.failed_login || 0)
    }
    if (Array.isArray(res.data.recent_logs) && res.data.recent_logs.length > 0) {
      recentLogs.value = res.data.recent_logs.map(log => ({
        logTime: log.log_time || log.logTime || log.oper_time || log.create_time || new Date().toLocaleString(),
        operation: log.operation || '操作',
        module: log.module || '系统模块',
        userName: log.user_name || log.userName || 'admin',
        status: log.status || (log.success === 1 ? '成功' : '失败'),
        message: log.message || log.remark || log.operation || '操作记录'
      }))
    }
  }
}

const loadTrend = async () => {
  const res = await getLogTrend()
  if (res && res.data && Array.isArray(res.data)) {
    trendData.value = res.data
  }
  renderTrendChart()
}

const loadTypeDistribution = async () => {
  const res = await getLogTypeDistribution()
  if (res && res.data && Array.isArray(res.data)) {
    typeData.value = res.data
  }
  renderTypeChart()
}

const loadLoginStats = async () => {
  const res = await getLogLoginStats()
  if (res && res.data && Array.isArray(res.data)) {
    loginData.value = res.data
  }
  renderLoginChart()
}

const renderTrendChart = () => {
  if (!trendChart) return
  const dates = trendData.value.map(d => d.date)
  const total = trendData.value.map(d => Number(d.total || 0))
  const success = trendData.value.map(d => Number(d.success || 0))
  const failed = trendData.value.map(d => Number(d.failed || 0))

  trendChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['总请求', '成功', '失败'], top: 0 },
    grid: { top: 50, left: 60, right: 30, bottom: 50 },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    series: [
      {
        name: '总请求',
        type: 'line',
        smooth: true,
        data: total,
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64,158,255,0.3)' },
            { offset: 1, color: 'rgba(64,158,255,0.02)' }
          ])
        }
      },
      { name: '成功', type: 'line', smooth: true, data: success, itemStyle: { color: '#67C23A' }, lineStyle: { width: 2 } },
      { name: '失败', type: 'line', smooth: true, data: failed, itemStyle: { color: '#F56C6C' }, lineStyle: { width: 2 } }
    ]
  })
}

const renderTypeChart = () => {
  if (!typeChart) return
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#95D475', '#8e44ad', '#16a085']
  const chartData = (typeData.value || []).map((item, idx) => ({
    name: item.title || item.type || item.business_type || item.module || '其他',
    value: Number(item.count || item.value || 0),
    itemStyle: { color: colors[idx % colors.length] }
  }))

  typeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 5, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      label: { show: true, formatter: '{b}\n{c} ({d}%)' },
      data: chartData,
      emphasis: {
        itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' }
      }
    }]
  })
}

const renderLoginChart = () => {
  if (!loginChart) return
  const dates = loginData.value.map(d => d.date)
  const success = loginData.value.map(d => Number(d.success_count || 0))
  const fail = loginData.value.map(d => Number(d.fail_count || 0))

  loginChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['登录成功', '登录失败'], top: 0 },
    grid: { top: 50, left: 60, right: 30, bottom: 50 },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    series: [
      { name: '登录成功', type: 'bar', data: success, itemStyle: { color: '#67C23A' }, barMaxWidth: 40 },
      { name: '登录失败', type: 'bar', data: fail, itemStyle: { color: '#F56C6C' }, barMaxWidth: 40 }
    ]
  })
}

const extractAnalysisContent = (res) => {
  if (!res) return '分析完成'
  if (typeof res === 'string') return res
  if (res.data) {
    if (typeof res.data === 'string') return res.data
    if (res.data.analysis) return res.data.analysis
    if (res.data.message) return res.data.message
    if (res.data.content) return res.data.content
    if (res.data.result) return res.data.result
  }
  if (res.analysis) return res.analysis
  if (res.message) return res.message
  if (res.content) return res.content
  return 'AI 分析完成'
}

// ============ 单项分析函数 ============

const analyzeTrend = async () => {
  analyzing.trend = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '请求趋势 AI 分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'trend'
  try {
    const forAI = (trendData.value || []).map(d => ({
      日期: d.date, 总请求: d.total, 成功: d.success, 失败: d.failed
    }))
    const res = await aiAnalyze({
      dataType: 'log-analysis-trend',
      dataSummary: {
        汇总: summary.value,
        近7天趋势: forAI
      },
      userQuestion: `请作为专业的系统运维分析师，基于以下系统近7天的请求趋势数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **数据概览**：总请求、成功请求、失败请求、成功率等关键指标
2. **趋势分析**：请求量峰值和低谷日期、可能的影响因素
3. **波动分析**：请求量稳定性、是否存在异常波动
4. **优化建议**：系统性能优化、监控告警等建议

## 输出要求
- 使用 Markdown 格式输出
- 用 **粗体** 强调关键数据和指标
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })
    aiResultDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error(e)
    aiResultDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.trend = false
    aiLoading.value = false
  }
}

const analyzeTypes = async () => {
  analyzing.types = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '请求类型分布 AI 分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'types'
  try {
    const forAI = (typeData.value || []).map(d => ({
      类型: d.title || d.type || d.business_type || d.module,
      请求数: d.count || d.value
    }))
    const analyzeRes = await aiAnalyze({
      dataType: 'log-type-distribution',
      dataSummary: forAI,
      userQuestion: `请作为专业的系统运维分析师，基于以下请求类型分布数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **高频类型识别**：最频繁的操作类型及其占比
2. **使用习惯分析**：请求类型分布反映的用户使用习惯和工作模式
3. **性能与安全评估**：性能瓶颈、资源消耗、安全风险
4. **优化建议**：接口优化、数据库优化、安全策略等

## 输出要求
- 使用 Markdown 格式输出
- 可使用表格展示请求类型分布
- 用 **粗体** 强调关键数据和建议
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })
    aiResultDialog.content = extractAnalysisContent(analyzeRes)
  } catch (e) {
    console.error(e)
    aiResultDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.types = false
    aiLoading.value = false
  }
}

const analyzeLogin = async () => {
  analyzing.login = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '登录情况 AI 分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'login'
  try {
    const forAI = (loginData.value || []).map(d => ({
      日期: d.date,
      成功次数: d.success_count,
      失败次数: d.fail_count,
      成功率: (d.success_count && (d.success_count + d.fail_count))
        ? (((d.success_count / (d.success_count + d.fail_count)) * 100).toFixed(2) + '%')
        : '0.00%'
    }))
    const totalSuccess = loginData.value.reduce((s, d) => s + Number(d.success_count || 0), 0)
    const totalFail = loginData.value.reduce((s, d) => s + Number(d.fail_count || 0), 0)
    const overallRate = (totalSuccess + totalFail) > 0 ? (((totalSuccess / (totalSuccess + totalFail)) * 100).toFixed(2) + '%') : '0.00%'
    const loginRes = await aiAnalyze({
      dataType: 'log-login-stats',
      dataSummary: {
        近7天登录汇总: {
          总登录数: totalSuccess + totalFail,
          总成功登录: totalSuccess,
          总失败登录: totalFail,
          整体成功率: overallRate
        },
        每日登录明细: forAI
      },
      userQuestion: `请作为专业的系统安全分析师，基于以下登录情况数据，生成一份安全评估和分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **登录成功率分析**：整体登录成功率、是否存在异常
2. **失败高峰识别**：失败率异常高的日期、可能原因
3. **登录趋势**：登录量变化趋势、突增或骤降的影响
4. **安全风险评估**：是否存在暴力破解特征、异常登录等风险
5. **优化建议**：提升登录体验和安全性的建议

## 输出要求
- 使用 Markdown 格式输出
- 可使用表格展示每日登录数据
- 用 **粗体** 强调关键指标和风险点
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })
    aiResultDialog.content = extractAnalysisContent(loginRes)
  } catch (e) {
    console.error(e)
    aiResultDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.login = false
    aiLoading.value = false
  }
}

// ============ 整体分析函数 ============

const analyzeOverall = async () => {
  analyzing.overall = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '系统日志 AI 整体分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'overall'
  try {
    // 汇总所有数据
    const trendForAI = (trendData.value || []).map(d => ({
      日期: d.date, 总请求: d.total, 成功: d.success, 失败: d.failed
    }))

    const typeForAI = (typeData.value || []).map(d => ({
      类型: d.title || d.type || d.business_type || d.module,
      请求数: d.count || d.value
    }))

    const totalLoginSuccess = loginData.value.reduce((s, d) => s + Number(d.success_count || 0), 0)
    const totalLoginFail = loginData.value.reduce((s, d) => s + Number(d.fail_count || 0), 0)
    const loginOverallRate = (totalLoginSuccess + totalLoginFail) > 0
      ? (((totalLoginSuccess / (totalLoginSuccess + totalLoginFail)) * 100).toFixed(2) + '%')
      : '0.00%'

    const loginForAI = (loginData.value || []).map(d => ({
      日期: d.date,
      成功次数: d.success_count,
      失败次数: d.fail_count,
      成功率: (d.success_count && (d.success_count + d.fail_count))
        ? (((d.success_count / (d.success_count + d.fail_count)) * 100).toFixed(2) + '%')
        : '0.00%'
    }))

    const res = await aiAnalyze({
      dataType: 'log-analysis-overall',
      dataSummary: {
        系统指标汇总: summary.value,
        近7天请求趋势: trendForAI,
        请求类型分布: typeForAI,
        登录情况汇总: {
          总登录数: totalLoginSuccess + totalLoginFail,
          总成功登录: totalLoginSuccess,
          总失败登录: totalLoginFail,
          整体成功率: loginOverallRate
        },
        每日登录明细: loginForAI
      },
      userQuestion: `请作为资深的系统安全和运维分析师，基于以下系统的完整日志数据，生成一份全面深入的运行分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **执行摘要**：系统整体运行状况、关键指标、健康度评估
2. **请求趋势分析**：请求量变化趋势、峰值低谷日期及原因
3. **类型分布分析**：高频操作类型、用户使用习惯、性能瓶颈
4. **登录安全分析**：登录成功率、异常失败率、安全风险
5. **关键发现与风险**：重要发现、潜在安全和运维风险
6. **综合建议**：安全加固、性能优化、监控告警等建议

## 输出要求
- 使用 Markdown 格式输出
- 可用表格呈现关键数据对比
- 用 **粗体** 强调关键指标和风险点
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })
    aiResultDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error(e)
    aiResultDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.overall = false
    aiLoading.value = false
  }
}

// ============ 导出与辅助函数 ============

const copyAnalysis = async () => {
  if (!aiResultDialog.content) return
  try {
    await navigator.clipboard.writeText(aiResultDialog.content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (e) {
    const textarea = document.createElement('textarea')
    textarea.value = aiResultDialog.content
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('内容已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

const exportAsMarkdown = () => {
  if (!aiResultDialog.content) return
  const content = `# ${aiResultDialog.title}

> 生成时间：${currentTimeStr.value}
> 数据来源：系统日志实时数据

---

${aiResultDialog.content}

---

*本报告由 AI 智能分析系统自动生成*`

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const fileName = `系统日志分析报告_${Date.now()}.md`
  triggerDownload(blob, fileName)
  ElMessage.success('Markdown 文件已下载')
}

const exportAsText = () => {
  if (!aiResultDialog.content) return
  const textContent = aiResultDialog.content
    .replace(/[#*`>]/g, '')
    .replace(/---/g, '========================================')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, '')

  const content = `${'='.repeat(60)}
${aiResultDialog.title}
${'='.repeat(60)}

生成时间：${currentTimeStr.value}
数据来源：系统日志实时数据

${'-'.repeat(60)}

${textContent}

${'-'.repeat(60)}
本报告由 AI 智能分析系统自动生成
${'='.repeat(60)}`

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const fileName = `系统日志分析报告_${Date.now()}.txt`
  triggerDownload(blob, fileName)
  ElMessage.success('TXT 文件已下载')
}

const printAnalysis = () => {
  if (!aiResultDialog.content) return
  const printWindow = window.open('', '_blank', 'width=900,height=700')
  if (!printWindow) {
    ElMessage.warning('无法打开打印窗口，请检查浏览器设置')
    return
  }
  printWindow.document.write(`
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <title>${aiResultDialog.title}</title>
      <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; padding: 30px; line-height: 1.8; color: #303133; }
        h1 { color: #409EFF; border-bottom: 3px solid #409EFF; padding-bottom: 10px; }
        h2 { color: #67C23A; border-left: 4px solid #67C23A; padding-left: 12px; margin-top: 25px; }
        h3 { color: #E6A23C; margin-top: 20px; }
        strong { color: #F56C6C; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ebeef5; padding: 8px 12px; text-align: left; }
        th { background: #f5f7fa; font-weight: bold; }
        ul, ol { padding-left: 25px; }
        li { margin: 6px 0; }
        blockquote { border-left: 4px solid #909399; padding-left: 15px; color: #606266; margin: 15px 0; }
        code { background: #f5f7fa; padding: 2px 6px; border-radius: 3px; color: #F56C6C; font-family: monospace; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%); border-radius: 8px; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ebeef5; color: #909399; font-size: 12px; }
        @media print { body { padding: 15px; } }
      </style>
    </head>
    <body>
      <div class="header">
        <h1 style="border:none; margin:0;">${aiResultDialog.title}</h1>
        <p style="margin: 10px 0 0 0; color: #606266;">生成时间：${currentTimeStr.value}</p>
      </div>
      <div style="padding: 10px 20px;">${renderedMarkdown.value}</div>
      <div class="footer">本报告由 AI 智能分析系统自动生成</div>
      <script>window.onload = function() { setTimeout(function() { window.print(); }, 500); }<\/script>
    </body>
    </html>
  `)
  printWindow.document.close()
}

const triggerDownload = (blob, fileName) => {
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  setTimeout(() => URL.revokeObjectURL(url), 100)
}

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['总请求', '成功', '失败'] },
      grid: { top: 40, left: 50, right: 30, bottom: 30 },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [
        { name: '总请求', type: 'line', smooth: true, data: [] },
        { name: '成功', type: 'line', smooth: true, data: [] },
        { name: '失败', type: 'line', smooth: true, data: [] }
      ]
    })
  }
  if (typeChartRef.value) {
    typeChart = echarts.init(typeChartRef.value)
    typeChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 5 },
      series: [{ type: 'pie', radius: ['35%', '65%'], data: [] }]
    })
  }
  if (loginChartRef.value) {
    loginChart = echarts.init(loginChartRef.value)
    loginChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['登录成功', '登录失败'] },
      grid: { top: 40, left: 50, right: 30, bottom: 30 },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [
        { name: '登录成功', type: 'bar', data: [] },
        { name: '登录失败', type: 'bar', data: [] }
      ]
    })
  }
}

const handleResize = () => {
  trendChart && trendChart.resize()
  typeChart && typeChart.resize()
  loginChart && loginChart.resize()
}

onMounted(async () => {
  initCharts()
  loading.value = true
  try {
    await Promise.all([loadSummary(), loadTrend(), loadTypeDistribution(), loadLoginStats()])
  } catch (e) {
    console.error('加载数据失败:', e)
  } finally {
    loading.value = false
  }
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart && trendChart.dispose()
  typeChart && typeChart.dispose()
  loginChart && loginChart.dispose()
})
</script>

<style scoped>
.log-analysis {
  padding: 20px;
}

/* 整体分析卡片 */
.row-overall {
  margin-bottom: 20px;
}

.overall-card {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 50%, #f0f9eb 100%);
  border: none;
}

.overall-card :deep(.el-card__body) {
  padding: 20px 25px;
}

.overall-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.overall-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.overall-info {
  display: flex;
  flex-direction: column;
}

.overall-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.overall-sub {
  font-size: 13px;
  color: #606266;
}

.overall-btn {
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  padding: 0 28px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35);
}

.overall-btn:hover {
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5);
}

.summary-row {
  margin-bottom: 0;
}

.chart-row {
  margin-top: 20px;
}

.table-row {
  margin-top: 20px;
}

.stat-card {
  height: 140px;
  padding: 12px;
  box-sizing: border-box;
}

.stat-card :deep(.el-card__body) {
  height: 100%;
  padding: 12px;
}

.card-inner {
  display: flex;
  align-items: center;
  height: 100%;
}

.icon-box {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.icon-blue {
  background: linear-gradient(135deg, #ecf5ff 0%, #b3d8ff 100%);
  color: #409EFF;
}

.icon-green {
  background: linear-gradient(135deg, #f0f9eb 0%, #c2e7b0 100%);
  color: #67C23A;
}

.icon-red {
  background: linear-gradient(135deg, #fef0f0 0%, #fbc4c4 100%);
  color: #F56C6C;
}

.icon-orange {
  background: linear-gradient(135deg, #fdf6ec 0%, #f5dab1 100%);
  color: #E6A23C;
}

.text-box {
  flex: 1;
  min-width: 0;
}

.text-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 6px;
  font-weight: 500;
}

.text-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1.25;
  white-space: nowrap;
}

.text-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-success {
  color: #67C23A;
}

.text-danger {
  color: #F56C6C;
}

.text-warning {
  color: #E6A23C;
}

.chart-box {
  width: 100%;
  height: 380px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* AI 分析对话框 */
.ai-content {
  padding: 5px 0;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.ai-header-text {
  flex: 1;
}

.ai-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 3px;
}

.ai-subtitle {
  font-size: 12px;
  color: #909399;
}

/* 工具栏 */
.ai-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

/* AI 内容区 */
.ai-body {
  min-height: 400px;
  max-height: 560px;
  overflow-y: auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.ai-body.ai-loading {
  min-height: 300px;
}

/* Markdown 内容样式 */
.ai-markdown-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.9;
}

.ai-markdown-content :deep(.md-h1) {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
  text-align: center;
  padding: 20px 0;
  margin: 0 0 25px 0;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  border-radius: 8px;
}

.ai-markdown-content :deep(.md-h2) {
  font-size: 18px;
  font-weight: 700;
  color: #67C23A;
  padding-left: 14px;
  border-left: 4px solid #67C23A;
  margin: 30px 0 15px 0;
}

.ai-markdown-content :deep(.md-h3) {
  font-size: 15px;
  font-weight: 700;
  color: #E6A23C;
  margin: 20px 0 10px 0;
}

.ai-markdown-content :deep(.md-h4),
.ai-markdown-content :deep(.md-h5),
.ai-markdown-content :deep(.md-h6) {
  font-size: 14px;
  font-weight: 600;
  color: #909399;
  margin: 15px 0 8px 0;
}

.ai-markdown-content :deep(.md-p) {
  margin: 12px 0;
  text-align: justify;
}

.ai-markdown-content :deep(strong) {
  color: #F56C6C;
  font-weight: 700;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 3px;
}

.ai-markdown-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.ai-markdown-content :deep(.md-code) {
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #F56C6C;
  border: 1px solid #e4e7ed;
}

.ai-markdown-content :deep(.md-ul) {
  padding-left: 24px;
  margin: 12px 0;
}

.ai-markdown-content :deep(.md-li) {
  margin: 8px 0;
  line-height: 1.8;
  list-style-type: disc;
}

.ai-markdown-content :deep(.md-li.md-li-num) {
  list-style-type: none;
}

.ai-markdown-content :deep(.md-num) {
  display: inline-block;
  min-width: 25px;
  font-weight: 700;
  color: #409EFF;
}

.ai-markdown-content :deep(.md-quote) {
  padding: 12px 18px;
  margin: 15px 0;
  background: #f5f7fa;
  border-left: 4px solid #909399;
  border-radius: 4px;
  color: #606266;
}

.ai-markdown-content :deep(.md-hr) {
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, #dcdfe6, transparent);
  margin: 25px 0;
}

/* 滚动条样式 */
.ai-body::-webkit-scrollbar {
  width: 8px;
}

.ai-body::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 4px;
}

.ai-body::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.ai-body::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>

<template>
  <div class="income-expense">
    <!-- 顶部整体分析按钮 -->
    <el-row :gutter="20" class="row-overall">
      <el-col :span="24">
        <el-card shadow="hover" class="overall-card">
          <div class="overall-inner">
            <div class="overall-left">
              <el-icon :size="32" color="#409EFF"><MagicStick /></el-icon>
              <div class="overall-info">
                <div class="overall-title">收支数据智能分析</div>
                <div class="overall-sub">整合收支趋势、分类分布、支付方式，一键生成全面的财务数据分析报告</div>
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

    <!-- 第一行：4 个统计卡片 -->
    <el-row :gutter="20" class="row-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-blue">
              <el-icon :size="28"><Wallet /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">总收入</div>
              <div class="text-value">¥ {{ formatNumber(summary.total_income) }}</div>
              <div class="text-sub">共 {{ formatNumber(summary.income_count) }} 笔收入</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-green">
              <el-icon :size="28"><Wallet /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">总支出</div>
              <div class="text-value">¥ {{ formatNumber(summary.total_expense) }}</div>
              <div class="text-sub">共 {{ formatNumber(summary.expense_count) }} 笔支出</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-orange">
              <el-icon :size="28"><TrendCharts /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">利润</div>
              <div class="text-value" :style="{ color: summary.profit >= 0 ? '#67C23A' : '#F56C6C' }">
                ¥ {{ formatNumber(summary.profit) }}
              </div>
              <div class="text-sub">{{ summary.profit >= 0 ? '盈利' : '亏损' }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-red">
              <el-icon :size="28"><DataLine /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">收支笔数</div>
              <div class="text-value">{{ formatNumber((summary.income_count || 0) + (summary.expense_count || 0)) }}</div>
              <div class="text-sub">收入 {{ formatNumber(summary.income_count) }} / 支出 {{ formatNumber(summary.expense_count) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：近30天每日收支趋势 -->
    <el-row :gutter="20" class="row-charts">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><TrendCharts /></el-icon>
                <span>&nbsp;近 30 天每日收支趋势</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeTrend" :loading="analyzing.trend">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：分类分布 + 支付方式分布 -->
    <el-row :gutter="20" class="row-charts">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><DataAnalysis /></el-icon>
                <span>&nbsp;收支分类分布</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeCategory" :loading="analyzing.category">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="categoryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Wallet /></el-icon>
                <span>&nbsp;支付方式分布</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeTopRecords" :loading="analyzing.topRecords">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="paymentChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI 分析结果弹窗 -->
    <el-dialog
      v-model="aiDialog.visible"
      :title="aiDialog.title"
      width="780px"
      top="5vh"
      :close-on-click-modal="false">
      <div class="ai-dialog">
        <div class="ai-header">
          <el-icon :size="36" color="#409EFF"><MagicStick /></el-icon>
          <div class="ai-header-text">
            <div class="ai-title">AI 智能分析报告</div>
            <div class="ai-subtitle">基于实时数据分析 · {{ currentTimeStr }}</div>
          </div>
          <div class="ai-header-tag">
            <el-tag :type="aiDialog.dataType === 'income-expense-overall' ? 'danger' : 'primary'" size="small">
              {{ aiDialog.dataType === 'income-expense-overall' ? '整体分析' : '单项分析' }}
            </el-tag>
          </div>
        </div>

        <div class="ai-toolbar" v-if="aiDialog.content && !aiLoading">
          <el-button size="small" @click="copyAnalysis">
            <el-icon><Document /></el-icon>
            <span>&nbsp;复制内容</span>
          </el-button>
          <el-button size="small" type="success" @click="exportAsMarkdown">
            <el-icon><Download /></el-icon>
            <span>&nbsp;导出 Markdown</span>
          </el-button>
          <el-button size="small" type="info" @click="printAnalysis">
            <el-icon><Printer /></el-icon>
            <span>&nbsp;打印报告</span>
          </el-button>
        </div>

        <div class="ai-body" :class="{ 'ai-loading': aiLoading }" v-loading="aiLoading">
          <div v-if="aiDialog.content" class="markdown-content" v-html="renderedMarkdown"></div>
          <el-empty v-else-if="!aiLoading" description="暂无分析结果，请点击 AI 分析按钮生成报告" />
        </div>
      </div>
      <template #footer>
        <el-button @click="aiDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import {
  MagicStick, Wallet, TrendCharts, DataLine, DataAnalysis,
  Document, Download, Printer
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getIncomeExpenseSummary,
  getIncomeExpenseTrend,
  getIncomeExpenseTopRecords
} from '@/api/visualization'
import { aiAnalyze } from '@/api/ai'

const loading = ref(false)
const aiLoading = ref(false)

const summary = ref({
  total_income: 0,
  total_expense: 0,
  profit: 0,
  income_count: 0,
  expense_count: 0
})

const categoryData = ref([])
const trendData = ref([])
const paymentData = ref([])
const topRecordsData = ref([])

const trendChartRef = ref(null)
const categoryChartRef = ref(null)
const paymentChartRef = ref(null)

let trendChart = null
let categoryChart = null
let paymentChart = null

const analyzing = reactive({
  trend: false,
  category: false,
  topRecords: false,
  overall: false
})

const aiDialog = reactive({
  visible: false,
  title: 'AI 智能分析',
  content: '',
  dataType: ''
})

const currentTimeStr = computed(() => {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`
})

const renderedMarkdown = computed(() => {
  if (!aiDialog.content) return ''
  return renderMarkdown(aiDialog.content)
})

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
  if (num === null || num === undefined || num === '') return '0'
  const n = Number(num)
  if (Number.isNaN(n)) return '0'
  return String(Math.round(n * 100) / 100).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const loadSummary = async () => {
  try {
    const res = await getIncomeExpenseSummary()
    const data = res && res.data
    if (data) {
      summary.value = {
        total_income: data.total_income ?? 0,
        total_expense: data.total_expense ?? 0,
        profit: data.profit ?? 0,
        income_count: data.income_count ?? 0,
        expense_count: data.expense_count ?? 0
      }
      if (Array.isArray(data.category_distribution)) {
        categoryData.value = data.category_distribution
      }
      if (Array.isArray(data.daily_trend)) {
        trendData.value = data.daily_trend
      }
      if (Array.isArray(data.payment_method_distribution)) {
        paymentData.value = data.payment_method_distribution
      }
      if (Array.isArray(data.top_records)) {
        topRecordsData.value = data.top_records
      }
    }
  } catch (e) {
    console.error('加载收支汇总失败:', e)
  }
}

const loadTrend = async () => {
  try {
    const res = await getIncomeExpenseTrend()
    const data = res && res.data
    if (Array.isArray(data)) {
      trendData.value = data
    }
  } catch (e) {
    console.error('加载收支趋势失败:', e)
  }
}

const loadTopRecords = async () => {
  try {
    const res = await getIncomeExpenseTopRecords()
    const data = res && res.data
    if (Array.isArray(data)) {
      topRecordsData.value = data
    }
  } catch (e) {
    console.error('加载大额收支失败:', e)
  }
}

const renderTrendChart = () => {
  if (!trendChart) return
  const data = trendData.value || []
  const dates = data.map(d => d.date)
  const incomes = data.map(d => Number(d.income || 0))
  const expenses = data.map(d => Number(d.expense || 0))
  const profits = data.map(d => Number(d.profit || 0))

  trendChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['收入', '支出', '利润'],
      top: 0
    },
    grid: {
      top: 50,
      left: 70,
      right: 70,
      bottom: 80
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val) => {
          if (Math.abs(val) >= 10000) return (val / 10000).toFixed(1) + '万'
          return val
        }
      }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        data: incomes,
        smooth: true,
        itemStyle: { color: '#67C23A' },
        lineStyle: { width: 3 },
        symbolSize: 8,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103,194,58,0.35)' },
            { offset: 1, color: 'rgba(103,194,58,0.05)' }
          ])
        }
      },
      {
        name: '支出',
        type: 'line',
        data: expenses,
        smooth: true,
        itemStyle: { color: '#F56C6C' },
        lineStyle: { width: 3 },
        symbolSize: 8,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245,108,108,0.3)' },
            { offset: 1, color: 'rgba(245,108,108,0.05)' }
          ])
        }
      },
      {
        name: '利润',
        type: 'line',
        data: profits,
        smooth: true,
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 3, type: 'solid' },
        symbolSize: 8
      }
    ]
  })
}

const renderCategoryChart = () => {
  if (!categoryChart) return
  const data = categoryData.value || []

  const incomeData = data
    .filter(d => d.record_type === 'income' || d.record_type === '收入')
    .map(d => ({ name: d.category, value: Number(d.total_amount || 0) }))

  const expenseData = data
    .filter(d => d.record_type === 'expense' || d.record_type === '支出')
    .map(d => ({ name: d.category, value: Number(d.total_amount || 0) }))

  categoryChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 20,
      top: 'center'
    },
    title: [
      { text: '收入', left: '18%', top: '48%', textStyle: { fontSize: 14, color: '#606266' } },
      { text: '支出', left: '68%', top: '48%', textStyle: { fontSize: 14, color: '#606266' } }
    ],
    series: [
      {
        name: '收入分类',
        type: 'pie',
        radius: ['35%', '55%'],
        center: ['20%', '50%'],
        avoidLabelOverlap: true,
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 13, fontWeight: 'bold' }
        },
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        data: incomeData.length > 0 ? incomeData : [{ name: '暂无数据', value: 0 }]
      },
      {
        name: '支出分类',
        type: 'pie',
        radius: ['35%', '55%'],
        center: ['70%', '50%'],
        avoidLabelOverlap: true,
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 13, fontWeight: 'bold' }
        },
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        data: expenseData.length > 0 ? expenseData : [{ name: '暂无数据', value: 0 }]
      }
    ]
  })
}

const renderPaymentChart = () => {
  if (!paymentChart) return
  const data = paymentData.value || []
  const pieData = data.map(d => ({
    name: d.payment_method || '其他',
    value: Number(d.total_amount || 0)
  }))

  paymentChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 20,
      top: 'center'
    },
    series: [
      {
        name: '支付方式',
        type: 'pie',
        radius: ['35%', '65%'],
        center: ['45%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n¥{c}'
        },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' }
        },
        data: pieData.length > 0 ? pieData : [{ name: '暂无数据', value: 0 }]
      }
    ]
  })
}

const initCharts = () => {
  if (trendChartRef.value) trendChart = echarts.init(trendChartRef.value)
  if (categoryChartRef.value) categoryChart = echarts.init(categoryChartRef.value)
  if (paymentChartRef.value) paymentChart = echarts.init(paymentChartRef.value)
}

const handleResize = () => {
  trendChart && trendChart.resize()
  categoryChart && categoryChart.resize()
  paymentChart && paymentChart.resize()
}

const openAiDialog = (title, dataType = '') => {
  aiDialog.visible = true
  aiDialog.title = title
  aiDialog.content = ''
  aiDialog.dataType = dataType
  aiLoading.value = true
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
  openAiDialog('收支趋势 AI 分析报告', 'income-expense-trend')
  try {
    const trendForAI = trendData.value.map(d => ({
      日期: d.date,
      收入: d.income,
      支出: d.expense,
      利润: d.profit
    }))

    const res = await aiAnalyze({
      dataType: 'income-expense-trend',
      dataSummary: {
        总体指标: {
          总收入: summary.value.total_income,
          总支出: summary.value.total_expense,
          利润: summary.value.profit,
          收入笔数: summary.value.income_count,
          支出笔数: summary.value.expense_count
        },
        '近30天每日趋势': trendForAI
      },
      userQuestion: `请作为专业的财务分析师，基于以下近30天的收支趋势数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **趋势概览**：整体收支趋势、峰值谷值日期及原因推测
2. **收支对比**：收入与支出的平衡情况、利润变化分析
3. **周期性分析**：是否存在明显的周/月周期性规律
4. **优化建议**：基于趋势给出具体可行的财务建议

## 输出要求
- 使用 Markdown 格式输出
- 用 **粗体** 强调关键数据和发现
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析收支趋势失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.trend = false
    aiLoading.value = false
  }
}

const analyzeCategory = async () => {
  analyzing.category = true
  openAiDialog('收支分类分布 AI 分析报告', 'income-expense-category')
  try {
    const categoryForAI = categoryData.value.map(d => ({
      分类: d.category,
      类型: d.record_type,
      总金额: d.total_amount,
      记录数: d.record_count
    }))

    const res = await aiAnalyze({
      dataType: 'income-expense-category',
      dataSummary: {
        总体指标: {
          总收入: summary.value.total_income,
          总支出: summary.value.total_expense,
          利润: summary.value.profit
        },
        分类分布: categoryForAI
      },
      userQuestion: `请作为专业的财务分析师，基于以下收支分类分布数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **收入结构**：主要收入来源、收入多样性评估
2. **支出结构**：主要支出类别、支出合理性分析
3. **关键发现**：从分类数据中提炼的重要洞察
4. **优化建议**：收入拓展方向、支出控制建议等

## 输出要求
- 使用 Markdown 格式输出
- 可用表格呈现分类数据对比
- 用 **粗体** 强调关键分类和数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析收支分类失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.category = false
    aiLoading.value = false
  }
}

const analyzeTopRecords = async () => {
  analyzing.topRecords = true
  openAiDialog('大额收支 AI 分析报告', 'income-expense-top-records')
  try {
    const topForAI = (topRecordsData.value || []).slice(0, 10).map(d => ({
      类型: d.record_type,
      分类: d.category,
      金额: d.amount,
      支付方式: d.payment_method,
      描述: d.description,
      日期: d.record_date,
      操作员: d.operator
    }))

    const paymentForAI = paymentData.value.map(d => ({
      支付方式: d.payment_method,
      总金额: d.total_amount,
      记录数: d.record_count
    }))

    const res = await aiAnalyze({
      dataType: 'income-expense-top-records',
      dataSummary: {
        总体指标: {
          总收入: summary.value.total_income,
          总支出: summary.value.total_expense,
          利润: summary.value.profit
        },
        支付方式分布: paymentForAI,
        '大额收支 TOP 10': topForAI
      },
      userQuestion: `请作为专业的财务分析师，基于以下大额收支和支付方式数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **大额收支识别**：TOP 10 收入/支出的特点、涉及的主要分类
2. **支付方式分析**：主要支付渠道、渠道集中度、潜在优化点
3. **风险评估**：是否存在异常大额收支、需要关注的项目
4. **优化建议**：支付渠道管理、大额支出审批流程建议等

## 输出要求
- 使用 Markdown 格式输出
- 可用表格呈现 TOP 10 收支明细
- 用 **粗体** 强调关键项目和数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析大额收支失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.topRecords = false
    aiLoading.value = false
  }
}

// ============ 整体分析函数 ============

const analyzeOverall = async () => {
  analyzing.overall = true
  openAiDialog('收支数据 AI 整体分析报告', 'income-expense-overall')
  try {
    const trendForAI = trendData.value.map(d => ({
      日期: d.date, 收入: d.income, 支出: d.expense, 利润: d.profit
    }))

    const categoryForAI = categoryData.value.map(d => ({
      分类: d.category, 类型: d.record_type, 总金额: d.total_amount, 记录数: d.record_count
    }))

    const topForAI = (topRecordsData.value || []).slice(0, 10).map(d => ({
      类型: d.record_type, 分类: d.category, 金额: d.amount, 日期: d.record_date, 描述: d.description
    }))

    const res = await aiAnalyze({
      dataType: 'income-expense-overall',
      dataSummary: {
        总体指标: {
          总收入: summary.value.total_income,
          总支出: summary.value.total_expense,
          利润: summary.value.profit,
          收入笔数: summary.value.income_count,
          支出笔数: summary.value.expense_count
        },
        '近30天收支趋势': trendForAI,
        收支分类分布: categoryForAI,
        '大额收支 TOP 10': topForAI
      },
      userQuestion: `请作为专业的数据分析师和财务顾问，基于以下完整的收支数据，生成一份全面深入的财务数据分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **执行摘要**：整体财务状况总结、关键数据指标
2. **趋势分析**：收支趋势变化、峰值低谷、周期性规律
3. **收支结构分析**：收入来源、支出结构的合理性评估
4. **大额交易分析**：TOP 10 收支项目识别和风险评估
5. **关键发现**：从数据中提炼的重要洞察和财务风险
6. **综合建议**：具体可执行的优化建议（收入拓展、支出控制、财务管理等）

## 输出要求
- 使用 Markdown 格式输出
- 用 **粗体** 强调关键发现和数据
- 可用表格呈现数据对比
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('整体分析失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.overall = false
    aiLoading.value = false
  }
}

// ============ 导出与辅助函数 ============

const copyAnalysis = async () => {
  if (!aiDialog.content) return
  try {
    await navigator.clipboard.writeText(aiDialog.content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (e) {
    const textarea = document.createElement('textarea')
    textarea.value = aiDialog.content
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
  if (!aiDialog.content) return
  const content = `# ${aiDialog.title}

> 生成时间：${currentTimeStr.value}
> 数据来源：收支管理看板实时数据

---

${aiDialog.content}

---

*本报告由 AI 智能分析系统自动生成*`

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const fileName = `收支分析报告_${Date.now()}.md`
  triggerDownload(blob, fileName)
  ElMessage.success('Markdown 文件已下载')
}

const printAnalysis = () => {
  if (!aiDialog.content) return
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
      <title>${aiDialog.title}</title>
      <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; padding: 30px; line-height: 1.8; color: #303133; }
        h1 { color: #409EFF; border-bottom: 3px solid #409EFF; padding-bottom: 10px; }
        h2 { color: '#67C23A'; border-left: 4px solid #67C23A; padding-left: 12px; margin-top: 25px; }
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
        <h1 style="border:none; margin:0;">${aiDialog.title}</h1>
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

onMounted(() => {
  initCharts()
  loading.value = true
  Promise.all([
    loadSummary(),
    loadTrend(),
    loadTopRecords()
  ]).finally(() => {
    loading.value = false
    renderTrendChart()
    renderCategoryChart()
    renderPaymentChart()
  })
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart && trendChart.dispose()
  categoryChart && categoryChart.dispose()
  paymentChart && paymentChart.dispose()
})
</script>

<style scoped>
.income-expense {
  padding: 20px;
}

.row-overall {
  margin-bottom: 20px;
}

.overall-card {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 50%, #e1f3d8 100%);
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

.row-cards {
  margin-bottom: 24px;
}

.row-charts {
  margin-bottom: 24px;
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
  color: #ffffff;
}

.icon-blue {
  background: linear-gradient(135deg, #409EFF 0%, #1860B0 100%);
}

.icon-green {
  background: linear-gradient(135deg, #67C23A 0%, #2F8B2A 100%);
}

.icon-orange {
  background: linear-gradient(135deg, #E6A23C 0%, #B97E1A 100%);
}

.icon-red {
  background: linear-gradient(135deg, #F56C6C 0%, #B93A3A 100%);
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

.chart-container {
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
.ai-dialog {
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
.markdown-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.9;
}

.markdown-content :deep(.md-h1) {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
  text-align: center;
  padding: 20px 0;
  margin: 0 0 25px 0;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  border-radius: 8px;
}

.markdown-content :deep(.md-h2) {
  font-size: 18px;
  font-weight: 700;
  color: #67C23A;
  padding-left: 14px;
  border-left: 4px solid #67C23A;
  margin: 30px 0 15px 0;
}

.markdown-content :deep(.md-h3) {
  font-size: 15px;
  font-weight: 700;
  color: #E6A23C;
  margin: 20px 0 10px 0;
}

.markdown-content :deep(.md-h4),
.markdown-content :deep(.md-h5),
.markdown-content :deep(.md-h6) {
  font-size: 14px;
  font-weight: 600;
  color: #909399;
  margin: 15px 0 8px 0;
}

.markdown-content :deep(.md-p) {
  margin: 12px 0;
  text-align: justify;
}

.markdown-content :deep(strong) {
  color: #F56C6C;
  font-weight: 700;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 3px;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.markdown-content :deep(.md-code) {
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #F56C6C;
  border: 1px solid #e4e7ed;
}

.markdown-content :deep(.md-ul) {
  padding-left: 24px;
  margin: 12px 0;
}

.markdown-content :deep(.md-li) {
  margin: 8px 0;
  line-height: 1.8;
  list-style-type: disc;
}

.markdown-content :deep(.md-li.md-li-num) {
  list-style-type: none;
}

.markdown-content :deep(.md-num) {
  display: inline-block;
  min-width: 25px;
  font-weight: 700;
  color: #409EFF;
}

.markdown-content :deep(.md-quote) {
  padding: 12px 18px;
  margin: 15px 0;
  background: #f5f7fa;
  border-left: 4px solid #909399;
  border-radius: 4px;
  color: #606266;
}

.markdown-content :deep(.md-hr) {
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

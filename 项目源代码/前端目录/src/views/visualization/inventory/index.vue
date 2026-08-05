<template>
  <div class="inventory">
    <!-- 顶部整体分析按钮 -->
    <el-row :gutter="20" class="row-overall">
      <el-col :span="24">
        <el-card shadow="hover" class="overall-card">
          <div class="overall-inner">
            <div class="overall-left">
              <el-icon :size="32" color="#409EFF"><MagicStick /></el-icon>
              <div class="overall-info">
                <div class="overall-title">库存数据智能分析</div>
                <div class="overall-sub">整合库存分类、高价值物品、低库存预警数据，一键生成全面的库存数据分析报告</div>
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
              <el-icon :size="28"><Box /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">物品总数</div>
              <div class="text-value">{{ formatNumber(summary.total_items) }}</div>
              <div class="text-sub">累计物品 {{ formatNumber(summary.total_items) }} 种</div>
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
              <div class="text-label">库存总价值</div>
              <div class="text-value">¥ {{ formatNumber(summary.total_value) }}</div>
              <div class="text-sub">累计价值 ¥ {{ formatNumber(summary.total_value) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-orange">
              <el-icon :size="28"><Warning /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">低库存物品</div>
              <div class="text-value">{{ formatNumber(summary.low_stock_count) }}</div>
              <div class="text-sub">需要补货的物品</div>
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
              <div class="text-label">分类数</div>
              <div class="text-value">{{ formatNumber(summary.category_count) }}</div>
              <div class="text-sub">库存分类数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：分类分布 + TOP 10 高价值物品 -->
    <el-row :gutter="20" class="row-charts">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><DataAnalysis /></el-icon>
                <span>&nbsp;库存分类分布</span>
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
                <span>&nbsp;TOP 10 高价值物品</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeTopItems" :loading="analyzing.topItems">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="topItemsChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：库存状态预警（表格 + 柱状图） -->
    <el-row :gutter="20" class="row-charts">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Warning /></el-icon>
                <span>&nbsp;库存状态预警</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeLowStock" :loading="analyzing.lowStock">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="12">
              <div ref="statusChartRef" class="chart-container" style="height: 400px;"></div>
            </el-col>
            <el-col :span="12">
              <el-table :data="lowStockItems" border stripe height="400">
                <el-table-column type="index" label="#" width="60" />
                <el-table-column prop="item_name" label="物品名称" min-width="160" />
                <el-table-column prop="category" label="分类" width="120" />
                <el-table-column prop="quantity" label="当前数量" width="110">
                  <template #default="scope">
                    <span :style="{ color: scope.row.quantity <= 5 ? '#F56C6C' : '#E6A23C', fontWeight: 'bold' }">
                      {{ scope.row.quantity }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="min_quantity" label="最低库存" width="100" />
                <el-table-column prop="location" label="存放位置" width="120" />
              </el-table>
            </el-col>
          </el-row>
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
            <el-tag :type="aiDialog.dataType === 'inventory-overall' ? 'danger' : 'primary'" size="small">
              {{ aiDialog.dataType === 'inventory-overall' ? '整体分析' : '单项分析' }}
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
  MagicStick, Box, Wallet, Warning, DataLine, DataAnalysis,
  Document, Download, Printer
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getInventorySummary,
  getInventoryCategory,
  getInventoryTopItems
} from '@/api/visualization'
import { aiAnalyze } from '@/api/ai'

const loading = ref(false)
const aiLoading = ref(false)

const summary = ref({
  total_items: 0,
  total_value: 0,
  low_stock_count: 0,
  category_count: 0
})

const categoryData = ref([])
const topItemsData = ref([])
const statusData = ref([])
const lowStockItems = ref([])

const categoryChartRef = ref(null)
const topItemsChartRef = ref(null)
const statusChartRef = ref(null)

let categoryChart = null
let topItemsChart = null
let statusChart = null

const analyzing = reactive({
  category: false,
  topItems: false,
  lowStock: false,
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

// 轻量级 Markdown 渲染函数
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
    const res = await getInventorySummary()
    const data = res && res.data
    if (data) {
      summary.value = {
        total_items: data.total_items ?? 0,
        total_value: data.total_value ?? 0,
        low_stock_count: data.low_stock_count ?? 0,
        category_count: data.category_count ?? 0
      }
      if (Array.isArray(data.category_distribution)) {
        categoryData.value = data.category_distribution
      }
      if (Array.isArray(data.status_distribution)) {
        statusData.value = data.status_distribution
      }
      if (Array.isArray(data.top_items)) {
        topItemsData.value = data.top_items
      }
      if (Array.isArray(data.low_stock_items)) {
        lowStockItems.value = data.low_stock_items
      }
    }
  } catch (e) {
    console.error('加载库存汇总失败:', e)
  }
}

const loadCategory = async () => {
  try {
    const res = await getInventoryCategory()
    const data = res && res.data
    if (Array.isArray(data)) {
      categoryData.value = data
    }
  } catch (e) {
    console.error('加载分类分布失败:', e)
  } finally {
    renderCategoryChart()
  }
}

const loadTopItems = async () => {
  try {
    const res = await getInventoryTopItems()
    const data = res && res.data
    if (Array.isArray(data)) {
      topItemsData.value = data
    }
  } catch (e) {
    console.error('加载 TOP 物品失败:', e)
  } finally {
    renderTopItemsChart()
  }
}

const categoryColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8e7cc3', '#00BCD4', '#FF9800', '#795548', '#607D8B']

const renderCategoryChart = () => {
  if (!categoryChart) return
  const data = categoryData.value || []
  const pieData = data.map((d, i) => ({
    name: d.category || '未分类',
    value: Number(d.item_count || 0),
    itemStyle: { color: categoryColors[i % categoryColors.length] }
  }))

  categoryChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 20,
      top: 'center'
    },
    series: [
      {
        name: '库存分类',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c} ({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: pieData
      }
    ]
  })
}

const renderTopItemsChart = () => {
  if (!topItemsChart) return
  const data = (topItemsData.value || []).slice(0, 10)
  const names = data.map(d => d.item_name).reverse()
  const values = data.map(d => Number(d.total_value || 0)).reverse()

  topItemsChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const p = params[0]
        const idx = data.length - 1 - p.dataIndex
        const item = data[idx]
        return `${p.name}<br/>价值: ¥${formatNumber(p.value)}<br/>数量: ${item?.quantity || 0} ${item?.unit || ''}`
      }
    },
    grid: {
      top: 20,
      left: 120,
      right: 80,
      bottom: 30
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val) => {
          if (val >= 10000) return (val / 10000).toFixed(1) + '万'
          if (val >= 1000) return (val / 1000).toFixed(1) + 'k'
          return val
        }
      }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        fontSize: 12,
        interval: 0
      }
    },
    series: [
      {
        type: 'bar',
        data: values,
        barWidth: '55%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#66B1FF' }
          ]),
          borderRadius: [0, 6, 6, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: (p) => '¥' + formatNumber(p.value)
        }
      }
    ]
  })
}

const renderStatusChart = () => {
  if (!statusChart) return
  const data = statusData.value || []
  if (data.length === 0) return
  const names = data.map(d => d.status || '未知')
  const counts = data.map(d => Number(d.item_count || 0))
  const values = data.map(d => Number(d.total_value || 0))

  statusChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['物品数', '总价值'],
      top: 0
    },
    grid: {
      top: 50,
      left: 70,
      right: 70,
      bottom: 50
    },
    xAxis: {
      type: 'category',
      data: names
    },
    yAxis: [
      {
        type: 'value',
        name: '物品数',
        axisLabel: { formatter: '{value}' }
      },
      {
        type: 'value',
        name: '总价值',
        axisLabel: {
          formatter: (val) => {
            if (val >= 10000) return (val / 10000).toFixed(1) + '万'
            return val
          }
        }
      }
    ],
    series: [
      {
        name: '物品数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#F56C6C' },
            { offset: 1, color: '#FFB3B3' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        barWidth: '40%',
        label: { show: true, position: 'top' }
      },
      {
        name: '总价值',
        type: 'line',
        yAxisIndex: 1,
        data: values,
        smooth: true,
        itemStyle: { color: '#E6A23C' },
        lineStyle: { width: 3 },
        symbolSize: 10
      }
    ]
  })
}

const initCharts = () => {
  if (categoryChartRef.value) categoryChart = echarts.init(categoryChartRef.value)
  if (topItemsChartRef.value) topItemsChart = echarts.init(topItemsChartRef.value)
  if (statusChartRef.value) statusChart = echarts.init(statusChartRef.value)
}

const handleResize = () => {
  categoryChart && categoryChart.resize()
  topItemsChart && topItemsChart.resize()
  statusChart && statusChart.resize()
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

const analyzeCategory = async () => {
  analyzing.category = true
  openAiDialog('库存分类分布 AI 分析报告', 'inventory-category')
  try {
    const categoryForAI = categoryData.value.map(d => ({
      分类: d.category,
      物品数: d.item_count,
      总数量: d.total_quantity,
      总价值: d.total_value
    }))

    const res = await aiAnalyze({
      dataType: 'inventory-category',
      dataSummary: {
        总体指标: {
          物品总数: summary.value.total_items,
          库存总价值: summary.value.total_value,
          分类数: summary.value.category_count
        },
        分类分布: categoryForAI
      },
      userQuestion: `请作为专业的库存管理分析师，基于以下库存分类分布数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **数据概览**：库存总价值、物品总数、分类数等关键指标
2. **分类结构分析**：主要分类占比、价值最高的分类、是否存在过度集中风险
3. **库存分布合理性**：分类分布是否合理、是否需要调整采购策略
4. **优化建议**：基于分析给出具体可行的库存管理建议

## 输出要求
- 使用 Markdown 格式输出
- 标题、列表、粗体强调关键数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析分类分布失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.category = false
    aiLoading.value = false
  }
}

const analyzeTopItems = async () => {
  analyzing.topItems = true
  openAiDialog('高价值物品 AI 分析报告', 'inventory-top-items')
  try {
    const topForAI = (topItemsData.value || []).slice(0, 10).map(d => ({
      物品名称: d.item_name,
      分类: d.category,
      数量: d.quantity,
      单位: d.unit,
      单价: d.unit_price,
      总价值: d.total_value,
      状态: d.status
    }))

    const res = await aiAnalyze({
      dataType: 'inventory-top-items',
      dataSummary: {
        库存总价值: summary.value.total_value,
        'TOP 10 高价值物品': topForAI
      },
      userQuestion: `请作为专业的库存管理分析师，基于以下高价值物品数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **高价值物品识别**：总价值最高的物品、占比分析
2. **风险评估**：是否有高价值物品处于低库存/缺货状态、潜在影响
3. **采购建议**：针对高价值物品的采购和存储策略建议
4. **优化建议**：具体可执行的优化措施

## 输出要求
- 使用 Markdown 格式输出
- 可用表格呈现 TOP 10 物品数据
- 用 **粗体** 强调关键物品和数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析高价值物品失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.topItems = false
    aiLoading.value = false
  }
}

const analyzeLowStock = async () => {
  analyzing.lowStock = true
  openAiDialog('低库存预警 AI 分析报告', 'inventory-low-stock')
  try {
    const lowStockForAI = lowStockItems.value.map(d => ({
      物品名称: d.item_name,
      分类: d.category,
      当前数量: d.quantity,
      最低库存: d.min_quantity,
      存放位置: d.location
    }))

    const statusForAI = statusData.value.map(d => ({
      状态: d.status,
      物品数: d.item_count,
      总价值: d.total_value
    }))

    const res = await aiAnalyze({
      dataType: 'inventory-low-stock',
      dataSummary: {
        低库存物品数: summary.value.low_stock_count,
        库存状态分布: statusForAI,
        低库存物品清单: lowStockForAI
      },
      userQuestion: `请作为专业的库存管理分析师，基于以下低库存预警数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **预警概览**：低库存/缺货物品数量、涉及的主要分类
2. **紧急度评估**：最需要立即补货的物品、可能造成的业务影响
3. **补货优先级**：根据分类和价值给出补货优先级建议
4. **优化建议**：采购计划、库存阈值调整、供应商管理等

## 输出要求
- 使用 Markdown 格式输出
- 可用表格呈现低库存物品清单
- 用 **粗体** 强调紧急物品和关键数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析低库存预警失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.lowStock = false
    aiLoading.value = false
  }
}

// ============ 整体分析函数 ============

const analyzeOverall = async () => {
  analyzing.overall = true
  openAiDialog('库存数据 AI 整体分析报告', 'inventory-overall')
  try {
    const categoryForAI = categoryData.value.map(d => ({
      分类: d.category, 物品数: d.item_count, 总数量: d.total_quantity, 总价值: d.total_value
    }))

    const topForAI = (topItemsData.value || []).slice(0, 10).map(d => ({
      物品名称: d.item_name, 分类: d.category, 数量: d.quantity, 总价值: d.total_value, 状态: d.status
    }))

    const lowStockForAI = lowStockItems.value.map(d => ({
      物品名称: d.item_name, 分类: d.category, 当前数量: d.quantity, 最低库存: d.min_quantity
    }))

    const res = await aiAnalyze({
      dataType: 'inventory-overall',
      dataSummary: {
        总体指标: {
          物品总数: summary.value.total_items,
          库存总价值: summary.value.total_value,
          低库存物品数: summary.value.low_stock_count,
          分类数: summary.value.category_count
        },
        分类分布: categoryForAI,
        'TOP 10 高价值物品': topForAI,
        低库存预警物品: lowStockForAI
      },
      userQuestion: `请作为专业的数据分析师和库存管理顾问，基于以下完整的库存数据，生成一份全面深入的数据分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **执行摘要**：仓库整体运营状况总结、关键数据指标
2. **分类结构分析**：主要分类占比、价值分布、是否存在集中风险
3. **高价值物品分析**：TOP 10 物品识别、风险管理建议
4. **低库存预警分析**：紧急补货需求、业务影响评估
5. **关键发现**：从数据中提炼的重要洞察和业务风险
6. **综合建议**：具体可执行的优化建议（采购、存储、预警阈值等）

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
> 数据来源：库存管理看板实时数据

---

${aiDialog.content}

---

*本报告由 AI 智能分析系统自动生成*`

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const fileName = `库存分析报告_${Date.now()}.md`
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
    loadCategory(),
    loadTopItems()
  ]).finally(() => {
    loading.value = false
    renderCategoryChart()
    renderTopItemsChart()
    renderStatusChart()
  })
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  categoryChart && categoryChart.dispose()
  topItemsChart && topItemsChart.dispose()
  statusChart && statusChart.dispose()
})
</script>

<style scoped>
.inventory {
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

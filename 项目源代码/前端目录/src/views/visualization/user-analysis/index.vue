<template>
  <div class="user-analysis">
    <!-- 顶部整体分析按钮 -->
    <el-row :gutter="20" class="row-overall">
      <el-col :span="24">
        <el-card shadow="hover" class="overall-card">
          <div class="overall-inner">
            <div class="overall-left">
              <el-icon :size="32" color="#409EFF"><MagicStick /></el-icon>
              <div class="overall-info">
                <div class="overall-title">用户与部门 AI 智能分析</div>
                <div class="overall-sub">整合部门分布、注册趋势、角色权限等数据，一键生成全面的组织数据分析报告</div>
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
    <el-row :gutter="20" class="row-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-blue">
              <el-icon :size="28"><User /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">总用户</div>
              <div class="text-value">{{ formatNumber(summary.total_user) }}</div>
              <div class="text-sub">部门数：{{ formatNumber(summary.dept_count) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-green">
              <el-icon :size="28"><CircleCheck /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">活跃用户</div>
              <div class="text-value">{{ formatNumber(summary.active_user) }}</div>
              <div class="text-sub">占比 {{ summary.active_rate }}%</div>
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
              <div class="text-label">新注册</div>
              <div class="text-value">{{ formatNumber(summary.new_register) }}</div>
              <div class="text-sub">近期新增用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-red">
              <el-icon :size="28"><Warning /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">异常用户</div>
              <div class="text-value">{{ formatNumber(summary.disabled_user) }}</div>
              <div class="text-sub">已禁用账号</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><OfficeBuilding /></el-icon>
                <span>&nbsp;部门用户分布 TOP 10</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeDept" :loading="analyzing.dept">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="deptChartRef" class="chart-large"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Calendar /></el-icon>
                <span>&nbsp;用户注册趋势（近30天）</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeTrend" :loading="analyzing.trend">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Avatar /></el-icon>
                <span>&nbsp;用户角色分布</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeRole" :loading="analyzing.role">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="roleChartRef" class="chart-large"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Rank /></el-icon>
                <span>&nbsp;部门用户排名 TOP 10</span>
              </div>
            </div>
          </template>
          <el-table :data="topDepts" border stripe style="width: 100%" max-height="380px" v-loading="loading">
            <el-table-column type="index" label="排名" width="90" align="center">
              <template #default="scope">
                <el-tag v-if="scope.$index < 3" :type="['danger', 'warning', 'success'][scope.$index]" size="small">
                  TOP {{ scope.$index + 1 }}
                </el-tag>
                <span v-else>{{ scope.$index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="deptName" label="部门名称" min-width="180" />
            <el-table-column prop="userCount" label="用户数" width="120" align="center" />
            <el-table-column label="占比" min-width="180">
              <template #default="scope">
                <el-progress :percentage="getPercentage(scope.row.userCount)" :stroke-width="12" />
              </template>
            </el-table-column>
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
import {
  User, CircleCheck, TrendCharts, Warning, OfficeBuilding,
  Calendar, Avatar, Rank, MagicStick, DocumentCopy, Download, Document, Printer
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getUserAnalysisSummary, getDeptUserDistribution, getUserRegisterTrend, getUserRoleDistribution } from '@/api/visualization'
import { aiAnalyze } from '@/api/ai'

const loading = ref(false)
const aiLoading = ref(false)
const summary = ref({
  total_user: 0,
  active_user: 0,
  disabled_user: 0,
  dept_count: 0,
  active_rate: '0.00',
  new_register: 0
})
const topDepts = ref([])
const deptData = ref([])
const trendData = ref([])
const roleData = ref([])

const deptChartRef = ref(null)
const trendChartRef = ref(null)
const roleChartRef = ref(null)
let deptChart = null, trendChart = null, roleChart = null

let totalUserForPercentage = 0
const analyzing = reactive({ dept: false, trend: false, role: false, overall: false })
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
  if (!num && num !== 0) return '0'
  return String(num).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const getPercentage = (count) => {
  if (!totalUserForPercentage) return 0
  return Math.round((Number(count) / totalUserForPercentage) * 100)
}

const loadSummary = async () => {
  try {
    const res = await getUserAnalysisSummary()
    const data = res?.data || {}
    const totalUser = Number(data.total_user || 0)
    const activeUser = Number(data.active_user || 0)
    const activeRate = totalUser > 0 ? (activeUser / totalUser * 100).toFixed(2) : '0.00'
    summary.value = {
      total_user: totalUser,
      active_user: activeUser,
      disabled_user: Number(data.disabled_user || 0),
      dept_count: Number(data.dept_count || 0),
      active_rate: activeRate,
      new_register: 0
    }
    totalUserForPercentage = totalUser || 1
  } catch (e) {
    console.error('加载用户汇总失败:', e)
  }
}

const loadDeptDistribution = async () => {
  try {
    const res = await getDeptUserDistribution()
    const data = (res?.data && Array.isArray(res.data)) ? res.data : []
    const norm = data.map(d => ({
      deptName: d.dept_name || d.name || '未命名',
      userCount: Number(d.user_count || d.count || d.value || 0)
    })).sort((a, b) => b.userCount - a.userCount)

    if (deptChart) {
      const top10 = norm.slice(0, 10).reverse()
      const names = top10.map(d => d.deptName)
      const values = top10.map(d => d.userCount)
      deptChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { top: 20, left: 120, right: 40, bottom: 30 },
        xAxis: { type: 'value', axisLabel: { formatter: '{value} 人' } },
        yAxis: { type: 'category', data: names, axisLabel: { fontSize: 12 } },
        series: [{
          type: 'bar', data: values, barWidth: '55%',
          itemStyle: {
            color: (params) => {
              const colors = ['#F56C6C', '#E6A23C', '#F2D67F', '#67C23A', '#95D475', '#409EFF', '#79BBFF', '#A0CFFF', '#909399', '#C0C4CC']
              return colors[params.dataIndex % colors.length]
            }, borderRadius: [0, 4, 4, 0]
          },
          label: { show: true, position: 'right', formatter: '{c} 人' }
        }]
      })
    }
    deptData.value = norm
    topDepts.value = norm
  } catch (e) { console.error('加载部门分布失败:', e) }
}

const loadRegisterTrend = async () => {
  try {
    const res = await getUserRegisterTrend()
    const data = (res?.data && Array.isArray(res.data)) ? res.data : []
    const norm = data.map(d => ({
      date: d.date,
      count: Number(d.count || d.user_count || 0)
    }))

    const newRegisterSum = norm.reduce((sum, d) => sum + d.count, 0)
    summary.value.new_register = newRegisterSum

    if (trendChart) trendChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      grid: { top: 40, left: 50, right: 30, bottom: 50 },
      xAxis: { type: 'category', data: norm.map(d => d.date), axisLabel: { rotate: 45 } },
      yAxis: { type: 'value' },
      series: [{
        type: 'line', smooth: true, data: norm.map(d => d.count),
        itemStyle: { color: '#409EFF' }, lineStyle: { width: 3 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(64,158,255,0.3)' }, { offset: 1, color: 'rgba(64,158,255,0.02)' }]) }
      }]
    })
    trendData.value = norm
  } catch (e) { console.error('加载注册趋势失败:', e) }
}

const loadRoleDistribution = async () => {
  try {
    const res = await getUserRoleDistribution()
    const data = (res?.data && Array.isArray(res.data)) ? res.data : []
    const norm = data.map(d => ({
      name: d.role_name || d.name || '未知角色',
      value: Number(d.user_count || d.count || 0)
    }))
    const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#95D475', '#79BBFF', '#A0CFFF']

    if (roleChart) roleChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 5, type: 'scroll' },
      series: [{
        type: 'pie', radius: ['38%', '68%'], center: ['50%', '45%'],
        avoidLabelOverlap: true,
        label: { show: true, formatter: '{b}\n{c} ({d}%)' },
        data: norm.map((item, idx) => ({ ...item, itemStyle: { color: colors[idx % colors.length] } })),
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } }
      }]
    })
    roleData.value = norm
  } catch (e) { console.error('加载角色分布失败:', e) }
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

const analyzeDept = async () => {
  analyzing.dept = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '部门用户分布 AI 分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'dept'
  try {
    const forAI = deptData.value.map(d => ({ 部门: d.deptName, 用户数: d.userCount }))
    const summaryData = {
      总用户: summary.value.total_user,
      活跃用户: summary.value.active_user,
      部门数: summary.value.dept_count
    }
    const aiRes = await aiAnalyze({
      dataType: 'user-dept-distribution',
      dataSummary: { 汇总: summaryData, 部门分布: forAI },
      userQuestion: `请作为资深的组织架构分析师，基于以下部门用户分布数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **分布合理性分析**：用户在各部门的分布是否合理、是否存在过度集中
2. **关键部门识别**：用户数最多的部门、规模合理性
3. **组织架构评估**：基于部门分布评估整体组织架构
4. **优化建议**：人员调配、部门重组、招聘策略等建议

## 输出要求
- 使用 Markdown 格式输出
- 可使用表格展示 TOP 10 部门数据
- 用 **粗体** 强调关键发现和数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })
    aiResultDialog.content = extractAnalysisContent(aiRes)
  } catch (e) {
    console.error(e)
    aiResultDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.dept = false
    aiLoading.value = false
  }
}

const analyzeTrend = async () => {
  analyzing.trend = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '用户注册趋势 AI 分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'trend'
  try {
    const forAI = trendData.value.map(d => ({ 日期: d.date, 注册数: d.count }))
    const aiRes = await aiAnalyze({
      dataType: 'user-register-trend',
      dataSummary: {
        汇总: {
          总用户: summary.value.total_user,
          近30天新增: summary.value.new_register,
          活跃用户: summary.value.active_user,
          活跃率: summary.value.active_rate + '%'
        },
        注册趋势: forAI
      },
      userQuestion: `请作为专业的用户增长分析师，基于以下用户注册趋势数据，生成一份结构化的增长分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **增长趋势识别**：用户注册量变化趋势、增长/下降/稳定模式
2. **关键日期分析**：注册量峰值和低谷日期、可能原因
3. **增长速度评估**：当前增长速度、是否需要策略调整
4. **优化建议**：用户获取、活动策划、留存策略等建议

## 输出要求
- 使用 Markdown 格式输出
- 用 **粗体** 强调关键指标和增长机会
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })
    aiResultDialog.content = extractAnalysisContent(aiRes)
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

const analyzeRole = async () => {
  analyzing.role = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '用户角色分布 AI 分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'role'
  try {
    const forAI = roleData.value.map(d => ({ 角色: d.name, 用户数: d.value }))
    const aiRes = await aiAnalyze({
      dataType: 'user-role-distribution',
      dataSummary: {
        汇总: {
          总用户: summary.value.total_user,
          角色数: forAI.length
        },
        角色分布: forAI
      },
      userQuestion: `请作为专业的权限管理和安全审计师，基于以下角色分布数据，生成一份结构化的权限分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **权限集中度评估**：哪些角色用户最多、权限集中风险
2. **管理员角色分析**：管理员类角色占比是否合理
3. **权限风险评估**：基于角色分布识别潜在权限风险
4. **优化建议**：权限调整、角色拆分、审计策略等建议

## 输出要求
- 使用 Markdown 格式输出
- 可使用表格展示各角色及其用户数和占比
- 用 **粗体** 强调关键发现和风险点
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })
    aiResultDialog.content = extractAnalysisContent(aiRes)
  } catch (e) {
    console.error(e)
    aiResultDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.role = false
    aiLoading.value = false
  }
}

// ============ 整体分析函数 ============

const analyzeOverall = async () => {
  analyzing.overall = true
  aiLoading.value = true
  aiResultDialog.visible = true
  aiResultDialog.title = '用户与部门 AI 整体分析报告'
  aiResultDialog.content = ''
  aiResultDialog.dataType = 'overall'
  try {
    const deptForAI = deptData.value.slice(0, 15).map(d => ({
      部门: d.deptName, 用户数: d.userCount
    }))
    const trendForAI = trendData.value.map(d => ({
      日期: d.date, 注册数: d.count
    }))
    const roleForAI = roleData.value.map(d => ({
      角色: d.name, 用户数: d.value
    }))

    const res = await aiAnalyze({
      dataType: 'user-analysis-overall',
      dataSummary: {
        核心指标汇总: {
          总用户数: summary.value.total_user,
          活跃用户数: summary.value.active_user,
          活跃率: summary.value.active_rate + '%',
          部门数: summary.value.dept_count,
          新注册用户: summary.value.new_register,
          已禁用用户: summary.value.disabled_user
        },
        部门分布TOP15: deptForAI,
        近期注册趋势: trendForAI,
        角色权限分布: roleForAI
      },
      userQuestion: `请作为资深的组织架构和人力资源管理顾问，基于以下完整的用户与部门数据，生成一份全面深入的组织分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **执行摘要**：组织整体用户和部门状况、关键指标、健康度评估
2. **部门分布分析**：用户分布合理性、关键部门识别、架构合理性
3. **用户增长趋势分析**：注册量变化趋势、增长模式、峰值低谷分析
4. **角色权限分析**：角色分布合理性、权限集中风险、最小权限原则
5. **组织健康度评估**：活跃率、增长健康度、均衡度、权限风险
6. **关键发现与建议**：重要发现、风险提示、综合优化建议

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
> 数据来源：用户与部门管理实时数据

---

${aiResultDialog.content}

---

*本报告由 AI 智能分析系统自动生成*`

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const fileName = `用户分析报告_${Date.now()}.md`
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
数据来源：用户与部门管理实时数据

${'-'.repeat(60)}

${textContent}

${'-'.repeat(60)}
本报告由 AI 智能分析系统自动生成
${'='.repeat(60)}`

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const fileName = `用户分析报告_${Date.now()}.txt`
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
  if (deptChartRef.value) {
    deptChart = echarts.init(deptChartRef.value)
    deptChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 20, left: 100, right: 30, bottom: 30 },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: [] },
      series: [{ type: 'bar', data: [], label: { show: true, position: 'right' } }]
    })
  }
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 40, left: 50, right: 30, bottom: 30 },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'line', smooth: true, data: [] }]
    })
  }
  if (roleChartRef.value) {
    roleChart = echarts.init(roleChartRef.value)
    roleChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 5 },
      series: [{ type: 'pie', radius: ['38%', '68%'], data: [] }]
    })
  }
}

const handleResize = () => {
  deptChart && deptChart.resize()
  trendChart && trendChart.resize()
  roleChart && roleChart.resize()
}

onMounted(async () => {
  initCharts()
  loading.value = true
  try {
    await Promise.all([loadSummary(), loadDeptDistribution(), loadRegisterTrend(), loadRoleDistribution()])
  } finally {
    loading.value = false
  }
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  deptChart && deptChart.dispose()
  trendChart && trendChart.dispose()
  roleChart && roleChart.dispose()
})
</script>

<style scoped>
.user-analysis {
  padding: 20px;
}

/* 整体分析卡片 */
.row-overall {
  margin-bottom: 20px;
}

.overall-card {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 50%, #fdf6ec 100%);
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

/* 统计卡片 */
.row-cards {
  margin-bottom: 24px;
}

.chart-section {
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

.chart-large {
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

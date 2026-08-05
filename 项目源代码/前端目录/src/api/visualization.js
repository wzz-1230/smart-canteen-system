import request from '@/utils/request'

// -------------------- 食堂销售看板接口 --------------------

// 获取销售汇总数据
export function getCanteenSalesSummary() {
  return request({
    url: '/visualization/canteen-sales/summary',
    method: 'get'
  })
}

// 获取每日销售趋势
export function getCanteenDailyTrend() {
  return request({
    url: '/visualization/canteen-sales/daily-trend',
    method: 'get'
  })
}

// 获取菜品销售排行
export function getDishRanking() {
  return request({
    url: '/visualization/canteen-sales/dish-ranking',
    method: 'get'
  })
}

// 获取销售时段分布
export function getCanteenHourlyDistribution() {
  return request({
    url: '/visualization/canteen-sales/hourly-distribution',
    method: 'get'
  })
}

// -------------------- 系统日志监控接口 --------------------

// 获取日志汇总
export function getLogAnalysisSummary() {
  return request({
    url: '/visualization/log-analysis/summary',
    method: 'get'
  })
}

// 获取请求趋势（近7天）
export function getLogTrend() {
  return request({
    url: '/visualization/log-analysis/trend',
    method: 'get'
  })
}

// 获取请求类型分布
export function getLogTypeDistribution() {
  return request({
    url: '/visualization/log-analysis/type-distribution',
    method: 'get'
  })
}

// 获取登录成功/失败统计
export function getLogLoginStats() {
  return request({
    url: '/visualization/log-analysis/login-stats',
    method: 'get'
  })
}

// -------------------- 用户与部门分析接口 --------------------

// 获取用户与部门分析汇总
export function getUserAnalysisSummary() {
  return request({
    url: '/visualization/user-analysis/summary',
    method: 'get'
  })
}

// 获取用户按部门分布
export function getDeptUserDistribution() {
  return request({
    url: '/visualization/user-analysis/dept-distribution',
    method: 'get'
  })
}

// 获取用户注册趋势（近30天）
export function getUserRegisterTrend() {
  return request({
    url: '/visualization/user-analysis/register-trend',
    method: 'get'
  })
}

// 获取用户角色分布
export function getUserRoleDistribution() {
  return request({
    url: '/visualization/user-analysis/role-distribution',
    method: 'get'
  })
}

// -------------------- 库存管理看板接口 --------------------

// 获取库存汇总数据
export function getInventorySummary() {
  return request({
    url: '/visualization/inventory/summary',
    method: 'get'
  })
}

// 获取库存分类分布
export function getInventoryCategory() {
  return request({
    url: '/visualization/inventory/category',
    method: 'get'
  })
}

// 获取 TOP 高价值物品
export function getInventoryTopItems() {
  return request({
    url: '/visualization/inventory/top-items',
    method: 'get'
  })
}

// -------------------- 收支管理看板接口 --------------------

// 获取收支汇总数据
export function getIncomeExpenseSummary() {
  return request({
    url: '/visualization/income-expense/summary',
    method: 'get'
  })
}

// 获取近30天收支趋势
export function getIncomeExpenseTrend() {
  return request({
    url: '/visualization/income-expense/trend',
    method: 'get'
  })
}

// 获取 TOP 大额收支记录
export function getIncomeExpenseTopRecords() {
  return request({
    url: '/visualization/income-expense/top-records',
    method: 'get'
  })
}

// 兼容旧名称
export const getUserDeptDistribution = getDeptUserDistribution
export const getUserStatusDistribution = getUserRoleDistribution

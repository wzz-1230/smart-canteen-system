import request from '@/utils/request'

// 获取数据分析汇总信息
export function getAnalyticsSummary() {
  return request({
    url: '/analytics/summary',
    method: 'get'
  })
}

// 获取库存记录列表
export function listInventory(query) {
  return request({
    url: '/analytics/inventory/list',
    method: 'get',
    params: query
  })
}

// 获取库存周转趋势
export function getInventoryTurnoverTrend() {
  return request({
    url: '/analytics/inventory/turnover-trend',
    method: 'get'
  })
}

// 获取物品类型分布
export function getInventoryTypeDistribution() {
  return request({
    url: '/analytics/inventory/type-distribution',
    method: 'get'
  })
}

// 获取收支明细列表
export function listRevenueExpense(query) {
  return request({
    url: '/analytics/revenue-expense/list',
    method: 'get',
    params: query
  })
}

// 获取收支趋势
export function getRevenueExpenseTrend() {
  return request({
    url: '/analytics/revenue-expense/trend',
    method: 'get'
  })
}

// 获取收入分类分布
export function getRevenueCategoryDistribution() {
  return request({
    url: '/analytics/revenue-expense/revenue-distribution',
    method: 'get'
  })
}

// 获取支出分类分布
export function getExpenseCategoryDistribution() {
  return request({
    url: '/analytics/revenue-expense/expense-distribution',
    method: 'get'
  })
}

// 获取利润分析列表
export function listProfit(query) {
  return request({
    url: '/analytics/profit/list',
    method: 'get',
    params: query
  })
}

// 获取利润趋势
export function getProfitTrend() {
  return request({
    url: '/analytics/profit/trend',
    method: 'get'
  })
}

// 获取成本结构分布
export function getCostStructureDistribution() {
  return request({
    url: '/analytics/profit/cost-structure',
    method: 'get'
  })
}

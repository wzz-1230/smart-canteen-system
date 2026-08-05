import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/ruoyi";

export function listMenu(query) {
  return request({
    url: '/canteen/menu/list',
    method: 'get',
    params: query
  })
}

export function getMenu(menuId) {
  return request({
    url: '/canteen/menu/' + parseStrEmpty(menuId),
    method: 'get'
  })
}

export function addMenu(data) {
  return request({
    url: '/canteen/menu',
    method: 'post',
    data: data
  })
}

export function updateMenu(data) {
  return request({
    url: '/canteen/menu',
    method: 'put',
    data: data
  })
}

export function delMenu(menuId) {
  return request({
    url: '/canteen/menu/' + menuId,
    method: 'delete'
  })
}

export function listOrder(query) {
  return request({
    url: '/canteen/order/list',
    method: 'get',
    params: query
  })
}

export function getOrder(orderId) {
  return request({
    url: '/canteen/order/' + parseStrEmpty(orderId),
    method: 'get'
  })
}

export function addOrder(data) {
  return request({
    url: '/canteen/order',
    method: 'post',
    data: data
  })
}

export function updateOrder(data) {
  return request({
    url: '/canteen/order',
    method: 'put',
    data: data
  })
}

export function delOrder(orderId) {
  return request({
    url: '/canteen/order/' + orderId,
    method: 'delete'
  })
}

export function listTable(query) {
  return request({
    url: '/canteen/table/list',
    method: 'get',
    params: query
  })
}

export function getTable(tableId) {
  return request({
    url: '/canteen/table/' + parseStrEmpty(tableId),
    method: 'get'
  })
}

export function addTable(data) {
  return request({
    url: '/canteen/table',
    method: 'post',
    data: data
  })
}

export function updateTable(data) {
  return request({
    url: '/canteen/table',
    method: 'put',
    data: data
  })
}

export function delTable(tableId) {
  return request({
    url: '/canteen/table/' + tableId,
    method: 'delete'
  })
}

export function updateTableStatus(tableId, status) {
  return request({
    url: '/canteen/table/' + tableId + '/status/' + status,
    method: 'put'
  })
}

export function listStaff(query) {
  return request({
    url: '/canteen/staff/list',
    method: 'get',
    params: query
  })
}

export function getStaff(staffId) {
  return request({
    url: '/canteen/staff/' + parseStrEmpty(staffId),
    method: 'get'
  })
}

export function addStaff(data) {
  return request({
    url: '/canteen/staff',
    method: 'post',
    data: data
  })
}

export function updateStaff(data) {
  return request({
    url: '/canteen/staff',
    method: 'put',
    data: data
  })
}

export function delStaff(staffId) {
  return request({
    url: '/canteen/staff/' + staffId,
    method: 'delete'
  })
}

export function listCanteenUser(query) {
  return request({
    url: '/canteen/user/list',
    method: 'get',
    params: query
  })
}

export function getCanteenUser(userId) {
  return request({
    url: '/canteen/user/' + parseStrEmpty(userId),
    method: 'get'
  })
}

export function addCanteenUser(data) {
  return request({
    url: '/canteen/user',
    method: 'post',
    data: data
  })
}

export function updateCanteenUser(data) {
  return request({
    url: '/canteen/user',
    method: 'put',
    data: data
  })
}

export function delCanteenUser(userId) {
  return request({
    url: '/canteen/user/' + userId,
    method: 'delete'
  })
}

export function resetCanteenUserPwd(userId, newPassword) {
  return request({
    url: '/canteen/user/reset-password',
    method: 'put',
    data: { userId: userId, newPassword: newPassword }
  })
}

export function canteenAiChat(question) {
  return request({
    url: '/canteen/ai/chat',
    method: 'post',
    data: { question: question }
  })
}

// 库存管理 API
export function listInventory(query) {
  return request({
    url: '/canteen/inventory/list',
    method: 'get',
    params: query
  })
}

export function getInventory(recordId) {
  return request({
    url: '/canteen/inventory/' + parseStrEmpty(recordId),
    method: 'get'
  })
}

export function addInventory(data) {
  return request({
    url: '/canteen/inventory',
    method: 'post',
    data: data
  })
}

export function updateInventory(data) {
  return request({
    url: '/canteen/inventory',
    method: 'put',
    data: data
  })
}

export function delInventory(recordId) {
  return request({
    url: '/canteen/inventory/' + recordId,
    method: 'delete'
  })
}

// 利润管理 API
export function listProfit(query) {
  return request({
    url: '/canteen/profit/list',
    method: 'get',
    params: query
  })
}

export function getProfit(recordId) {
  return request({
    url: '/canteen/profit/' + parseStrEmpty(recordId),
    method: 'get'
  })
}

export function addProfit(data) {
  return request({
    url: '/canteen/profit',
    method: 'post',
    data: data
  })
}

export function updateProfit(data) {
  return request({
    url: '/canteen/profit',
    method: 'put',
    data: data
  })
}

export function delProfit(recordId) {
  return request({
    url: '/canteen/profit/' + recordId,
    method: 'delete'
  })
}

// 收支管理 API
export function listRevenueExpense(query) {
  return request({
    url: '/canteen/revenue-expense/list',
    method: 'get',
    params: query
  })
}

export function getRevenueExpense(recordId) {
  return request({
    url: '/canteen/revenue-expense/' + parseStrEmpty(recordId),
    method: 'get'
  })
}

export function addRevenueExpense(data) {
  return request({
    url: '/canteen/revenue-expense',
    method: 'post',
    data: data
  })
}

export function updateRevenueExpense(data) {
  return request({
    url: '/canteen/revenue-expense',
    method: 'put',
    data: data
  })
}

export function delRevenueExpense(recordId) {
  return request({
    url: '/canteen/revenue-expense/' + recordId,
    method: 'delete'
  })
}

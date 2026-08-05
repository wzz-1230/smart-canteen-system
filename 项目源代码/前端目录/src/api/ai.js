import request from '@/utils/request'

// -------------------- DeepSeek 大模型对话接口 --------------------

// 数据分析（用于可视化页面的AI分析）
export function aiAnalyze(data) {
  return request({
    url: '/ai/analyze',
    method: 'post',
    data: data,
    timeout: 120000
  })
}

// 对话（非流式，用于简单测试）
export function aiChat(data) {
  return request({
    url: '/ai/chat',
    method: 'post',
    data: data,
    timeout: 120000
  })
}

// 获取支持的模型列表
export function getAIModels() {
  return request({
    url: '/ai/models',
    method: 'get'
  })
}

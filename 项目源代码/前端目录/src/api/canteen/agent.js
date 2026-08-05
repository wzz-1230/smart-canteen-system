import request from "@/utils/request";
import { getToken } from "@/utils/auth";

/**
 * 食堂智能体对话（使用原生fetch，支持流式响应）
 * @param {Object} data - 请求参数
 * @param {string} data.message - 用户消息
 * @param {boolean} data.useKnowledge - 是否使用知识库
 * @param {Function} onChunk - 流式响应回调（每收到新内容时调用）
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Promise<string>} - 完整的响应文本
 */
export function canteenAgentChat(data, onChunk = null, timeout = 120000) {
  return new Promise((resolve, reject) => {
    // 从环境变量获取 baseURL，确保通过 Vite 代理
    const baseURL = import.meta.env.VITE_APP_BASE_API || '';
    const url = baseURL + '/canteen/agent/chat';

    // 获取 token
    const token = getToken() || '';

    // 超时控制器
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => {
      abortController.abort();
      reject(new Error('请求超时，请稍后重试'));
    }, timeout);

    // 发起请求
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
      },
      body: JSON.stringify(data),
      signal: abortController.signal,
    })
      .then(async response => {
        if (!response.ok) {
          clearTimeout(timeoutId);
          let errorMsg = '请求失败';
          try {
            const errorData = await response.json();
            errorMsg = errorData.msg || errorData.message || `请求失败: ${response.status}`;
          } catch (e) {
            errorMsg = `请求失败: ${response.status}`;
          }
          reject(new Error(errorMsg));
          return;
        }

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullText = '';

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const text = decoder.decode(value, { stream: true });
          fullText += text;

          if (onChunk) {
            onChunk(fullText);
          }
        }

        clearTimeout(timeoutId);
        resolve(fullText);
      })
      .catch(error => {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
          reject(new Error('请求已取消'));
        } else {
          reject(error);
        }
      });
  });
}

// 获取食堂知识库
export function getCanteenKnowledge(queryType = 'all') {
  return request({
    url: "/canteen/agent/knowledge",
    method: "post",
    data: {
      queryType: queryType,
    },
    // 知识库请求给较长超时
    timeout: 60000
  });
}

// 获取智能体配置
export function getAgentConfig() {
  return request({
    url: "/canteen/agent/config",
    method: "get",
  });
}

// 快速智能分析
export function quickAnalyze(queryType = 'overview') {
  return request({
    url: "/canteen/agent/quick-analyze",
    method: "post",
    data: {
      queryType: queryType,
    },
    timeout: 60000
  });
}

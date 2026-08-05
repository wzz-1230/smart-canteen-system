<template>
  <div class="app-container chat-container">
    <el-container style="height: 100%">
      <!-- 主区域：对话 -->
      <el-main class="chat-main">
        <div class="chat-header">
          <div class="header-left">
            <el-icon><Coffee /></el-icon>
            <span class="header-title">食堂智能助手</span>
          </div>
          <div class="header-right">
            <el-tooltip content="新建对话" placement="bottom">
              <el-button icon="Refresh" @click="clearChat">新对话</el-button>
            </el-tooltip>
          </div>
        </div>

        <div class="chat-history" ref="chatHistoryRef">
          <div class="chat-content" ref="chatContentRef" :class="{ 'is-empty': messageList.length === 0 }">
            <div v-if="messageList.length === 0" class="welcome-screen">
              <div class="welcome-icon">
                <el-icon size="60"><Service /></el-icon>
              </div>
              <h2>你好！我是食堂智能助手 🍜</h2>
              <p>基于菜品知识库，为您提供菜品查询和推荐服务</p>

              <div class="quick-questions">
                <div class="quick-title">试试这些问题：</div>
                <div class="question-grid">
                  <div class="question-card" @click="sendQuickQuestion('有哪些辣味菜品？推荐一下')">
                    �️ 有哪些辣味菜品？推荐一下
                  </div>
                  <div class="question-card" @click="sendQuickQuestion('推荐一些清淡的素菜')">
                    🥗 推荐一些清淡的素菜
                  </div>
                  <div class="question-card" @click="sendQuickQuestion('红烧肉这道菜怎么样？')">
                    🥘 红烧肉这道菜怎么样？
                  </div>
                  <div class="question-card" @click="sendQuickQuestion('今天有什么特色菜推荐？')">
                    ⭐ 今天有什么特色菜推荐？
                  </div>
                </div>
              </div>
            </div>

            <div
              v-for="(msg, index) in messageList"
              :key="index"
              :class="[
                'message-row',
                msg.role === 'user' ? 'message-user' : 'message-ai',
              ]"
            >
              <div class="message-avatar">
                <el-avatar
                  :icon="msg.role === 'user' ? 'UserFilled' : 'Service'"
                  :size="40"
                  :class="msg.role === 'user' ? 'avatar-user' : 'avatar-ai'"
                ></el-avatar>
              </div>
              <div class="message-content-wrapper">
                <div class="message-sender">
                  {{ msg.role === "user" ? "我" : "食堂AI助手" }}
                  <span class="message-time">{{ msg.time }}</span>
                </div>
                <div class="message-bubble">
                  <div v-if="msg.role === 'user'" class="user-text">{{ msg.content }}</div>
                  <div v-else class="ai-text">
                    <div v-if="msg.loading" class="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                    <div v-else class="markdown-body">
                      <div class="ai-content" v-html="renderAiContent(msg.content)"></div>
                    </div>
                  </div>
                </div>
                <div class="message-footer" v-if="msg.role === 'assistant'">
                  <el-button link type="info" icon="DocumentCopy" size="small" @click="copyText(msg.content)">复制</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <div class="input-wrapper">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              :placeholder="loading ? 'AI正在思考...' : '请输入您的问题，如：今天有什么菜品推荐？'"
              :disabled="loading"
              resize="none"
              @keydown.enter.exact.prevent="handleSendMessage"
              @keydown.enter.shift.exact.prevent="inputMessage += '\n'"
            />
          </div>
          <div class="input-actions">
            <div class="hint-text">按 Enter 发送，Shift+Enter 换行</div>
            <el-button
              :type="loading ? 'danger' : 'primary'"
              :icon="loading ? 'VideoPause' : 'Promotion'"
              :disabled="!loading && !inputMessage.trim()"
              @click="handleSendMessage"
            >
              {{ loading ? "停止" : "发送" }}
            </el-button>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from "vue";
import { ElMessage } from "element-plus";
import { canteenAgentChat } from "@/api/canteen/agent";

// 消息列表
const messageList = ref([]);
const inputMessage = ref("");
const loading = ref(false);
const chatHistoryRef = ref(null);
const chatContentRef = ref(null);

let chatController = null;

// 格式化时间
function getCurrentTime() {
  const now = new Date();
  return `${now.getHours().toString().padStart(2, "0")}:${now
    .getMinutes()
    .toString()
    .padStart(2, "0")}`;
}

// 将智能体回复中的文本转换为 HTML（支持图片识别、换行）
function renderAiContent(text) {
  if (!text) return "";

  let result = String(text);

  // 1. 清理HTML标签和属性代码
  // 1a. 将完整的<img>标签转换为Markdown格式
  result = result.replace(/<img\b[^>]*>/gi, function(imgTag) {
    const srcMatch = imgTag.match(/src\s*=\s*["']([^"']+)["']/i);
    const altMatch = imgTag.match(/alt\s*=\s*["']([^"']*)["']/i);
    const src = srcMatch ? srcMatch[1] : '';
    const alt = altMatch ? altMatch[1] : '图片';
    if (src) {
      return '![' + alt + '](' + src + ')';
    }
    return '';
  });

  // 1b. 移除其他HTML标签
  result = result.replace(/<[^>]+>/g, '');

  // 1c. 清理残留的HTML属性片段
  result = result.replace(/\s+(?:class|id|style|loading|onerror|onload|onclick|onmouseover|onmouseout|src|alt|title|width|height|border)\s*=\s*"[^"]*"/g, '');
  result = result.replace(/\s+(?:class|id|style|loading|onerror|onload|onclick|onmouseover|onmouseout|src|alt|title|width|height|border)\s*=\s*'[^']*'/g, '');

  // 1d. 清理孤立的结束标签碎片
  result = result.replace(/\s*\/>/g, '');

  // 1e. 清理系统标记内容
  result = result.replace(/\{"msg_type"[^}]*\}/g, '');
  result = result.replace(/\["msg_type"[^}\]]*\}/g, '');

  // 2. 处理各种图片格式 — 统一转换为图片展示
  // 使用一个健壮的函数来处理所有图片URL
  function makeImg(url, alt) {
    const safeUrl = normalizeImageUrl(url.trim());
    const safeAlt = (alt || '菜品图片').replace(/[<>"']/g, '');
    return '<div class="ai-image-wrapper"><img src="' + safeUrl + '" alt="' + safeAlt + '" class="ai-content-image" loading="lazy"/></div>';
  }

  // 2a. Markdown 格式: ![描述](URL)
  const mdImgRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  result = result.replace(mdImgRegex, function(match, alt, url) {
    return makeImg(url, alt);
  });

  // 2b. 中文格式: 【图片】URL
  const cnImgRegex1 = /【图片】\s*([^\s<"']+)/gi;
  result = result.replace(cnImgRegex1, function(match, url) {
    return makeImg(url, '菜品图片');
  });

  // 2c. 格式: [图片: URL] 或 [图片：URL]
  const cnImgRegex2 = /\[图片[：:]\s*([^\]]+)\]/gi;
  result = result.replace(cnImgRegex2, function(match, url) {
    return makeImg(url, '菜品图片');
  });

  // 2d. 格式: 图片: URL 或 图片：URL（在行首或空格后出现）
  const cnImgRegex3 = /(?:^|\s)图片[：:]\s*([^\s<"']+\.(?:png|jpg|jpeg|gif|webp)[^\s<"']*)/gi;
  result = result.replace(cnImgRegex3, function(match, url) {
    return makeImg(url, '菜品图片');
  });

  // 2e. 裸URL匹配 — 匹配任何包含 canteen-menu-images 或菜品文件名的URL
  // 智能体可能返回各种不标准的URL格式，这里统一处理
  const rawImgRegex = /(https?:\/\/[^\s<"']*canteen-menu-images[^\s<"']*\.(?:png|jpg|jpeg|gif|webp)[^\s<"']*|\/?static\/canteen-menu-images[^\s<"']*\.(?:png|jpg|jpeg|gif|webp)[^\s<"']*|[^\s<"']*canteen-menu-images[^\s<"']*\.(?:png|jpg|jpeg|gif|webp)[^\s<"']*)/gi;
  result = result.replace(rawImgRegex, function(match, url) {
    return makeImg(url, '菜品图片');
  });

  // 3. 处理普通的换行
  result = result.replace(/\n/g, '<br/>');

  return result;
}

// 图片 URL 标准化 — 核心逻辑：从任何格式的URL中提取文件名，统一使用代理路径
function normalizeImageUrl(url) {
  if (!url) return "";
  
  let rawUrl = String(url).trim();
  
  // 1. 从URL中提取图片文件名（去除协议、域名、路径前缀）
  // 处理各种可能的格式：
  //   http://localhost:9099/static/canteen-menu-images/水煮肉片.png
  //   http:/localhost:9099static/canteen-menu-images/水煮肉片.png (缺少斜杠)
  //   /static/canteen-menu-images/水煮肉片.png
  //   static/canteen-menu-images/水煮肉片.png
  //   canteen-menu-images/水煮肉片.png
  //   水煮肉片.png
  
  let filename = rawUrl;
  
  // 去除协议和域名部分（包括不标准的 http:/ 或 http://）
  filename = filename.replace(/^https?:\/+/i, ''); // http:// 或 https:// 或 http:/
  filename = filename.replace(/^localhost:\d+/i, ''); // localhost:9099
  filename = filename.replace(/^[^\/]*\//, ''); // 其他域名
  
  // 去除路径前缀，只保留文件名
  // 先尝试提取完整路径（含 canteen-menu-images 目录）
  let imagePath = '';
  const pathMatch = filename.match(/canteen-menu-images[\/\\]*([^\s<>"']+\.(?:png|jpg|jpeg|gif|webp))/i);
  if (pathMatch) {
    imagePath = 'canteen-menu-images/' + pathMatch[1];
  } else {
    // 只提取文件名（最后一个 / 后的部分，或整个字符串）
    const lastSlash = filename.lastIndexOf('/');
    const lastBackslash = filename.lastIndexOf('\\');
    const idx = Math.max(lastSlash, lastBackslash);
    if (idx >= 0) {
      imagePath = 'canteen-menu-images/' + filename.substring(idx + 1);
    } else {
      imagePath = 'canteen-menu-images/' + filename;
    }
  }
  
  // 清理文件名中的多余字符
  imagePath = imagePath.replace(/[<>"']/g, '').trim();
  
  // 2. 对图片路径中的中文字符进行编码（只编码中文字符，保留 / 和扩展名）
  // 使用 encodeURIComponent 对每个中文字符单独编码
  const encodedPath = imagePath.replace(/[\u4e00-\u9fa5]/g, function(ch) {
    return encodeURIComponent(ch);
  });
  
  // 3. 统一使用代理路径，让前端开发服务器代理到后端
  return '/dev-api/static/' + encodedPath;
}

// HTML 字符转义（保留为兼容，但已不再使用）
function escapeHtml(text) {
  if (!text) return "";
  return String(text).replace(/[<>"']/g, '');
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatContentRef.value) {
      chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight;
    }
  });
}

// 发送快捷问题
function sendQuickQuestion(question) {
  inputMessage.value = question;
  handleSendMessage();
}

// 清除对话
function clearChat() {
  messageList.value = [];
  inputMessage.value = "";
}

// 复制文本
function copyText(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      ElMessage.success("已复制到剪贴板");
    });
  } else {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    ElMessage.success("已复制到剪贴板");
  }
}

// 发送消息
async function handleSendMessage() {
  const message = inputMessage.value.trim();
  if (!message || loading.value) return;

  // 添加用户消息
  messageList.value.push({
    role: "user",
    content: message,
    time: getCurrentTime(),
  });
  inputMessage.value = "";
  scrollToBottom();

  // 添加AI消息（占位）
  const aiMsgIndex = messageList.value.length;
  messageList.value.push({
    role: "assistant",
    content: "",
    time: getCurrentTime(),
    loading: true,
  });
  scrollToBottom();

  // 设置加载状态
  loading.value = true;

  try {
    // 使用新的流式API请求接口
    await canteenAgentChat(
      { message: message, useKnowledge: true },
      // 流式回调：每次收到新内容时更新消息
      (fullText) => {
        if (messageList.value[aiMsgIndex]) {
          messageList.value[aiMsgIndex].content = fullText;
          messageList.value[aiMsgIndex].loading = false;
          scrollToBottom();
        }
      },
      // 超时时间：120秒
      120000
    );

    // 检查是否有内容返回
    if (!messageList.value[aiMsgIndex] || !messageList.value[aiMsgIndex].content) {
      messageList.value[aiMsgIndex].content = "（未能获取有效回复，请重试）";
      messageList.value[aiMsgIndex].loading = false;
    }
  } catch (error) {
    console.error("对话失败:", error);
    if (messageList.value[aiMsgIndex]) {
      messageList.value[aiMsgIndex].content =
        "⚠️ 对话失败：" + (error.message || "网络错误，请检查后端服务是否正常运行");
      messageList.value[aiMsgIndex].loading = false;
    }
  } finally {
    loading.value = false;
    scrollToBottom();
  }
}

// 初始化
onMounted(() => {
  // 页面加载完成
});

// 监听消息变化，自动滚动
watch(
  () => messageList.value.length,
  () => {
    scrollToBottom();
  }
);
</script>

<style scoped>
.chat-container {
  padding: 0;
  height: calc(100vh - 80px);
  background: #f5f7fa;
}

.chat-main {
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-left: 8px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  background: #f5f7fa;
}

.chat-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100%;
}

.chat-content.is-empty {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.welcome-screen {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.welcome-screen h2 {
  color: #303133;
  margin-bottom: 10px;
}

.welcome-screen p {
  color: #909399;
  margin-bottom: 30px;
}

.quick-questions {
  margin-top: 30px;
  max-width: 800px;
}

.quick-title {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.question-card {
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  font-size: 14px;
  color: #303133;
  text-align: left;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  background: #ecf5ff;
  color: #409eff;
}

.message-row {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.message-user {
  flex-direction: row-reverse;
}

.message-ai {
  flex-direction: row;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-user {
  background: #409eff;
}

.avatar-ai {
  background: #67c23a;
}

.message-content-wrapper {
  max-width: 75%;
}

.message-sender {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.message-time {
  margin-left: 10px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
}

.message-user .message-bubble {
  background: #409eff;
  color: white;
  border-top-right-radius: 4px;
}

.message-ai .message-bubble {
  background: white;
  color: #303133;
  border-top-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.user-text {
  white-space: pre-wrap;
}

.ai-text {
  white-space: pre-wrap;
}

/* AI回复中的图片样式 */
.ai-image-wrapper {
  margin: 12px 0;
  text-align: center;
  max-width: 100%;
  overflow: hidden;
}

.ai-content-image {
  max-width: 100%;
  max-height: 200px;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  object-fit: contain;
  display: inline-block;
}

.typing-indicator {
  display: inline-flex;
  gap: 4px;
  padding: 5px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #c0c4cc;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-4px); }
}

.message-footer {
  margin-top: 8px;
}

.chat-input-area {
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 15px 25px;
  flex-shrink: 0;
}

.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.hint-text {
  font-size: 12px;
  color: #909399;
}

.knowledge-content {
  min-height: 400px;
}

.knowledge-content .tab-content {
  max-height: 500px;
  overflow-y: auto;
}

.knowledge-content pre {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.8;
  color: #303133;
}

/* 滚动条样式 */
.chat-history::-webkit-scrollbar,
.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track,
.chat-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb,
.chat-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb:hover,
.chat-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式 */
@media (max-width: 768px) {
  .question-grid {
    grid-template-columns: 1fr;
  }

  .message-content-wrapper {
    max-width: 85%;
  }

  .chat-header {
    padding: 12px 15px;
  }

  .chat-input-area {
    padding: 12px 15px;
  }
}

/* AI 消息内容增强 - 图片展示 */
.ai-content {
  white-space: normal;
  word-break: break-word;
  line-height: 1.7;
}

.ai-content :deep(.ai-image-wrapper) {
  display: block;
  margin: 12px 0;
  text-align: center;
  max-width: 100%;
  overflow: hidden;
}

.ai-content :deep(.ai-content-image) {
  max-width: 100%;
  max-height: 200px;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  object-fit: contain;
  display: inline-block;
}

.ai-content :deep(.ai-image) {
  max-width: 100%;
  max-height: 200px;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  object-fit: contain;
  display: inline-block;
}

.ai-content :deep(.ai-image:hover) {
  transform: scale(1.02);
}
</style>

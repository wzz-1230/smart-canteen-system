<template>
  <div class="swagger-container">
    <iframe
      :src="swaggerUrl"
      frameborder="0"
      style="width: 100%; height: 100%; min-height: 800px;"
      title="Swagger API 文档"
    ></iframe>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const swaggerUrl = ref('')

onMounted(() => {
  // 使用 Vite 代理：/dev-api → http://127.0.0.1:9099
  // 后端 FastAPI Swagger UI 端点是 /docs
  const baseApi = import.meta.env.VITE_APP_BASE_API || '/dev-api'
  swaggerUrl.value = baseApi + '/docs'
  // 注意：由于 Swagger UI 本身是静态页面，iframe 的 src 需要直接指向后端
  // 但 Vite 代理会把 /dev-api 前缀去掉，转发到 9099 端口
  // 为确保 Swagger UI 的资源正确加载，直接使用绝对地址
  swaggerUrl.value = 'http://127.0.0.1:9099/docs'
})
</script>

<style scoped>
.swagger-container {
  width: 100%;
  height: 100%;
  min-height: 800px;
}
</style>

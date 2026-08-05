<template>
  <div :style="{ height: height }" v-loading="loading" element-loading-text="正在加载页面，请稍候！">
    <iframe
      v-if="iframeSrc"
      :id="iframeId"
      style="width: 100%; height: 100%; border: 0"
      :src="iframeSrc"
      ref="iframeRef"
      frameborder="no"
      border="0"
      marginwidth="0"
      marginheight="0"
      framespacing="0"
      allowfullscreen="true"
    ></iframe>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const props = defineProps({
  src: {
    type: String,
    default: ''
  },
  iframeId: {
    type: String,
    default: ''
  }
})

const loading = ref(true)
const iframeRef = ref(null)

const height = computed(() => {
  return (document.documentElement.clientHeight - 94.5) + 'px'
})

const iframeSrc = computed(() => {
  if (props.src) return props.src
  if (route.meta && route.meta.link) return route.meta.link
  return ''
})

function onResize() {
  // 响应窗口大小变化
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  if (iframeRef.value) {
    iframeRef.value.onload = () => {
      loading.value = false
    }
  } else {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

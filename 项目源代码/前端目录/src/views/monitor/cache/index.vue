<template>
  <div class="app-container">
    <el-row :gutter="10">
      <el-col :span="12" class="card-box">
        <el-card>
          <template #header>
            <el-icon><DataAnalysis /></el-icon>
            <span style="margin-left: 8px;">缓存状态</span>
          </template>
          <el-table :data="cacheStats" size="small" border>
            <el-table-column prop="name" label="属性" width="150" />
            <el-table-column prop="value" label="值" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12" class="card-box">
        <el-card>
          <template #header>
            <el-icon><Coin /></el-icon>
            <span style="margin-left: 8px;">内存使用</span>
          </template>
          <el-table :data="memoryStats" size="small" border>
            <el-table-column prop="name" label="属性" width="150" />
            <el-table-column prop="value" label="值" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10">
      <el-col :span="24" class="card-box">
        <el-card>
          <template #header>
            <el-row :gutter="10">
              <el-col :span="12">
                <el-icon><Grid /></el-icon>
                <span style="margin-left: 8px;">缓存键列表</span>
              </el-col>
              <el-col :span="12">
                <el-button type="primary" size="small" @click="getCacheList" style="float: right; margin-right: 8px;">刷新</el-button>
                <el-button type="danger" size="small" @click="clearCache" style="float: right; margin-right: 8px;">清空缓存</el-button>
              </el-col>
            </el-row>
          </template>
          <el-table :data="cacheList" border v-loading="loading" size="small">
            <el-table-column type="index" label="序号" width="80" align="center" />
            <el-table-column prop="key" label="缓存键" width="200" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="ttl" label="剩余时间(秒)" width="150" />
            <el-table-column prop="size" label="大小" width="120" />
            <el-table-column label="操作" align="center" width="150">
              <template #default="scope">
                <el-button type="danger" size="small" @click="deleteCache(scope.row.key)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, Coin, Grid } from '@element-plus/icons-vue'

const loading = ref(false)
const cacheStats = ref([])
const memoryStats = ref([])
const cacheList = ref([])

function getCacheList() {
  loading.value = true
  // 模拟缓存数据
  setTimeout(() => {
    cacheList.value = [
      { key: 'login_tokens:*', type: 'hash', ttl: '-1', size: '512B' },
      { key: 'captcha_codes:*', type: 'string', ttl: '300', size: '128B' },
      { key: 'sys_dict:*', type: 'hash', ttl: '-1', size: '2KB' },
      { key: 'sys_config:*', type: 'hash', ttl: '-1', size: '1KB' },
    ]
    cacheStats.value = [
      { name: '服务状态', value: '运行中 (端口 6379)' },
      { name: 'Redis 版本', value: '5.0.14' },
      { name: '已连接客户端', value: '3' },
      { name: '运行时间', value: '2小时15分' },
      { name: '总命令数', value: '1,234' },
    ]
    memoryStats.value = [
      { name: '已用内存', value: '2.5 MB' },
      { name: '内存峰值', value: '3.1 MB' },
      { name: '可用内存', value: '512 MB' },
      { name: '内存占用率', value: '0.5%' },
    ]
    loading.value = false
  }, 300)
}

function deleteCache(key) {
  ElMessageBox.confirm(`确定删除缓存键 "${key}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    // 实际项目中应该调用后端 API 删除缓存
    // listCache.del(key)
    cacheList.value = cacheList.value.filter(item => item.key !== key)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function clearCache() {
  ElMessageBox.confirm('确定要清空所有缓存吗？此操作不可恢复！', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    cacheList.value = []
    cacheStats.value = []
    memoryStats.value = []
    ElMessage.success('清空成功')
  }).catch(() => {})
}

onMounted(() => {
  getCacheList()
})
</script>

<style scoped>
.card-box {
  margin-bottom: 15px;
}
</style>

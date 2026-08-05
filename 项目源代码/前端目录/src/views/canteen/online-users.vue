<template>
  <div class="app-container">
    <div class="stats-card">
      <div class="stat-item">
        <div class="stat-value">{{ onlineCount }}</div>
        <div class="stat-label">在线用户</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ totalCount }}</div>
        <div class="stat-label">总用户数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ todayLogin }}</div>
        <div class="stat-label">今日登录</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ avgDuration }}</div>
        <div class="stat-label">平均在线时长</div>
      </div>
    </div>

    <div class="table-container">
      <div class="search-bar">
        <el-input v-model="searchText" placeholder="搜索用户名" class="search-input" @keyup.enter="loadOnlineUsers"></el-input>
        <el-button type="primary" @click="refresh">刷新</el-button>
        <el-button type="danger" @click="forceLogout">强制下线</el-button>
      </div>

      <el-table :data="onlineUsers" border style="width: 100%">
        <el-table-column prop="userId" label="用户ID" width="100"></el-table-column>
        <el-table-column prop="username" label="用户名" width="120"></el-table-column>
        <el-table-column prop="nickName" label="昵称" width="120"></el-table-column>
        <el-table-column prop="ipAddress" label="IP地址" width="150"></el-table-column>
        <el-table-column prop="loginTime" label="登录时间" width="180"></el-table-column>
        <el-table-column prop="onlineDuration" label="在线时长" width="120"></el-table-column>
        <el-table-column prop="browser" label="浏览器" width="150"></el-table-column>
        <el-table-column prop="os" label="操作系统" width="120"></el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" type="danger" @click="handleForceLogout(scope.row)">强制下线</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const searchText = ref('')
const onlineUsers = ref([])

const onlineCount = computed(() => onlineUsers.value.length)
const totalCount = ref(128)
const todayLogin = ref(45)
const avgDuration = ref('1小时35分钟')

const mockUsers = [
  { userId: '1', username: 'admin', nickName: '超级管理员', ipAddress: '10.37.151.134', loginTime: '2024-06-12 08:30:00', onlineDuration: '2小时15分', browser: 'Chrome', os: 'Windows 10' },
  { userId: '2', username: 'zhangsan', nickName: '张三', ipAddress: '10.37.151.135', loginTime: '2024-06-12 09:15:00', onlineDuration: '1小时30分', browser: 'Firefox', os: 'Windows 11' },
  { userId: '3', username: 'lisi', nickName: '李四', ipAddress: '10.37.151.136', loginTime: '2024-06-12 10:00:00', onlineDuration: '30分钟', browser: 'Edge', os: 'Windows 10' },
  { userId: '4', username: 'wangwu', nickName: '王五', ipAddress: '10.37.151.137', loginTime: '2024-06-12 10:20:00', onlineDuration: '10分钟', browser: 'Chrome', os: 'macOS' },
  { userId: '5', username: 'zhaoliu', nickName: '赵六', ipAddress: '10.37.151.138', loginTime: '2024-06-12 08:00:00', onlineDuration: '2小时45分', browser: 'Safari', os: 'macOS' },
  { userId: '6', username: 'sunba', nickName: '孙八', ipAddress: '10.37.151.139', loginTime: '2024-06-12 09:30:00', onlineDuration: '1小时', browser: 'Chrome', os: 'Linux' }
]

const loadOnlineUsers = () => {
  onlineUsers.value = mockUsers.filter(item => {
    return !searchText.value || item.username.includes(searchText.value) || item.nickName.includes(searchText.value)
  })
}

const refresh = () => {
  ElMessage.success('已刷新在线用户列表')
  loadOnlineUsers()
}

const forceLogout = () => {
  ElMessage.warning('已强制所有用户下线')
  onlineUsers.value = []
}

const handleForceLogout = (row) => {
  ElMessage.success(`已强制 ${row.nickName} 下线`)
  onlineUsers.value = onlineUsers.value.filter(u => u.userId !== row.userId)
}

onMounted(() => {
  loadOnlineUsers()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.stats-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  color: #fff;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.table-container {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.search-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input {
  width: 250px;
}
</style>

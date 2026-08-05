<template>
  <div class="app-container">
    <div class="search-bar">
      <el-input v-model="searchText" placeholder="搜索菜品" class="search-input" @keyup.enter="searchMenu" clearable>
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="selectedType" placeholder="选择类型" class="type-select" @change="searchMenu" clearable>
        <el-option label="全部" value=""></el-option>
        <el-option label="热菜" value="0"></el-option>
        <el-option label="凉菜" value="1"></el-option>
        <el-option label="主食" value="2"></el-option>
        <el-option label="汤品" value="3"></el-option>
        <el-option label="饮品" value="4"></el-option>
      </el-select>
      <el-select v-model="selectedTable" placeholder="选择餐桌（可选）" class="table-select" clearable>
        <el-option label="不选择餐桌" value=""></el-option>
        <el-option v-for="table in tableList" :key="table.tableId" :label="table.tableName + ' (' + table.tableNo + ')'" :value="table.tableId"></el-option>
      </el-select>
      <el-button type="primary" @click="searchMenu">
        <el-icon style="margin-right: 4px"><Search /></el-icon>
        搜索
      </el-button>
    </div>

    <div class="menu-grid">
      <div v-for="item in menuList" :key="item.menuId" class="menu-card" @click="addToCart(item)">
        <div class="menu-image">
          <img v-if="imageOf(item)" :src="imageOf(item)" :alt="item.menuName" @error="onImageError($event)">
          <div v-else class="no-image">图片未上传</div>
        </div>
        <div class="menu-info">
          <h3 class="menu-name">{{ item.menuName }}</h3>
          <p class="menu-desc">{{ item.description }}</p>
          <div class="menu-footer">
            <span class="menu-price">¥{{ item.price.toFixed(2) }}</span>
            <span class="menu-type">{{ getMenuTypeName(item.menuType) }}</span>
          </div>
        </div>
        <div class="add-btn">
          <el-button size="small" type="primary" @click.stop="addToCart(item)">+</el-button>
        </div>
        <div v-if="getCartQty(item.menuId) > 0" class="cart-badge">{{ getCartQty(item.menuId) }}</div>
      </div>
    </div>

    <div v-if="cartItems.length > 0" class="cart-panel">
      <div class="cart-header">
        <span>购物车 ({{ cartItems.length }})</span>
        <el-button size="small" type="text" @click="clearCart">清空</el-button>
      </div>
      <div class="cart-list">
        <div v-for="item in cartItems" :key="item.menuId" class="cart-item">
          <span class="cart-name">{{ item.menuName }}</span>
          <span class="cart-price">¥{{ item.price.toFixed(2) }}</span>
          <div class="cart-qty">
            <el-button size="mini" @click="decreaseQty(item)">-</el-button>
            <span>{{ item.qty }}</span>
            <el-button size="mini" @click="increaseQty(item)">+</el-button>
          </div>
        </div>
      </div>
      <div class="cart-footer">
        <div class="footer-left">
          <span class="total-label">合计:</span>
          <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
        </div>
        <el-button type="primary" size="large" @click="submitOrder" :loading="submitting">提交订单</el-button>
      </div>
    </div>

    <el-dialog v-model="showOrderSuccess" title="订单提交成功" width="400px" center>
      <div class="success-content">
        <div class="success-icon">
          <el-icon :size="48" color="#67c23a"><CircleCheckFilled /></el-icon>
        </div>
        <h3>订单提交成功！</h3>
        <p>订单编号：{{ orderNo }}</p>
        <p>订单金额：¥{{ orderAmount.toFixed(2) }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showOrderSuccess = false; clearCart()">继续点单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { CircleCheckFilled, Search } from '@element-plus/icons-vue';
import { listMenu, addOrder, listTable } from '@/api/canteen/canteen';
import useUserStore from '@/store/modules/user';
const userStore = useUserStore();
const searchText = ref('');
const selectedType = ref('');
const selectedTable = ref('');
const menuList = ref([]);
const tableList = ref([]);
const cartItems = ref([]);
const submitting = ref(false);
const showOrderSuccess = ref(false);
const orderNo = ref('');
const orderAmount = ref(0);
const totalPrice = computed(() => {
 return cartItems.value.reduce((sum, item) => sum + item.price * item.qty, 0);
});
const getMenuTypeName = (type) => {
 const typeMap = {
 '0': '热菜',
 '1': '凉菜',
 '2': '主食',
 '3': '汤品',
 '4': '饮品'
 };
 return typeMap[type] || '其他';
};
const getFoodImage = (name) => {
  // 已弃用：图片完全由后端通过 imageUrl 字段提供，无匹配时前端显示"图片未上传"占位
  return '';
};
const imageOf = (item) => {
  if (!item) return ''
  const url = item.imageUrl
  if (!url) return ''
  const trimmed = String(url).trim()
  if (!trimmed) return ''
  // 完整URL、/static/ 相对路径、文件名三种情况处理
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed
  }
  if (trimmed.startsWith('/static/')) {
    return trimmed
  }
  if (trimmed.startsWith('/')) {
    return '/static/canteen-menu-images/' + trimmed.slice(1)
  }
  // 只有文件名的情况（如 "红烧肉.jpg"）
  return '/static/canteen-menu-images/' + trimmed
};
const onImageError = (event) => {
  if (!event || !event.target) return;
  const img = event.target;
  img.style.display = 'none';
  const wrapper = img.parentElement;
  if (wrapper) {
    const placeholder = document.createElement('div');
    placeholder.className = 'no-image';
    placeholder.textContent = '图片未上传';
    wrapper.appendChild(placeholder);
  }
};
const getCartQty = (menuId) => {
 const item = cartItems.value.find(i => i.menuId === menuId);
 return item ? item.qty : 0;
};
const searchMenu = async () => {
 // 构造干净的查询参数：只有有值时才发送
 const params = {};
 if (searchText.value && searchText.value.trim()) {
  params.menuName = searchText.value.trim();
 }
 if (selectedType.value !== '' && selectedType.value !== undefined && selectedType.value !== null) {
  params.menuType = String(selectedType.value);
 }
 params.pageSize = 40;
 try {
  const response = await listMenu(params);
  if (response && response.rows) {
   menuList.value = response.rows;
  }
  else {
   menuList.value = [];
  }
 }
 catch (error) {
  console.error('获取菜品列表失败:', error);
  menuList.value = [];
  ElMessage.error('获取菜品列表失败，请重试');
 }
};
const loadTables = async () => {
 try {
 const response = await listTable({});
 if (response && response.rows) {
 tableList.value = response.rows.filter(t => t.tableStatus === '0');
 }
 }
 catch (error) {
 console.error('获取餐桌列表失败:', error);
 }
};
const addToCart = (item) => {
 const existing = cartItems.value.find(i => i.menuId === item.menuId);
 if (existing) {
 existing.qty++;
 }
 else {
 cartItems.value.push({ ...item, qty: 1 });
 }
};
const decreaseQty = (item) => {
 if (item.qty > 1) {
 item.qty--;
 }
 else {
 cartItems.value = cartItems.value.filter(i => i.menuId !== item.menuId);
 }
};
const increaseQty = (item) => {
 item.qty++;
};
const clearCart = () => {
 cartItems.value = [];
};
const submitOrder = async () => {
 if (cartItems.value.length === 0) {
  ElMessage.warning('请先选择菜品');
  return;
 }
 submitting.value = true;
 try {
  const items = cartItems.value.map(item => ({
   menu_id: item.menuId,
   menu_name: item.menuName,
   price: item.price,
   quantity: item.qty,
   amount: item.price * item.qty
  }));
  const orderData = {
   userId: userStore.id || 1,
   tableId: selectedTable.value ? parseInt(selectedTable.value) : null,
   items: items,
   remark: ''
  };
 const response = await addOrder(orderData);
if (response && (response.isSuccess || response.is_success || response.success)) {
 orderNo.value = response.result?.orderNo || '未知';
 orderAmount.value = totalPrice.value;
 showOrderSuccess.value = true;
 ElMessage.success('订单提交成功');
}
else {
 ElMessage.error(response?.message || '订单提交失败');
}
 }
 catch (error) {
 console.error('提交订单失败:', error);
 ElMessage.error('订单提交失败，请重试');
 }
 finally {
 submitting.value = false;
 }
};
onMounted(() => {
 searchMenu();
 loadTables();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fa;
}

.search-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  width: 250px;
}

.type-select, .table-select {
  width: 140px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  padding-bottom: 120px;
}

.menu-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  position: relative;
  transition: all 0.2s;
  cursor: pointer;
}

.menu-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.menu-image img {
  width: 100%;
  height: 160px;
  object-fit: cover;
}
.no-image {
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
  background: #f5f7fa;
  letter-spacing: 2px;
}

.menu-info {
  padding: 14px;
}

.menu-name {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 6px 0;
  color: #303133;
}

.menu-desc {
  font-size: 13px;
  color: #909399;
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-price {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

.menu-type {
  font-size: 12px;
  color: #67c23a;
  background: #f0f9eb;
  padding: 2px 8px;
  border-radius: 4px;
}

.add-btn {
  position: absolute;
  top: 12px;
  right: 12px;
}

.add-btn .el-button {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
}

.cart-badge {
  position: absolute;
  top: 12px;
  right: 52px;
  background: #f56c6c;
  color: #fff;
  font-size: 12px;
  min-width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  border-radius: 10px;
  padding: 0 5px;
}

.cart-panel {
  position: fixed;
  bottom: 0;
  left: 220px;
  right: 0;
  background: #fff;
  border-top: 1px solid #ebeef5;
  padding: 15px 24px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
}

.cart-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}

.cart-list {
  max-height: 160px;
  overflow-y: auto;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed #ebeef5;
}

.cart-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.cart-price {
  color: #f56c6c;
  font-weight: 600;
  margin-right: 16px;
  font-size: 14px;
}

.cart-qty {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cart-qty span {
  min-width: 24px;
  text-align: center;
  font-size: 14px;
}

.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.footer-left {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.total-label {
  font-size: 14px;
  color: #606266;
}

.total-price {
  font-size: 22px;
  font-weight: bold;
  color: #f56c6c;
}

.success-content {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  margin-bottom: 16px;
}

.success-content h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #303133;
}

.success-content p {
  margin: 6px 0;
  font-size: 14px;
  color: #606266;
}
</style>

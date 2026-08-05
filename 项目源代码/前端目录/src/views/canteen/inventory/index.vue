<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="物品名称" prop="itemName">
        <el-input
          v-model="queryParams.itemName"
          placeholder="请输入物品名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="物品类型" prop="itemType">
        <el-select v-model="queryParams.itemType" placeholder="请选择" clearable style="width: 140px">
          <el-option label="全部" value="" />
          <el-option label="食材" value="0" />
          <el-option label="调料" value="1" />
          <el-option label="餐具" value="2" />
          <el-option label="饮品" value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="正常" value="0" />
          <el-option label="预警" value="1" />
          <el-option label="缺货" value="2" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['system:canteen:inventory:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasPermi="['system:canteen:inventory:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['system:canteen:inventory:delete']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="inventoryList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="记录编号" align="center" prop="recordId" width="80" v-if="columns.recordId.visible" />
      <el-table-column label="物品名称" align="center" prop="itemName" v-if="columns.itemName.visible" :show-overflow-tooltip="true" />
      <el-table-column label="类型" align="center" v-if="columns.itemType.visible" width="80">
        <template #default="scope">{{ getItemTypeLabel(scope.row.itemType) }}</template>
      </el-table-column>
      <el-table-column label="初始数量" align="center" prop="initialQuantity" v-if="columns.initialQuantity.visible" width="90" />
      <el-table-column label="入库" align="center" prop="inQuantity" v-if="columns.inQuantity.visible" width="80" />
      <el-table-column label="出库" align="center" prop="outQuantity" v-if="columns.outQuantity.visible" width="80" />
      <el-table-column label="剩余" align="center" prop="remainingQuantity" v-if="columns.remainingQuantity.visible" width="80">
        <template #default="scope">
          <span :style="{ color: scope.row.remainingQuantity < 10 ? '#f56c6c' : '#303133' }">{{ scope.row.remainingQuantity }}</span>
        </template>
      </el-table-column>
      <el-table-column label="单位" align="center" prop="unit" v-if="columns.unit.visible" width="70" />
      <el-table-column label="单价" align="center" prop="unitPrice" v-if="columns.unitPrice.visible" width="90">
        <template #default="scope">{{ scope.row.unitPrice ? scope.row.unitPrice.toFixed(2) : '0.00' }}</template>
      </el-table-column>
      <el-table-column label="总价值" align="center" prop="totalValue" v-if="columns.totalValue.visible" width="100">
        <template #default="scope">{{ scope.row.totalValue ? scope.row.totalValue.toFixed(2) : '0.00' }}</template>
      </el-table-column>
      <el-table-column label="周转率" align="center" prop="turnoverRate" v-if="columns.turnoverRate.visible" width="80">
        <template #default="scope">{{ scope.row.turnoverRate ? scope.row.turnoverRate.toFixed(2) + '%' : '0.00%' }}</template>
      </el-table-column>
      <el-table-column label="状态" align="center" v-if="columns.status.visible" width="80">
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.status)" size="small">{{ getStatusLabel(scope.row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="记录日期" align="center" prop="recordDate" v-if="columns.recordDate.visible" width="160">
        <template #default="scope">{{ parseTime(scope.row.recordDate) }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:canteen:inventory:edit']"></el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:canteen:inventory:delete']"></el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form :model="form" :rules="rules" ref="inventoryRef" label-width="80px">
        <el-form-item label="物品名称" prop="itemName">
          <el-input v-model="form.itemName" placeholder="请输入物品名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="物品类型" prop="itemType">
          <el-select v-model="form.itemType" placeholder="请选择">
            <el-option label="食材" value="0" />
            <el-option label="调料" value="1" />
            <el-option label="餐具" value="2" />
            <el-option label="饮品" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始数量" prop="initialQuantity">
          <el-input-number v-model="form.initialQuantity" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="入库数量" prop="inQuantity">
          <el-input-number v-model="form.inQuantity" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="出库数量" prop="outQuantity">
          <el-input-number v-model="form.outQuantity" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="剩余数量" prop="remainingQuantity">
          <el-input-number v-model="form.remainingQuantity" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如：个/斤/箱" maxlength="20" />
        </el-form-item>
        <el-form-item label="单价" prop="unitPrice">
          <el-input-number v-model="form.unitPrice" :min="0" :step="0.5" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="总价值" prop="totalValue">
          <el-input-number v-model="form.totalValue" :min="0" :step="1" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="周转率" prop="turnoverRate">
          <el-input-number v-model="form.turnoverRate" :min="0" :step="1" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="0">正常</el-radio>
            <el-radio label="1">预警</el-radio>
            <el-radio label="2">缺货</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Inventory">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listInventory, getInventory, addInventory, updateInventory, delInventory } from '@/api/canteen/canteen'

const { proxy } = getCurrentInstance()

const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref('')
const open = ref(false)
const inventoryList = ref([])

const columns = ref({
  recordId: { visible: true },
  itemName: { visible: true },
  itemType: { visible: true },
  initialQuantity: { visible: true },
  inQuantity: { visible: true },
  outQuantity: { visible: true },
  remainingQuantity: { visible: true },
  unit: { visible: true },
  unitPrice: { visible: true },
  totalValue: { visible: true },
  turnoverRate: { visible: true },
  status: { visible: true },
  recordDate: { visible: true }
})

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    itemName: undefined,
    itemType: undefined,
    status: undefined
  },
  rules: {
    itemName: [{ required: true, message: '物品名称不能为空', trigger: 'blur' }],
    itemType: [{ required: true, message: '物品类型不能为空', trigger: 'change' }]
  }
})

const { queryParams, form, rules } = toRefs(data)
const inventoryRef = ref()
const queryRef = ref()

function getItemTypeLabel(type) {
  const typeMap = { '0': '食材', '1': '调料', '2': '餐具', '3': '饮品' }
  return typeMap[type] || '其他'
}

function getStatusLabel(status) {
  const statusMap = { '0': '正常', '1': '预警', '2': '缺货' }
  return statusMap[status] || '未知'
}

function getStatusTagType(status) {
  if (status === '0') return 'success'
  if (status === '1') return 'warning'
  if (status === '2') return 'danger'
  return 'info'
}

/** 查询库存列表 */
function getList() {
  loading.value = true
  listInventory(queryParams.value).then((response) => {
    inventoryList.value = response.rows || []
    total.value = response.total || 0
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

/** 表单重置 */
function reset() {
  form.value = {
    recordId: undefined,
    itemName: '',
    itemType: '0',
    initialQuantity: 0,
    inQuantity: 0,
    outQuantity: 0,
    remainingQuantity: 0,
    unit: '个',
    unitPrice: 0,
    totalValue: 0,
    turnoverRate: 0,
    status: '0',
    remark: ''
  }
  proxy.resetForm('inventoryRef')
}

/** 搜索 */
function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

/** 重置 */
function resetQuery() {
  proxy.resetForm('queryRef')
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.recordId)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

/** 新增按钮 */
function handleAdd() {
  reset()
  open.value = true
  title.value = '添加库存'
}

/** 修改按钮 */
function handleUpdate(row) {
  reset()
  const recordId = row.recordId || ids.value[0]
  getInventory(recordId).then((response) => {
    form.value = response.data || {}
    open.value = true
    title.value = '修改库存'
  })
}

/** 提交按钮 */
function submitForm() {
  inventoryRef.value.validate((valid) => {
    if (valid) {
      if (form.value.recordId !== undefined && form.value.recordId !== null) {
        updateInventory(form.value).then((response) => {
          if (response.code === 200) {
            ElMessage.success('修改成功')
            open.value = false
            getList()
          }
        })
      } else {
        addInventory(form.value).then((response) => {
          if (response.code === 200) {
            ElMessage.success('新增成功')
            open.value = false
            getList()
          }
        })
      }
    }
  })
}

/** 删除按钮 */
function handleDelete(row) {
  const recordIds = row.recordId || ids.value
  ElMessageBox.confirm('是否确认删除库存记录?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return delInventory(recordIds)
  }).then((response) => {
    if (response.code === 200) {
      getList()
      ElMessage.success('删除成功')
    }
  }).catch(() => {})
}

onMounted(() => {
  getList()
})
</script>

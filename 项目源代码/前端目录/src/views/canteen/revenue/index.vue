<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="项目名称" prop="itemName">
        <el-input
          v-model="queryParams.itemName"
          placeholder="请输入项目名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="类型" prop="recordType">
        <el-select v-model="queryParams.recordType" placeholder="请选择" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="收入" value="0" />
          <el-option label="支出" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-select v-model="queryParams.category" placeholder="请选择" clearable style="width: 140px">
          <el-option label="全部" value="" />
          <el-option label="销售" value="销售" />
          <el-option label="采购" value="采购" />
          <el-option label="人工" value="人工" />
          <el-option label="水电" value="水电" />
          <el-option label="其他" value="其他" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['system:canteen:revenue:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasPermi="['system:canteen:revenue:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['system:canteen:revenue:delete']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="revenueList" @selection-change="handleSelectionChange" :summary-method="getSummaries" show-summary>
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="记录编号" align="center" prop="recordId" width="80" v-if="columns.recordId.visible" />
      <el-table-column label="类型" align="center" v-if="columns.recordType.visible" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.recordType === '0' ? 'success' : 'danger'" size="small">
            {{ scope.row.recordType === '0' ? '收入' : '支出' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="分类" align="center" prop="category" v-if="columns.category.visible" width="100" />
      <el-table-column label="项目名称" align="center" prop="itemName" v-if="columns.itemName.visible" :show-overflow-tooltip="true" />
      <el-table-column label="金额" align="center" prop="amount" v-if="columns.amount.visible" width="110">
        <template #default="scope">
          <span :style="{ color: scope.row.recordType === '0' ? '#67c23a' : '#f56c6c', fontWeight: 'bold' }">
            {{ scope.row.recordType === '0' ? '+' : '-' }}{{ scope.row.amount ? scope.row.amount.toFixed(2) : '0.00' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="支付方式" align="center" prop="payMethod" v-if="columns.payMethod.visible" width="100" />
      <el-table-column label="关联订单" align="center" prop="relatedOrder" v-if="columns.relatedOrder.visible" :show-overflow-tooltip="true" />
      <el-table-column label="状态" align="center" v-if="columns.status.visible" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'info'" size="small">
            {{ scope.row.status === '0' ? '正常' : '作废' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="记录日期" align="center" prop="recordDate" v-if="columns.recordDate.visible" width="160">
        <template #default="scope">{{ parseTime(scope.row.recordDate) }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:canteen:revenue:edit']"></el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:canteen:revenue:delete']"></el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form :model="form" :rules="rules" ref="revenueRef" label-width="80px">
        <el-form-item label="类型" prop="recordType">
          <el-radio-group v-model="form.recordType">
            <el-radio label="0">收入</el-radio>
            <el-radio label="1">支出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="销售" value="销售" />
            <el-option label="采购" value="采购" />
            <el-option label="人工" value="人工" />
            <el-option label="水电" value="水电" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目名称" prop="itemName">
          <el-input v-model="form.itemName" placeholder="请输入项目名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0" :step="1" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="支付方式" prop="payMethod">
          <el-select v-model="form.payMethod" placeholder="请选择支付方式" clearable style="width: 100%">
            <el-option label="现金" value="现金" />
            <el-option label="微信" value="微信" />
            <el-option label="支付宝" value="支付宝" />
            <el-option label="银行卡" value="银行卡" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联订单" prop="relatedOrder">
          <el-input v-model="form.relatedOrder" placeholder="请输入关联订单编号" maxlength="64" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="0">正常</el-radio>
            <el-radio label="1">作废</el-radio>
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

<script setup name="Revenue">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listRevenueExpense, getRevenueExpense, addRevenueExpense, updateRevenueExpense, delRevenueExpense } from '@/api/canteen/canteen'

const { proxy } = getCurrentInstance()

const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref('')
const open = ref(false)
const revenueList = ref([])

const columns = ref({
  recordId: { visible: true },
  recordType: { visible: true },
  category: { visible: true },
  itemName: { visible: true },
  amount: { visible: true },
  payMethod: { visible: true },
  relatedOrder: { visible: true },
  status: { visible: true },
  recordDate: { visible: true }
})

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    itemName: undefined,
    recordType: undefined,
    category: undefined,
    status: undefined
  },
  rules: {
    recordType: [{ required: true, message: '类型不能为空', trigger: 'change' }],
    category: [{ required: true, message: '分类不能为空', trigger: 'change' }],
    itemName: [{ required: true, message: '项目名称不能为空', trigger: 'blur' }],
    amount: [{ required: true, message: '金额不能为空', trigger: 'blur' }]
  }
})

const { queryParams, form, rules } = toRefs(data)
const revenueRef = ref()
const queryRef = ref()

/** 汇总统计 */
function getSummaries(param) {
  const { columns, data } = param
  const sums = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '合计'
      return
    }
    const values = data.map((item) => Number(item[column.property]))
    if (column.property === 'amount') {
      const income = data.filter((item) => item.recordType === '0').reduce((sum, item) => sum + Number(item.amount), 0)
      const expense = data.filter((item) => item.recordType === '1').reduce((sum, item) => sum + Number(item.amount), 0)
      sums[index] = `收: ¥${income.toFixed(2)} / 支: ¥${expense.toFixed(2)} / 净: ¥${(income - expense).toFixed(2)}`
    } else {
      sums[index] = ''
    }
  })
  return sums
}

/** 查询收支列表 */
function getList() {
  loading.value = true
  listRevenueExpense(queryParams.value).then((response) => {
    revenueList.value = response.rows || []
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
    recordType: '0',
    category: '销售',
    itemName: '',
    amount: 0,
    payMethod: '',
    relatedOrder: '',
    status: '0',
    remark: ''
  }
  proxy.resetForm('revenueRef')
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
  title.value = '添加收支'
}

/** 修改按钮 */
function handleUpdate(row) {
  reset()
  const recordId = row.recordId || ids.value[0]
  getRevenueExpense(recordId).then((response) => {
    form.value = response.data || {}
    open.value = true
    title.value = '修改收支'
  })
}

/** 提交按钮 */
function submitForm() {
  revenueRef.value.validate((valid) => {
    if (valid) {
      if (form.value.recordId !== undefined && form.value.recordId !== null) {
        updateRevenueExpense(form.value).then((response) => {
          if (response.code === 200) {
            ElMessage.success('修改成功')
            open.value = false
            getList()
          }
        })
      } else {
        addRevenueExpense(form.value).then((response) => {
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
  ElMessageBox.confirm('是否确认删除收支记录?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    return delRevenueExpense(recordIds)
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

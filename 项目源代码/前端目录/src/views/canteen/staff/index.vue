<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="员工姓名" prop="staffName">
        <el-input
          v-model="queryParams.staffName"
          placeholder="请输入员工姓名"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="岗位" prop="position">
        <el-select v-model="queryParams.position" placeholder="请选择岗位" clearable style="width: 160px">
          <el-option label="厨师" value="厨师" />
          <el-option label="服务员" value="服务员" />
          <el-option label="收银员" value="收银员" />
          <el-option label="管理员" value="管理员" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 160px">
          <el-option label="在职" value="0" />
          <el-option label="离职" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" icon="Plus" @click="handleAdd" v-hasPermi="['system:canteen:staff:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" icon="Edit" @click="handleUpdate" :disabled="single" v-hasPermi="['system:canteen:staff:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" icon="Delete" @click="handleDelete" :disabled="multiple" v-hasPermi="['system:canteen:staff:remove']">删除</el-button>
      </el-col>
    </el-row>

    <el-table v-loading="loading" :data="staffList" @selection-change="handleSelectionChange" border>
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="员工编号" align="center" prop="staffNo" width="120" />
      <el-table-column label="员工姓名" align="center" prop="staffName" width="120" />
      <el-table-column label="岗位" align="center" prop="position" width="100" />
      <el-table-column label="联系电话" align="center" prop="phone" width="150" />
      <el-table-column label="邮箱" align="center" prop="email" show-overflow-tooltip />
      <el-table-column label="状态" align="center" prop="status" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'info'">
            {{ scope.row.status === '0' ? '在职' : '离职' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="入职日期" align="center" prop="hireDate" width="120" />
      <el-table-column label="创建时间" align="center" prop="createTime" width="180" />
      <el-table-column label="操作" align="center" width="220" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button size="small" type="text" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:canteen:staff:edit']">修改</el-button>
          <el-button size="small" type="text" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:canteen:staff:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      v-model:total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="staffRef" :model="form" :rules="rules" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="员工编号" prop="staffNo">
              <el-input v-model="form.staffNo" placeholder="请输入员工编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="员工姓名" prop="staffName">
              <el-input v-model="form.staffName" placeholder="请输入员工姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="岗位" prop="position">
              <el-select v-model="form.position" placeholder="请选择岗位" style="width: 100%">
                <el-option label="厨师" value="厨师" />
                <el-option label="服务员" value="服务员" />
                <el-option label="收银员" value="收银员" />
                <el-option label="管理员" value="管理员" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期" prop="hireDate">
              <el-date-picker v-model="form.hireDate" type="date" placeholder="请选择入职日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio value="0">在职</el-radio>
                <el-radio value="1">离职</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, toRefs, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listStaff, getStaff, addStaff, updateStaff, delStaff } from '@/api/canteen/canteen'

const { proxy } = getCurrentInstance()

const loading = ref(false)
const showSearch = ref(true)
const staffList = ref([])
const single = ref(true)
const multiple = ref(true)
const ids = ref([])
const total = ref(0)
const title = ref('')
const open = ref(false)

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    staffName: undefined,
    position: undefined,
    status: undefined
  },
  rules: {
    staffName: [{ required: true, message: '员工姓名不能为空', trigger: 'blur' }],
    position: [{ required: true, message: '岗位不能为空', trigger: 'change' }],
    phone: [
      { pattern: /^1[3-9]\d{9}$|^$/, message: '请输入正确的手机号码', trigger: 'blur' }
    ],
    email: [
      { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
    ]
  }
})

const { queryParams, form, rules } = toRefs(data)

/** 查询员工列表 */
function getList() {
  loading.value = true
  listStaff(queryParams.value).then((response) => {
    staffList.value = response.rows || []
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

/** 重置表单 */
function reset() {
  form.value = {
    staffId: undefined,
    staffNo: '',
    staffName: '',
    position: '',
    phone: '',
    email: '',
    status: '0',
    hireDate: '',
    remark: ''
  }
  proxy?.resetForm?.()
}

/** 查询按钮 */
function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

/** 重置按钮 */
function resetQuery() {
  proxy?.resetForm?.()
  queryParams.value.staffName = undefined
  queryParams.value.position = undefined
  queryParams.value.status = undefined
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.staffId)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

/** 新增按钮 */
function handleAdd() {
  reset()
  open.value = true
  title.value = '添加员工'
}

/** 修改按钮 */
function handleUpdate(row) {
  reset();
  const staffId = row.staffId || ids.value;
  getStaff(staffId).then((response) => {
    Object.assign(form.value, response.data);
    open.value = true;
    title.value = '修改员工';
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs.staffRef.validate((valid) => {
    if (valid) {
      if (form.value.staffId != null && form.value.staffId !== '' && form.value.staffId !== undefined) {
        updateStaff(form.value).then(() => {
          ElMessage.success('修改成功')
          open.value = false
          getList()
        })
      } else {
        addStaff(form.value).then(() => {
          ElMessage.success('新增成功')
          open.value = false
          getList()
        })
      }
    }
  })
}

/** 删除按钮 */
function handleDelete(row) {
  const staffIds = row.staffId || ids.value
  ElMessageBox.confirm('是否确认删除所选的员工数据项?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    if (Array.isArray(staffIds) && staffIds.length > 0) {
      const promises = staffIds.map((id) => delStaff(id))
      Promise.all(promises).then(() => {
        ElMessage.success('删除成功')
        getList()
      })
    } else {
      delStaff(staffIds).then(() => {
        ElMessage.success('删除成功')
        getList()
      })
    }
  }).catch(() => {})
}

onMounted(() => {
  getList()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}
</style>

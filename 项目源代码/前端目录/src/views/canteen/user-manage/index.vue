<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="用户账号" prop="userName">
        <el-input
          v-model="queryParams.userName"
          placeholder="请输入用户账号"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="用户昵称" prop="nickName">
        <el-input
          v-model="queryParams.nickName"
          placeholder="请输入用户昵称"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 160px">
          <el-option label="正常" value="0" />
          <el-option label="停用" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" icon="Plus" @click="handleAdd" v-hasPermi="['system:canteen:user:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" icon="Edit" @click="handleUpdate" :disabled="single" v-hasPermi="['system:canteen:user:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="warning" icon="Key" @click="handleResetPwd" :disabled="single" v-hasPermi="['system:canteen:user:edit']">重置密码</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" icon="Delete" @click="handleDelete" :disabled="multiple" v-hasPermi="['system:canteen:user:remove']">删除</el-button>
      </el-col>
    </el-row>

    <el-table v-loading="loading" :data="userList" @selection-change="handleSelectionChange" border>
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="用户账号" align="center" prop="userName" width="140" />
      <el-table-column label="用户昵称" align="center" prop="nickName" width="140" />
      <el-table-column label="邮箱" align="center" prop="email" show-overflow-tooltip />
      <el-table-column label="手机号" align="center" prop="phonenumber" width="140" />
      <el-table-column label="余额" align="center" prop="balance" width="100">
        <template #default="scope">
          <span style="color: #409eff; font-weight: bold">¥ {{ (scope.row.balance ?? 0).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
            {{ scope.row.status === '0' ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180" />
      <el-table-column label="操作" align="center" width="220" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button size="small" type="text" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:canteen:user:edit']">修改</el-button>
          <el-button size="small" type="text" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:canteen:user:remove']">删除</el-button>
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

    <el-dialog :title="title" v-model="open" width="640px" append-to-body>
      <el-form ref="userRef" :model="form" :rules="rules" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="用户账号" prop="userName">
              <el-input v-model="form.userName" placeholder="请输入用户账号" :disabled="form.userId != null && form.userId !== undefined" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户昵称" prop="nickName">
              <el-input v-model="form.nickName" placeholder="请输入用户昵称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row v-if="form.userId == null || form.userId === undefined">
          <el-col :span="12">
            <el-form-item label="初始密码" prop="password">
              <el-input v-model="form.password" placeholder="留空则使用默认123456" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio value="0">正常</el-radio>
                <el-radio value="1">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phonenumber">
              <el-input v-model="form.phonenumber" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="余额" prop="balance">
              <el-input-number v-model="form.balance" :min="0" :precision="2" controls-position="right" style="width: 100%" />
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

    <el-dialog title="重置密码" v-model="resetOpen" width="400px" append-to-body>
      <el-form ref="pwdRef" :model="pwdForm" :rules="pwdRules" label-width="100px">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="pwdForm.password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="pwdForm.confirmPassword" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitPwdForm">确 定</el-button>
          <el-button @click="resetOpen = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, toRefs, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listCanteenUser, getCanteenUser, addCanteenUser, updateCanteenUser, delCanteenUser, resetCanteenUserPwd } from '@/api/canteen/canteen'

const { proxy } = getCurrentInstance()

const loading = ref(false)
const showSearch = ref(true)
const userList = ref([])
const single = ref(true)
const multiple = ref(true)
const ids = ref([])
const total = ref(0)
const title = ref('')
const open = ref(false)
const resetOpen = ref(false)

const data = reactive({
  form: {},
  pwdForm: {
    userId: undefined,
    password: '',
    confirmPassword: ''
  },
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    userName: undefined,
    nickName: undefined,
    status: undefined
  },
  rules: {
    userName: [{ required: true, message: '用户账号不能为空', trigger: 'blur' }],
    nickName: [{ required: true, message: '用户昵称不能为空', trigger: 'blur' }],
    email: [
      { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
    ],
    phonenumber: [
      { pattern: /^1[3-9]\d{9}$|^$/, message: '请输入正确的手机号码', trigger: 'blur' }
    ]
  },
  pwdRules: {
    password: [{ required: true, message: '新密码不能为空', trigger: 'blur' }],
    confirmPassword: [
      { required: true, message: '确认密码不能为空', trigger: 'blur' },
      {
        validator: (rule, value, callback) => {
          if (value !== data.pwdForm.password) {
            callback(new Error('两次输入的密码不一致'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
    ]
  }
})

const { queryParams, form, rules, pwdRules, pwdForm } = toRefs(data)

/** 查询用户列表 */
function getList() {
  loading.value = true
  listCanteenUser(queryParams.value).then((response) => {
    userList.value = response.rows || []
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
    userId: undefined,
    userName: '',
    nickName: '',
    password: '',
    email: '',
    phonenumber: '',
    status: '0',
    balance: 0,
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
  queryParams.value.userName = undefined
  queryParams.value.nickName = undefined
  queryParams.value.status = undefined
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.userId)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

/** 新增按钮 */
function handleAdd() {
  reset()
  open.value = true
  title.value = '添加食堂用户'
}

/** 修改按钮 */
function handleUpdate(row) {
  reset();
  const userId = row.userId || ids.value;
  getCanteenUser(userId).then((response) => {
    Object.assign(form.value, response.data);
    open.value = true;
    title.value = '修改会员';
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs.userRef.validate((valid) => {
    if (valid) {
      if (form.value.userId != null && form.value.userId !== undefined) {
        updateCanteenUser(form.value).then(() => {
          ElMessage.success('修改成功')
          open.value = false
          getList()
        })
      } else {
        addCanteenUser(form.value).then(() => {
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
  const userIds = row.userId || ids.value
  ElMessageBox.confirm('是否确认删除所选的食堂用户数据项?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    if (Array.isArray(userIds) && userIds.length > 0) {
      const promises = userIds.map((id) => delCanteenUser(id))
      Promise.all(promises).then(() => {
        ElMessage.success('删除成功')
        getList()
      })
    } else {
      delCanteenUser(userIds).then(() => {
        ElMessage.success('删除成功')
        getList()
      })
    }
  }).catch(() => {})
}

/** 重置密码 */
function handleResetPwd(row) {
  const userId = row.userId || (ids.value && ids.value[0])
  pwdForm.value.userId = userId
  pwdForm.value.password = ''
  pwdForm.value.confirmPassword = ''
  resetOpen.value = true
}

function submitPwdForm() {
  proxy.$refs.pwdRef.validate((valid) => {
    if (valid) {
      resetCanteenUserPwd(pwdForm.value.userId, pwdForm.value.password).then(() => {
        ElMessage.success('重置成功')
        resetOpen.value = false
      })
    }
  })
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
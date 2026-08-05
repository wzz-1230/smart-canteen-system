<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="菜品名称" prop="menuName">
        <el-input
          v-model="queryParams.menuName"
          placeholder="请输入菜品名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="菜品类型" prop="menuType">
        <el-select v-model="queryParams.menuType" placeholder="请选择" clearable style="width: 160px">
          <el-option label="全部" value="" />
          <el-option label="热菜" value="0" />
          <el-option label="凉菜" value="1" />
          <el-option label="主食" value="2" />
          <el-option label="汤品" value="3" />
          <el-option label="饮品" value="4" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="正常" value="0" />
          <el-option label="下架" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['system:canteen:menu:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasPermi="['system:canteen:menu:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['system:canteen:menu:delete']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="menuList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="菜品编号" align="center" prop="menuId" v-if="columns.menuId.visible" />
      <el-table-column label="菜品名称" align="center" prop="menuName" v-if="columns.menuName.visible" :show-overflow-tooltip="true" />
      <el-table-column label="菜品类型" align="center" v-if="columns.menuType.visible">
        <template #default="scope">{{ getMenuTypeLabel(scope.row.menuType) }}</template>
      </el-table-column>
      <el-table-column label="价格" align="center" prop="price" v-if="columns.price.visible">
        <template #default="scope">{{ scope.row.price.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="状态" align="center" v-if="columns.status.visible">
        <template #default="scope">
          <el-switch v-model="scope.row.status" active-value="0" inactive-value="1" @change="handleStatusChange(scope.row)"></el-switch>
        </template>
      </el-table-column>
      <el-table-column label="排序号" align="center" prop="sortOrder" v-if="columns.sortOrder.visible" />
      <el-table-column label="描述" align="center" prop="description" :show-overflow-tooltip="true" />
      <el-table-column label="图片" align="center" width="120">
        <template #default="scope">
          <el-image
            v-if="scope.row.imageUrl"
            :src="scope.row.imageUrl"
            :preview-src-list="[scope.row.imageUrl]"
            fit="cover"
            style="width: 60px; height: 60px; border-radius: 4px"
          />
          <span v-else style="color: #909399; font-size: 12px">无图片</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" v-if="columns.createTime.visible" width="160">
        <template #default="scope">{{ parseTime(scope.row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:canteen:menu:edit']"></el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:canteen:menu:delete']"></el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form :model="form" :rules="rules" ref="menuRef" label-width="80px">
        <el-form-item label="菜品名称" prop="menuName">
          <el-input v-model="form.menuName" placeholder="请输入菜品名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="菜品类型" prop="menuType">
          <el-select v-model="form.menuType" placeholder="请选择">
            <el-option label="热菜" value="0" />
            <el-option label="凉菜" value="1" />
            <el-option label="主食" value="2" />
            <el-option label="汤品" value="3" />
            <el-option label="饮品" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input v-model.number="form.price" placeholder="请输入价格" type="number" step="0.01" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="form.imageUrl" placeholder="请输入图片URL" maxlength="200" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" maxlength="500"></el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="0">正常</el-radio>
            <el-radio value="1">下架</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="排序号">
          <el-input v-model.number="form.sortOrder" placeholder="请输入排序号" type="number" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注"></el-input>
        </el-form-item>
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

<script setup name="CanteenMenu">
import { ref, reactive, toRefs, getCurrentInstance, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listMenu, getMenu, addMenu, updateMenu, delMenu } from "@/api/canteen/canteen";

const { proxy } = getCurrentInstance() || {};

const menuList = ref([]);
const open = ref(false);
const loading = ref(true);
const menuRef = ref(null);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const menuTypeOptions = {
  "0": "热菜",
  "1": "凉菜",
  "2": "主食",
  "3": "汤品",
  "4": "饮品"
};

const columns = ref({
  menuId: { label: "菜品编号", visible: true },
  menuName: { label: "菜品名称", visible: true },
  menuType: { label: "菜品类型", visible: true },
  price: { label: "价格", visible: true },
  status: { label: "状态", visible: true },
  sortOrder: { label: "排序号", visible: true },
  createTime: { label: "创建时间", visible: true },
});

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    menuName: undefined,
    menuType: undefined,
    status: undefined,
  },
  rules: {
    menuName: [{ required: true, message: "菜品名称不能为空", trigger: "blur" }],
    menuType: [{ required: true, message: "菜品类型不能为空", trigger: "change" }],
    price: [{ required: true, message: "价格不能为空", trigger: "blur" }],
  },
});

const { queryParams, form, rules } = toRefs(data);

const getMenuTypeLabel = (type) => menuTypeOptions[type] || type;

function getList() {
  loading.value = true;
  listMenu(queryParams.value).then((res) => {
    loading.value = false;
    menuList.value = res.rows;
    total.value = res.total;
  });
}

function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

function resetQuery() {
  queryParams.value = {
    pageNum: 1,
    pageSize: 10,
    menuName: undefined,
    menuType: undefined,
    status: undefined,
  };
}

function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.menuId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

function handleDelete(row) {
  const menuIds = row.menuId || ids.value;
  ElMessageBox.confirm('是否确认删除菜品编号为"' + menuIds + '"的数据项？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    delMenu(menuIds).then(() => {
      getList();
      ElMessage.success("删除成功");
    });
  }).catch(() => {});
}

function handleStatusChange(row) {
  let text = row.status === "0" ? "启用" : "下架";
  const oldStatus = row.status;
  ElMessageBox.confirm('确认要"' + text + '"' + row.menuName + '"吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    updateMenu({ menuId: row.menuId, status: row.status }).then(() => {
      ElMessage.success(text + "成功");
    });
  }).catch(() => {
    row.status = oldStatus;
  });
}

function reset() {
  form.value = {
    menuId: undefined,
    menuName: undefined,
    menuType: "0",
    price: undefined,
    imageUrl: "",
    description: "",
    status: "0",
    sortOrder: 0,
    remark: "",
  };
  menuRef.value?.resetFields();
}

function cancel() {
  open.value = false;
  reset();
}

function handleAdd() {
  reset();
  open.value = true;
  title.value = "新增菜品";
}

function handleUpdate(row) {
  reset();
  const menuId = row.menuId || ids.value;
  getMenu(menuId).then((response) => {
    form.value = response.data;
    open.value = true;
    title.value = "修改菜品";
  });
}

function submitForm() {
  proxy.$refs["menuRef"].validate((valid) => {
    if (valid) {
      if (form.value.menuId != undefined) {
        updateMenu(form.value).then(() => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addMenu(form.value).then(() => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

onMounted(() => {
  getList();
});
</script>
<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="餐桌编号" prop="tableNo">
        <el-input
          v-model="queryParams.tableNo"
          placeholder="请输入餐桌编号"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="餐桌名称" prop="tableName">
        <el-input
          v-model="queryParams.tableName"
          placeholder="请输入餐桌名称"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="tableStatus">
        <el-select v-model="queryParams.tableStatus" placeholder="请选择" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="空闲" value="0" />
          <el-option label="占用" value="1" />
          <el-option label="预订" value="2" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['system:canteen:table:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasPermi="['system:canteen:table:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['system:canteen:table:delete']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="tableList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="餐桌编号" align="center" prop="tableId" v-if="columns.tableId.visible" />
      <el-table-column label="桌号" align="center" prop="tableNo" v-if="columns.tableNo.visible" />
      <el-table-column label="餐桌名称" align="center" prop="tableName" v-if="columns.tableName.visible" :show-overflow-tooltip="true" />
      <el-table-column label="容纳人数" align="center" prop="capacity" v-if="columns.capacity.visible" />
      <el-table-column label="状态" align="center" v-if="columns.tableStatus.visible">
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.tableStatus)">{{ getTableStatusLabel(scope.row.tableStatus) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="位置" align="center" prop="location" v-if="columns.location.visible" :show-overflow-tooltip="true" />
      <el-table-column label="创建时间" align="center" prop="createTime" v-if="columns.createTime.visible" width="160">
        <template #default="scope">{{ parseTime(scope.row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:canteen:table:edit']"></el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:canteen:table:delete']"></el-button>
          <el-select v-model="statusSelect[scope.row.tableId]" @change="(val) => handleStatusChange(scope.row.tableId, val)" placeholder="状态">
            <el-option label="空闲" value="0" />
            <el-option label="占用" value="1" />
            <el-option label="预订" value="2" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form :model="form" :rules="rules" ref="tableRef" label-width="80px">
        <el-form-item label="餐桌编号" prop="tableNo">
          <el-input v-model="form.tableNo" placeholder="请输入餐桌编号" maxlength="20" />
        </el-form-item>
        <el-form-item label="餐桌名称">
          <el-input v-model="form.tableName" placeholder="请输入餐桌名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="容纳人数" prop="capacity">
          <el-input v-model.number="form.capacity" placeholder="请输入容纳人数" type="number" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.tableStatus">
            <el-radio value="0">空闲</el-radio>
            <el-radio value="1">占用</el-radio>
            <el-radio value="2">预订</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="位置描述">
          <el-input v-model="form.location" placeholder="请输入位置描述" maxlength="100" />
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

<script setup name="CanteenTable">
import { ref, reactive, toRefs, getCurrentInstance, onMounted } from "vue";
import { listTable, getTable, addTable, updateTable, delTable, updateTableStatus } from "@/api/canteen/canteen";

const { proxy } = getCurrentInstance() || {};

const tableList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const statusSelect = ref({});

const tableStatusOptions = {
  "0": "空闲",
  "1": "占用",
  "2": "预订"
};

const columns = ref({
  tableId: { label: "餐桌编号", visible: true },
  tableNo: { label: "桌号", visible: true },
  tableName: { label: "餐桌名称", visible: true },
  capacity: { label: "容纳人数", visible: true },
  tableStatus: { label: "状态", visible: true },
  location: { label: "位置", visible: true },
  createTime: { label: "创建时间", visible: true },
});

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    tableNo: undefined,
    tableName: undefined,
    tableStatus: undefined,
  },
  rules: {
    tableNo: [{ required: true, message: "餐桌编号不能为空", trigger: "blur" }],
    capacity: [{ required: true, message: "容纳人数不能为空", trigger: "blur" }],
  },
});

const { queryParams, form, rules } = toRefs(data);

const getTableStatusLabel = (status) => tableStatusOptions[status] || status;

const getStatusTagType = (status) => {
  switch (status) {
    case "0": return "success";
    case "1": return "warning";
    case "2": return "info";
    default: return "default";
  }
};

function getList() {
  loading.value = true;
  listTable(queryParams.value).then((res) => {
    loading.value = false;
    tableList.value = res.rows;
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
    tableNo: undefined,
    tableName: undefined,
    tableStatus: undefined,
  };
}

function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.tableId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

function handleDelete(row) {
  const tableIds = row.tableId || ids.value;
  proxy.$modal
    .confirm('是否确认删除餐桌编号为"' + tableIds + '"的数据项？')
    .then(() => delTable(tableIds))
    .then(() => {
      getList();
      proxy.$modal.msgSuccess("删除成功");
    })
    .catch(() => {});
}

function handleStatusChange(tableId, status) {
  updateTableStatus(tableId, status).then(() => {
    proxy.$modal.msgSuccess("状态更新成功");
    getList();
  });
}

function reset() {
  form.value = {
    tableId: undefined,
    tableNo: undefined,
    tableName: "",
    capacity: 4,
    tableStatus: "0",
    location: "",
    remark: "",
  };
  proxy.resetForm("tableRef");
}

function cancel() {
  open.value = false;
  reset();
}

function handleAdd() {
  reset();
  open.value = true;
  title.value = "新增餐桌";
}

function handleUpdate(row) {
  reset();
  const tableId = row.tableId || ids.value;
  getTable(tableId).then((response) => {
    form.value = response.data;
    open.value = true;
    title.value = "修改餐桌";
  });
}

function submitForm() {
  proxy.$refs["tableRef"].validate((valid) => {
    if (valid) {
      if (form.value.tableId != undefined) {
        updateTable(form.value).then(() => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addTable(form.value).then(() => {
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
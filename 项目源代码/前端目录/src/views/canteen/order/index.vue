<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="订单编号" prop="orderNo">
        <el-input
          v-model="queryParams.orderNo"
          placeholder="请输入订单编号"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="订单状态" prop="orderStatus">
        <el-select v-model="queryParams.orderStatus" placeholder="请选择" clearable style="width: 160px">
          <el-option label="全部" value="" />
          <el-option label="待支付" value="0" />
          <el-option label="已支付" value="1" />
          <el-option label="已完成" value="2" />
          <el-option label="已取消" value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="用户ID" prop="userId">
        <el-input
          v-model.number="queryParams.userId"
          placeholder="请输入用户ID"
          clearable
          style="width: 160px"
          type="number"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['system:canteen:order:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasPermi="['system:canteen:order:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['system:canteen:order:delete']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table
      v-loading="loading"
      :data="orderList"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
      style="cursor: pointer"
    >
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="订单编号" align="center" prop="orderId" v-if="columns.orderId.visible" />
      <el-table-column label="订单号" align="center" prop="orderNo" v-if="columns.orderNo.visible" :show-overflow-tooltip="true">
        <template #default="scope">
          <el-link type="primary" :underline="false" @click.stop="handleDetail(scope.row)">
            {{ scope.row.orderNo }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="用户ID" align="center" prop="userId" v-if="columns.userId.visible" />
      <el-table-column label="餐桌ID" align="center" prop="tableId" v-if="columns.tableId.visible" />
      <el-table-column label="订单总额" align="center" prop="totalAmount" v-if="columns.totalAmount.visible">
        <template #default="scope">¥ {{ Number(scope.row.totalAmount).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="订单状态" align="center" v-if="columns.orderStatus.visible" width="110">
        <template #default="scope">
          <el-tag :type="getOrderStatusTagType(scope.row.orderStatus)" effect="light" size="small">
            {{ getOrderStatusLabel(scope.row.orderStatus) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="支付方式" align="center" prop="payMethod" v-if="columns.payMethod.visible" />
      <el-table-column label="创建时间" align="center" prop="createTime" v-if="columns.createTime.visible" width="160">
        <template #default="scope">{{ parseTime(scope.row.createTime) }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="220" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click.stop="handleDetail(scope.row)">查看</el-button>
          <el-button link type="primary" icon="Edit" @click.stop="handleUpdate(scope.row)" v-hasPermi="['system:canteen:order:edit']"></el-button>
          <el-button link type="danger" icon="Delete" @click.stop="handleDelete(scope.row)" v-hasPermi="['system:canteen:order:delete']"></el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form :model="form" :rules="rules" ref="orderRef" label-width="80px">
        <el-form-item label="用户ID" prop="userId">
          <el-input v-model.number="form.userId" placeholder="请输入用户ID" type="number" />
        </el-form-item>
        <el-form-item label="餐桌ID">
          <el-input v-model.number="form.tableId" placeholder="请输入餐桌ID" type="number" />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="form.orderStatus" placeholder="请选择">
            <el-option label="待支付" value="0" />
            <el-option label="已支付" value="1" />
            <el-option label="已完成" value="2" />
            <el-option label="已取消" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-input v-model="form.payMethod" placeholder="请输入支付方式" maxlength="20" />
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

    <el-dialog title="订单详情" v-model="detailOpen" width="780px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单编号">{{ orderDetail.orderInfo?.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="订单ID">{{ orderDetail.orderInfo?.orderId }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getOrderStatusTagType(orderDetail.orderInfo?.orderStatus)" effect="light">
            {{ getOrderStatusLabel(orderDetail.orderInfo?.orderStatus) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="订单总额">
          <span style="color: #f56c6c; font-weight: bold; font-size: 16px;">
            ¥ {{ Number(orderDetail.orderInfo?.totalAmount || 0).toFixed(2) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ orderDetail.orderInfo?.userId }}</el-descriptions-item>
        <el-descriptions-item label="餐桌ID">{{ orderDetail.orderInfo?.tableId || '—' }}</el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ orderDetail.orderInfo?.payMethod || '—' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(orderDetail.orderInfo?.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ orderDetail.orderInfo?.remark || '—' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">菜品明细（共 {{ orderDetail.detailList?.length || 0 }} 项）</el-divider>

      <el-table
        v-if="orderDetail.detailList && orderDetail.detailList.length > 0"
        :data="orderDetail.detailList"
        border
        stripe
        size="default"
        :summary-method="getSummaries"
        show-summary
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="menuName" label="菜品名称" min-width="160" />
        <el-table-column prop="price" label="单价（元）" width="120" align="right">
          <template #default="scope">{{ Number(scope.row.price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column prop="amount" label="金额（元）" width="120" align="right">
          <template #default="scope">{{ Number(scope.row.amount).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="该订单暂无菜品明细" :image-size="80" />

      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="detailOpen = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="CanteenOrder">
import { ref, reactive, toRefs, getCurrentInstance, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listOrder, getOrder, addOrder, updateOrder, delOrder } from "@/api/canteen/canteen";

const { proxy } = getCurrentInstance() || {};

const orderList = ref([]);
const open = ref(false);
const detailOpen = ref(false);
const loading = ref(true);
const orderRef = ref(null);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const orderDetail = ref({
  orderInfo: {},
  detailList: []
});

const orderStatusOptions = {
  "0": "待支付",
  "1": "已支付",
  "2": "已完成",
  "3": "已取消"
};

const columns = ref({
  orderId: { label: "订单编号", visible: true },
  orderNo: { label: "订单号", visible: true },
  userId: { label: "用户ID", visible: true },
  tableId: { label: "餐桌ID", visible: true },
  totalAmount: { label: "订单总额", visible: true },
  orderStatus: { label: "订单状态", visible: true },
  payMethod: { label: "支付方式", visible: true },
  createTime: { label: "创建时间", visible: true },
});

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    orderNo: undefined,
    userId: undefined,
    orderStatus: undefined,
  },
  rules: {
    userId: [{ required: true, message: "用户ID不能为空", trigger: "blur" }],
  },
});

const { queryParams, form, rules } = toRefs(data);

const getOrderStatusLabel = (status) => orderStatusOptions[status] || status;

const getOrderStatusTagType = (status) => {
  const map = { "0": "warning", "1": "success", "2": "info", "3": "danger" };
  return map[status] || "info";
};

function handleRowClick(row, column) {
  if (column && (column.type === "selection" || column.label === "操作")) return;
  handleDetail(row);
}

function getSummaries({ columns, data }) {
  const result = [];
  columns.forEach((column, index) => {
    if (index === 0) {
      result.push("合计");
    } else if (column.label && column.label.indexOf("金额") !== -1) {
      const total = data.reduce((prev, curr) => prev + Number(curr.amount || 0), 0);
      result.push("¥ " + total.toFixed(2));
    } else {
      result.push("");
    }
  });
  return result;
}

function getList() {
  loading.value = true;
  listOrder(queryParams.value).then((res) => {
    loading.value = false;
    orderList.value = res.rows;
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
    orderNo: undefined,
    userId: undefined,
    orderStatus: undefined,
  };
}

function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.orderId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

function handleDelete(row) {
  const orderIds = row.orderId || ids.value;
  ElMessageBox.confirm('是否确认删除订单编号为"' + orderIds + '"的数据项？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    delOrder(orderIds).then(() => {
      getList();
      ElMessage.success("删除成功");
    });
  }).catch(() => {});
}

function handleDetail(row) {
  getOrder(row.orderId).then((response) => {
    orderDetail.value = response.data;
    detailOpen.value = true;
  });
}

function reset() {
  form.value = {
    orderId: undefined,
    userId: undefined,
    tableId: undefined,
    orderStatus: "0",
    payMethod: "",
    remark: "",
  };
  orderRef.value?.resetFields();
}

function cancel() {
  open.value = false;
  reset();
}

function handleAdd() {
  reset();
  open.value = true;
  title.value = "新增订单";
}

function handleUpdate(row) {
  reset();
  const orderId = row.orderId || ids.value;
  getOrder(orderId).then((response) => {
    form.value = response.data.orderInfo || {};
    open.value = true;
    title.value = "修改订单";
  });
}

function submitForm() {
  proxy.$refs["orderRef"].validate((valid) => {
    if (valid) {
      if (form.value.orderId != undefined) {
        updateOrder(form.value).then(() => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addOrder({
          userId: form.value.userId,
          tableId: form.value.tableId,
          items: [],
          remark: form.value.remark
        }).then(() => {
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
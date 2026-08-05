from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CanteenMenuModel(BaseModel):
    """
    菜品信息视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    menu_id: Optional[int] = Field(None, description='菜品ID')
    menu_name: Optional[str] = Field(None, description='菜品名称')
    menu_type: Optional[str] = Field(None, description='菜品类型（0热菜 1凉菜 2主食 3汤品 4饮品）')
    price: Optional[float] = Field(None, description='菜品价格')
    image_url: Optional[str] = Field(None, description='菜品图片URL')
    description: Optional[str] = Field(None, description='菜品描述')
    status: Optional[str] = Field(None, description='状态（0正常 1下架）')
    sort_order: Optional[int] = Field(None, description='排序号')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class CanteenMenuPageQueryModel(BaseModel):
    """
    菜品分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    menu_id: Optional[int] = Field(None, description='菜品ID')
    menu_name: Optional[str] = Field(None, description='菜品名称')
    menu_type: Optional[str] = Field(None, description='菜品类型')
    status: Optional[str] = Field(None, description='状态')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')


class OrderRecordModel(BaseModel):
    """
    订单记录视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    order_id: Optional[int] = Field(None, description='订单ID')
    order_no: Optional[str] = Field(None, description='订单编号')
    user_id: Optional[int] = Field(None, description='用户ID')
    table_id: Optional[int] = Field(None, description='餐桌ID')
    total_amount: Optional[float] = Field(None, description='订单总额')
    order_status: Optional[str] = Field(None, description='订单状态（0待支付 1已支付 2已完成 3已取消）')
    pay_method: Optional[str] = Field(None, description='支付方式')
    pay_time: Optional[datetime] = Field(None, description='支付时间')
    remark: Optional[str] = Field(None, description='备注')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[datetime] = Field(None, description='更新时间')


class OrderRecordPageQueryModel(BaseModel):
    """
    订单分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    order_id: Optional[int] = Field(None, description='订单ID')
    order_no: Optional[str] = Field(None, description='订单编号')
    user_id: Optional[int] = Field(None, description='用户ID')
    order_status: Optional[str] = Field(None, description='订单状态')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')


class OrderDetailModel(BaseModel):
    """
    订单详情视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    detail_id: Optional[int] = Field(None, description='详情ID')
    order_id: Optional[int] = Field(None, description='订单ID')
    menu_id: Optional[int] = Field(None, description='菜品ID')
    menu_name: Optional[str] = Field(None, description='菜品名称')
    price: Optional[float] = Field(None, description='单价')
    quantity: Optional[int] = Field(None, description='数量')
    amount: Optional[float] = Field(None, description='金额')


class OrderCreateModel(BaseModel):
    """
    订单创建视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    user_id: int = Field(..., description='用户ID')
    table_id: Optional[int] = Field(None, description='餐桌ID')
    items: Optional[list[dict]] = Field([], description='订单项列表')
    remark: Optional[str] = Field(None, description='备注')


class DiningTableModel(BaseModel):
    """
    餐桌信息视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    table_id: Optional[int] = Field(None, description='餐桌ID')
    table_no: Optional[str] = Field(None, description='餐桌编号')
    table_name: Optional[str] = Field(None, description='餐桌名称')
    capacity: Optional[int] = Field(None, description='容纳人数')
    table_status: Optional[str] = Field(None, description='状态（0空闲 1占用 2预订）')
    location: Optional[str] = Field(None, description='位置描述')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class DiningTablePageQueryModel(BaseModel):
    """
    餐桌分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    table_id: Optional[int] = Field(None, description='餐桌ID')
    table_no: Optional[str] = Field(None, description='餐桌编号')
    table_name: Optional[str] = Field(None, description='餐桌名称')
    table_status: Optional[str] = Field(None, description='状态')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')


class CanteenStaffModel(BaseModel):
    """
    食堂员工信息视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    staff_id: Optional[int] = Field(None, description='员工ID')
    staff_no: Optional[str] = Field(None, description='员工编号')
    staff_name: Optional[str] = Field(None, description='员工姓名')
    position: Optional[str] = Field(None, description='岗位')
    phone: Optional[str] = Field(None, description='联系电话')
    email: Optional[str] = Field(None, description='邮箱')
    status: Optional[str] = Field(None, description='状态（0在职 1离职）')
    hire_date: Optional[str] = Field(None, description='入职日期')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class CanteenStaffPageQueryModel(BaseModel):
    """
    食堂员工分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    staff_name: Optional[str] = Field(None, description='员工姓名')
    position: Optional[str] = Field(None, description='岗位')
    status: Optional[str] = Field(None, description='状态')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')


class CanteenUserModel(BaseModel):
    """
    食堂用户信息视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    user_id: Optional[int] = Field(None, description='用户ID')
    user_name: Optional[str] = Field(None, description='用户账号')
    nick_name: Optional[str] = Field(None, description='用户昵称')
    password: Optional[str] = Field(None, description='密码')
    email: Optional[str] = Field(None, description='邮箱')
    phonenumber: Optional[str] = Field(None, description='手机号')
    sex: Optional[str] = Field(None, description='性别')
    avatar: Optional[str] = Field(None, description='头像')
    status: Optional[str] = Field(None, description='状态（0正常 1停用）')
    balance: Optional[float] = Field(None, description='余额')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class CanteenUserPageQueryModel(BaseModel):
    """
    食堂用户分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_name: Optional[str] = Field(None, description='用户账号')
    nick_name: Optional[str] = Field(None, description='用户昵称')
    status: Optional[str] = Field(None, description='状态')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')


class CanteenUserResetPwdModel(BaseModel):
    """
    食堂用户重置密码视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_id: int = Field(..., description='用户ID')
    password: str = Field(..., description='新密码')


class CanteenInventoryModel(BaseModel):
    """
    库存管理视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    record_id: Optional[int] = Field(None, description='记录ID')
    item_name: Optional[str] = Field(None, description='物品名称')
    item_type: Optional[str] = Field(None, description='物品类型')
    initial_quantity: Optional[float] = Field(None, description='初始数量')
    in_quantity: Optional[float] = Field(None, description='入库数量')
    out_quantity: Optional[float] = Field(None, description='出库数量')
    remaining_quantity: Optional[float] = Field(None, description='剩余数量')
    unit: Optional[str] = Field(None, description='单位')
    unit_price: Optional[float] = Field(None, description='单价')
    total_value: Optional[float] = Field(None, description='总价值')
    turnover_rate: Optional[float] = Field(None, description='周转率')
    record_date: Optional[str] = Field(None, description='记录日期')
    status: Optional[str] = Field(None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class CanteenInventoryPageQueryModel(BaseModel):
    """
    库存分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    item_name: Optional[str] = Field(None, description='物品名称')
    item_type: Optional[str] = Field(None, description='物品类型')
    status: Optional[str] = Field(None, description='状态')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')


class CanteenProfitModel(BaseModel):
    """
    利润分析视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    record_id: Optional[int] = Field(None, description='记录ID')
    period_type: Optional[str] = Field(None, description='周期类型（day日 week周 month月）')
    period_name: Optional[str] = Field(None, description='周期名称')
    start_date: Optional[str] = Field(None, description='开始日期')
    end_date: Optional[str] = Field(None, description='结束日期')
    revenue: Optional[float] = Field(None, description='收入')
    cost: Optional[float] = Field(None, description='成本')
    labor_cost: Optional[float] = Field(None, description='人工成本')
    material_cost: Optional[float] = Field(None, description='材料成本')
    utility_cost: Optional[float] = Field(None, description='水电成本')
    other_cost: Optional[float] = Field(None, description='其他成本')
    profit: Optional[float] = Field(None, description='利润')
    profit_rate: Optional[float] = Field(None, description='利润率')
    order_count: Optional[int] = Field(None, description='订单数')
    customer_count: Optional[int] = Field(None, description='客户数')
    avg_order_amount: Optional[float] = Field(None, description='平均订单金额')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    remark: Optional[str] = Field(None, description='备注')


class CanteenProfitPageQueryModel(BaseModel):
    """
    利润分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    period_type: Optional[str] = Field(None, description='周期类型')
    period_name: Optional[str] = Field(None, description='周期名称')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')


class CanteenRevenueExpenseModel(BaseModel):
    """
    收支记录视图模型
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    record_id: Optional[int] = Field(None, description='记录ID')
    record_type: Optional[str] = Field(None, description='记录类型（0收入 1支出）')
    category: Optional[str] = Field(None, description='分类')
    item_name: Optional[str] = Field(None, description='项目名称')
    amount: Optional[float] = Field(None, description='金额')
    pay_method: Optional[str] = Field(None, description='支付方式')
    related_order: Optional[str] = Field(None, description='关联订单')
    record_date: Optional[str] = Field(None, description='记录日期')
    status: Optional[str] = Field(None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class CanteenRevenueExpensePageQueryModel(BaseModel):
    """
    收支分页查询视图模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    record_type: Optional[str] = Field(None, description='记录类型')
    category: Optional[str] = Field(None, description='分类')
    item_name: Optional[str] = Field(None, description='项目名称')
    status: Optional[str] = Field(None, description='状态')
    page_num: Optional[int] = Field(1, description='页码')
    page_size: Optional[int] = Field(10, description='每页数量')

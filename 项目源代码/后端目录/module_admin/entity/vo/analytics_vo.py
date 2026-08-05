from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InventoryRecordModel(BaseModel):
    """
    库存记录视图模型
    """

    model_config = ConfigDict(from_attributes=True)

    record_id: Optional[int] = Field(None, description='记录ID')
    item_name: Optional[str] = Field(None, description='物品名称')
    item_type: Optional[str] = Field(None, description='类型')
    initial_quantity: Optional[float] = Field(None, description='初始数量')
    in_quantity: Optional[float] = Field(None, description='入库数量')
    out_quantity: Optional[float] = Field(None, description='出库数量')
    remaining_quantity: Optional[float] = Field(None, description='剩余数量')
    unit: Optional[str] = Field(None, description='单位')
    unit_price: Optional[float] = Field(None, description='单价')
    total_value: Optional[float] = Field(None, description='库存总价值')
    turnover_rate: Optional[float] = Field(None, description='周转率')
    record_date: Optional[str] = Field(None, description='记录日期')
    status: Optional[str] = Field(None, description='状态')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class InventoryPageQueryModel(BaseModel):
    """
    库存分页查询视图模型
    """

    model_config = ConfigDict(populate_by_name=True)

    item_name: Optional[str] = Field(None, description='物品名称')
    item_type: Optional[str] = Field(None, description='类型')
    status: Optional[str] = Field(None, description='状态')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')
    page_num: Optional[int] = Field(1, description='页码', alias='pageNum')
    page_size: Optional[int] = Field(10, description='每页数量', alias='pageSize')


class RevenueExpenseModel(BaseModel):
    """
    收支明细视图模型
    """

    model_config = ConfigDict(from_attributes=True)

    record_id: Optional[int] = Field(None, description='记录ID')
    record_type: Optional[str] = Field(None, description='类型（0收入 1支出）')
    category: Optional[str] = Field(None, description='分类')
    item_name: Optional[str] = Field(None, description='项目名称')
    amount: Optional[float] = Field(None, description='金额')
    pay_method: Optional[str] = Field(None, description='支付方式')
    related_order: Optional[str] = Field(None, description='关联订单编号')
    record_date: Optional[str] = Field(None, description='记录日期')
    status: Optional[str] = Field(None, description='状态')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[str] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class RevenueExpensePageQueryModel(BaseModel):
    """
    收支分页查询视图模型
    """

    model_config = ConfigDict(populate_by_name=True)

    record_type: Optional[str] = Field(None, description='类型')
    category: Optional[str] = Field(None, description='分类')
    item_name: Optional[str] = Field(None, description='项目名称')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')
    page_num: Optional[int] = Field(1, description='页码', alias='pageNum')
    page_size: Optional[int] = Field(10, description='每页数量', alias='pageSize')


class ProfitAnalysisModel(BaseModel):
    """
    利润分析视图模型
    """

    model_config = ConfigDict(from_attributes=True)

    record_id: Optional[int] = Field(None, description='记录ID')
    period_type: Optional[str] = Field(None, description='周期类型')
    period_name: Optional[str] = Field(None, description='周期名称')
    start_date: Optional[str] = Field(None, description='开始日期')
    end_date: Optional[str] = Field(None, description='结束日期')
    revenue: Optional[float] = Field(None, description='总收入')
    cost: Optional[float] = Field(None, description='总成本')
    labor_cost: Optional[float] = Field(None, description='人工成本')
    material_cost: Optional[float] = Field(None, description='食材成本')
    utility_cost: Optional[float] = Field(None, description='水电成本')
    other_cost: Optional[float] = Field(None, description='其他成本')
    profit: Optional[float] = Field(None, description='利润')
    profit_rate: Optional[float] = Field(None, description='利润率%')
    order_count: Optional[int] = Field(None, description='订单数量')
    customer_count: Optional[int] = Field(None, description='顾客数量')
    avg_order_amount: Optional[float] = Field(None, description='客单价')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[str] = Field(None, description='创建时间')
    remark: Optional[str] = Field(None, description='备注')


class ProfitPageQueryModel(BaseModel):
    """
    利润分析分页查询视图模型
    """

    model_config = ConfigDict(populate_by_name=True)

    period_type: Optional[str] = Field(None, description='周期类型')
    period_name: Optional[str] = Field(None, description='周期名称')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')
    page_num: Optional[int] = Field(1, description='页码', alias='pageNum')
    page_size: Optional[int] = Field(10, description='每页数量', alias='pageSize')


class AnalyticsSummaryModel(BaseModel):
    """
    数据分析汇总视图模型
    """

    total_revenue: float = Field(0.0, description='总收入')
    total_cost: float = Field(0.0, description='总支出')
    total_profit: float = Field(0.0, description='总利润')
    profit_rate: float = Field(0.0, description='利润率%')
    total_orders: int = Field(0, description='订单总数')
    total_items: int = Field(0, description='物品总数')
    low_stock_items: int = Field(0, description='低库存物品数')
    avg_turnover_rate: float = Field(0.0, description='平均周转率')
    avg_order_amount: float = Field(0.0, description='客单价')


class TrendDataModel(BaseModel):
    """
    趋势数据视图模型（用于图表）
    """

    name: str = Field('', description='名称（日期/周期）')
    value: float = Field(0.0, description='数值')


class CategoryDataModel(BaseModel):
    """
    分类数据视图模型（用于饼图/环形图）
    """

    name: str = Field('', description='分类名称')
    value: float = Field(0.0, description='数值')
    percentage: float = Field(0.0, description='百分比')

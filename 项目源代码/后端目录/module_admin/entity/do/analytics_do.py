from datetime import datetime

from sqlalchemy import CHAR, Column, DateTime, Float, Integer, String

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class InventoryRecord(Base):
    """
    库存记录表
    """

    __tablename__ = 'canteen_inventory'
    __table_args__ = {'comment': '库存记录表'}

    record_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='记录ID')
    item_name = Column(String(100), nullable=False, comment='物品名称')
    item_type = Column(String(20), nullable=True, server_default='0', comment='类型（0食材 1调料 2餐具 3饮品）')
    initial_quantity = Column(Float, nullable=False, server_default='0', comment='初始数量')
    in_quantity = Column(Float, nullable=False, server_default='0', comment='入库数量')
    out_quantity = Column(Float, nullable=False, server_default='0', comment='出库数量')
    remaining_quantity = Column(Float, nullable=False, server_default='0', comment='剩余数量')
    unit = Column(String(20), nullable=True, server_default="'个'", comment='单位')
    unit_price = Column(Float, nullable=False, server_default='0', comment='单价')
    total_value = Column(Float, nullable=False, server_default='0', comment='库存总价值')
    turnover_rate = Column(Float, nullable=False, server_default='0', comment='周转率')
    record_date = Column(DateTime, nullable=True, comment='记录日期', default=datetime.now())
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1预警 2缺货）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间', default=datetime.now())
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间', default=datetime.now())
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )


class RevenueExpense(Base):
    """
    收支明细表
    """

    __tablename__ = 'canteen_revenue_expense'
    __table_args__ = {'comment': '收支明细表'}

    record_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='记录ID')
    record_type = Column(CHAR(1), nullable=False, server_default='0', comment='类型（0收入 1支出）')
    category = Column(String(50), nullable=False, comment='分类（销售/采购/人工/水电等）')
    item_name = Column(String(100), nullable=False, comment='项目名称')
    amount = Column(Float, nullable=False, server_default='0', comment='金额')
    pay_method = Column(String(20), nullable=True, server_default="''", comment='支付方式')
    related_order = Column(String(64), nullable=True, server_default="''", comment='关联订单编号')
    record_date = Column(DateTime, nullable=True, comment='记录日期', default=datetime.now())
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1作废）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间', default=datetime.now())
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间', default=datetime.now())
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )


class ProfitAnalysis(Base):
    """
    利润分析表
    """

    __tablename__ = 'canteen_profit'
    __table_args__ = {'comment': '利润分析表'}

    record_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='记录ID')
    period_type = Column(String(20), nullable=False, server_default="'day'", comment='周期类型（day/week/month/quarter/year）')
    period_name = Column(String(50), nullable=False, comment='周期名称')
    start_date = Column(DateTime, nullable=True, comment='开始日期')
    end_date = Column(DateTime, nullable=True, comment='结束日期')
    revenue = Column(Float, nullable=False, server_default='0', comment='总收入')
    cost = Column(Float, nullable=False, server_default='0', comment='总成本')
    labor_cost = Column(Float, nullable=False, server_default='0', comment='人工成本')
    material_cost = Column(Float, nullable=False, server_default='0', comment='食材成本')
    utility_cost = Column(Float, nullable=False, server_default='0', comment='水电成本')
    other_cost = Column(Float, nullable=False, server_default='0', comment='其他成本')
    profit = Column(Float, nullable=False, server_default='0', comment='利润')
    profit_rate = Column(Float, nullable=False, server_default='0', comment='利润率%')
    order_count = Column(Integer, nullable=False, server_default='0', comment='订单数量')
    customer_count = Column(Integer, nullable=False, server_default='0', comment='顾客数量')
    avg_order_amount = Column(Float, nullable=False, server_default='0', comment='客单价')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间', default=datetime.now())
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )

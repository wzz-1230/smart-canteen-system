from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String
from config.database import Base


class Inventory(Base):
    __tablename__ = 'inventory'
    __table_args__ = {'comment': '库存管理表'}
    inventory_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='库存ID')
    item_name = Column(String(100), nullable=False, comment='物品名称')
    category = Column(String(50), nullable=True, comment='分类（如：食材/耗材/设备/清洁用品）')
    unit = Column(String(20), nullable=True, comment='单位（如：kg/个/箱/瓶）')
    quantity = Column(Float, nullable=True, default=0.0, comment='当前库存数量')
    min_quantity = Column(Float, nullable=True, default=0.0, comment='最低安全库存')
    unit_price = Column(Float, nullable=True, default=0.0, comment='单价')
    total_value = Column(Float, nullable=True, default=0.0, comment='库存总价值')
    location = Column(String(100), nullable=True, comment='存放位置（如：A区/仓库1号）')
    supplier = Column(String(100), nullable=True, comment='供应商')
    status = Column(String(20), nullable=True, default='正常', comment='状态（正常/低库存/缺货）')
    remark = Column(String(500), nullable=True, comment='备注')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, comment='更新时间')

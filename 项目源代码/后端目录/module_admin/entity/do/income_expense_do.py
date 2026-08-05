from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String
from config.database import Base


class IncomeExpense(Base):
    __tablename__ = 'income_expense'
    __table_args__ = {'comment': '收支管理表'}
    record_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='记录ID')
    record_type = Column(String(20), nullable=False, comment='类型（收入/支出）')
    category = Column(String(50), nullable=True, comment='分类（如：销售收入/采购支出/工资/水电/租金）')
    amount = Column(Float, nullable=True, default=0.0, comment='金额')
    payment_method = Column(String(50), nullable=True, comment='支付方式（现金/银行/微信/支付宝）')
    record_date = Column(DateTime, nullable=True, default=datetime.now, comment='发生日期')
    description = Column(String(200), nullable=True, comment='描述')
    operator = Column(String(50), nullable=True, comment='经办人')
    department = Column(String(50), nullable=True, comment='关联部门')
    remark = Column(String(500), nullable=True, comment='备注')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, comment='更新时间')

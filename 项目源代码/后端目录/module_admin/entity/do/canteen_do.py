from datetime import datetime

from sqlalchemy import CHAR, Column, DateTime, Float, Integer, String, Text

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class CanteenMenu(Base):
    __tablename__ = 'canteen_menu'
    __table_args__ = {'comment': '菜品信息表'}

    menu_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='菜品ID')
    menu_name = Column(String(100), nullable=True, server_default="''", comment='菜品名称')
    menu_type = Column(CHAR(1), nullable=True, server_default='0', comment='菜品类型')
    price = Column(Float, nullable=True, server_default='0.0', comment='菜品价格')
    image_url = Column(String(500), nullable=True, server_default="''", comment='菜品图片URL')
    description = Column(Text, nullable=True, comment='菜品描述')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态')
    sort_order = Column(Integer, nullable=True, server_default='0', comment='排序号')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='备注')


class OrderRecord(Base):
    __tablename__ = 'canteen_order'
    __table_args__ = {'comment': '订单记录表'}

    order_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='订单ID')
    order_no = Column(String(50), nullable=True, server_default="''", comment='订单编号')
    user_id = Column(Integer, nullable=True, comment='用户ID')
    table_id = Column(Integer, nullable=True, comment='餐桌ID')
    total_amount = Column(Float, nullable=True, server_default='0.0', comment='订单总额')
    order_status = Column(CHAR(1), nullable=True, server_default='0', comment='订单状态')
    pay_method = Column(String(50), nullable=True, server_default="''", comment='支付方式')
    pay_time = Column(DateTime, nullable=True, comment='支付时间')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='备注')


class OrderDetail(Base):
    __tablename__ = 'canteen_order_detail'
    __table_args__ = {'comment': '订单详情表'}

    detail_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='详情ID')
    order_id = Column(Integer, nullable=True, comment='订单ID')
    menu_id = Column(Integer, nullable=True, comment='菜品ID')
    menu_name = Column(String(100), nullable=True, server_default="''", comment='菜品名称')
    price = Column(Float, nullable=True, server_default='0.0', comment='单价')
    quantity = Column(Integer, nullable=True, server_default='0', comment='数量')
    amount = Column(Float, nullable=True, server_default='0.0', comment='金额')


class DiningTable(Base):
    __tablename__ = 'canteen_table'
    __table_args__ = {'comment': '餐桌信息表'}

    table_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='餐桌ID')
    table_no = Column(String(20), nullable=True, server_default="''", comment='餐桌编号')
    table_name = Column(String(100), nullable=True, server_default="''", comment='餐桌名称')
    capacity = Column(Integer, nullable=True, server_default='0', comment='容纳人数')
    table_status = Column(CHAR(1), nullable=True, server_default='0', comment='状态')
    location = Column(String(200), nullable=True, server_default="''", comment='位置描述')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='备注')


class CanteenStaff(Base):
    __tablename__ = 'canteen_staff'
    __table_args__ = {'comment': '食堂员工信息表'}

    staff_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='员工ID')
    staff_no = Column(String(50), nullable=True, server_default="''", comment='员工编号')
    staff_name = Column(String(50), nullable=True, server_default="''", comment='员工姓名')
    position = Column(String(50), nullable=True, server_default="''", comment='岗位')
    phone = Column(String(20), nullable=True, server_default="''", comment='联系电话')
    email = Column(String(100), nullable=True, server_default="''", comment='邮箱')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态')
    hire_date = Column(String(20), nullable=True, server_default="''", comment='入职日期')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='备注')


class CanteenUser(Base):
    __tablename__ = 'canteen_user'
    __table_args__ = {'comment': '食堂用户信息表'}

    user_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='用户ID')
    user_name = Column(String(50), nullable=True, server_default="''", comment='用户账号')
    nick_name = Column(String(50), nullable=True, server_default="''", comment='用户昵称')
    password = Column(String(100), nullable=True, server_default="''", comment='密码')
    email = Column(String(100), nullable=True, server_default="''", comment='邮箱')
    phonenumber = Column(String(20), nullable=True, server_default="''", comment='手机号')
    sex = Column(CHAR(1), nullable=True, server_default='0', comment='性别')
    avatar = Column(String(500), nullable=True, server_default="''", comment='头像')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态')
    balance = Column(Float, nullable=True, server_default='0.0', comment='余额')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='备注')

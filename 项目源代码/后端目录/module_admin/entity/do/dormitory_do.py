from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class DormitoryRoom(Base):
    __tablename__ = 'dormitory_room'
    __table_args__ = {'comment': 'dormitory_room'}

    room_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='room_id')
    building_no = Column(String(20), nullable=False, comment='building_no')
    floor_no = Column(Integer, nullable=False, comment='floor_no')
    room_no = Column(String(20), nullable=False, comment='room_no')
    room_type = Column(String(20), nullable=True, server_default='4 person', comment='room_type')
    max_capacity = Column(Integer, nullable=False, server_default='4', comment='max_capacity')
    current_capacity = Column(Integer, nullable=True, server_default='0', comment='current_capacity')
    room_status = Column(CHAR(1), nullable=True, server_default='0', comment='room_status')
    create_by = Column(String(64), nullable=True, server_default="''", comment='create_by')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='create_time')
    update_by = Column(String(64), nullable=True, server_default="''", comment='update_by')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='update_time')
    remark = Column(String(500), nullable=True, server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type), comment='remark')
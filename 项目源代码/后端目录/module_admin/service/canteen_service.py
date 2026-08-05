from datetime import datetime
import os
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from config.env import UploadConfig
from exceptions.exception import ServiceException
from module_admin.dao.canteen_dao import CanteenDao
from module_admin.entity.vo.canteen_vo import (
    CanteenInventoryModel,
    CanteenInventoryPageQueryModel,
    CanteenMenuModel,
    CanteenMenuPageQueryModel,
    CanteenProfitModel,
    CanteenProfitPageQueryModel,
    CanteenRevenueExpenseModel,
    CanteenRevenueExpensePageQueryModel,
    CanteenStaffModel,
    CanteenStaffPageQueryModel,
    CanteenUserModel,
    CanteenUserPageQueryModel,
    CanteenUserResetPwdModel,
    DiningTableModel,
    DiningTablePageQueryModel,
    OrderCreateModel,
    OrderDetailModel,
    OrderRecordModel,
    OrderRecordPageQueryModel,
)
from utils.common_util import CamelCaseUtil


def _get_image_url_for_menu(menu_name: str) -> str:
    """
    根据菜品名称获取图片 URL。
    查找顺序：
    1. static/canteen-menu-images/<菜名>.<ext>（用户手动上传）
    2. static/canteen-menu-images/ai/<菜名>.<ext>（AI 自动生成）
    没有匹配到图片返回空字符串，由前端显示"图片未上传"占位。
    """
    name = (menu_name or '').strip()
    if not name:
        return ''
    try:
        for ext in UploadConfig.CANTEEN_MENU_IMAGE_EXTS:
            p = os.path.join(UploadConfig.CANTEEN_MENU_IMAGE_PATH, f'{name}{ext}')
            if os.path.exists(p):
                return f'{UploadConfig.CANTEEN_MENU_IMAGE_PREFIX}/{name}{ext}'
        for ext in UploadConfig.CANTEEN_MENU_IMAGE_EXTS:
            p = os.path.join(UploadConfig.CANTEEN_MENU_AI_IMAGE_PATH, f'{name}{ext}')
            if os.path.exists(p):
                return f'{UploadConfig.CANTEEN_MENU_IMAGE_PREFIX}/ai/{name}{ext}'
    except Exception:
        return ''
    return ''


def _to_camel(data, menu_name_hint: str | None = None):
    """
    将数据转换为驼峰命名；若为菜品记录且 image_url 为空，
    则尝试在本地 static/canteen-menu-images 目录按菜名匹配图片。
    """
    if isinstance(data, dict):
        mapped = {CamelCaseUtil.snake_to_camel(k): _to_camel(v) for k, v in data.items()}
        # 特殊处理菜品图片：数据库字段为空时按菜名查本地
        if 'menuName' in mapped and (not mapped.get('imageUrl') or mapped.get('imageUrl') == ''):
            local_url = _get_image_url_for_menu(menu_name_hint or mapped.get('menuName', ''))
            if local_url:
                mapped['imageUrl'] = local_url
        return mapped
    elif isinstance(data, list):
        return [_to_camel(item) for item in data]
    elif hasattr(data, '__dict__'):
        # 处理 ORM 对象
        result = {}
        current_menu_name = None
        for k, v in vars(data).items():
            if k.startswith('_'):
                continue
            key = CamelCaseUtil.snake_to_camel(k)
            result[key] = _to_camel(v)
            if k == 'menu_name':
                current_menu_name = v
        if 'menuName' in result and (not result.get('imageUrl') or result.get('imageUrl') == ''):
            local_url = _get_image_url_for_menu(current_menu_name or result.get('menuName', ''))
            if local_url:
                result['imageUrl'] = local_url
        return result
    else:
        return data


class CanteenService:
    """
    食堂管理模块服务层
    """

    @classmethod
    async def get_menu_list_services(
        cls, query_db: AsyncSession, query_object: CanteenMenuPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取菜品列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 菜品列表信息对象
        """
        query_result = await CanteenDao.get_menu_list(query_db, query_object, is_page)

        # 转换为驼峰命名
        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]

        return query_result

    @classmethod
    async def get_menu_detail_services(cls, query_db: AsyncSession, menu_id: int) -> dict[str, Any] | None:
        """
        获取菜品详情信息service

        :param query_db: orm对象
        :param menu_id: 菜品ID
        :return: 菜品详情信息对象
        """
        menu_info = await CanteenDao.get_menu_by_id(query_db, menu_id)
        if menu_info:
            return _to_camel(menu_info)
        return None

    @classmethod
    async def add_menu_services(cls, query_db: AsyncSession, menu: CanteenMenuModel) -> CrudResponseModel:
        """
        新增菜品信息service

        :param query_db: orm对象
        :param menu: 菜品信息对象
        :return: 新增结果
        """
        menu.create_time = datetime.now()
        menu.update_time = datetime.now()
        await CanteenDao.add_menu_dao(query_db, menu)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_menu_services(cls, query_db: AsyncSession, menu: CanteenMenuModel) -> CrudResponseModel:
        """
        编辑菜品信息service

        :param query_db: orm对象
        :param menu: 菜品信息对象
        :return: 编辑结果
        """
        menu.update_time = datetime.now()
        await CanteenDao.edit_menu_dao(query_db, menu.model_dump(exclude_unset=True))
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_menu_services(cls, query_db: AsyncSession, menu: CanteenMenuModel) -> CrudResponseModel:
        """
        删除菜品信息service

        :param query_db: orm对象
        :param menu: 菜品信息对象
        :return: 删除结果
        """
        await CanteenDao.delete_menu_dao(query_db, menu)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def get_order_list_services(
        cls, query_db: AsyncSession, query_object: OrderRecordPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取订单列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 订单列表信息对象
        """
        query_result = await CanteenDao.get_order_list(query_db, query_object, is_page)

        # 转换为驼峰命名
        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]

        return query_result

    @classmethod
    async def get_order_detail_services(cls, query_db: AsyncSession, order_id: int) -> dict[str, Any]:
        """
        获取订单详情信息service

        :param query_db: orm对象
        :param order_id: 订单ID
        :return: 订单详情信息对象
        """
        order_info = await CanteenDao.get_order_by_id(query_db, order_id)
        detail_list = await CanteenDao.get_order_detail_list(query_db, order_id)

        result = {
            'orderInfo': _to_camel(order_info),
            'detailList': [_to_camel(detail) for detail in detail_list],
        }

        return result

    @classmethod
    async def add_order_services(cls, query_db: AsyncSession, order: OrderCreateModel) -> CrudResponseModel:
        """
        新增订单信息service

        :param query_db: orm对象
        :param order: 订单信息对象
        :return: 新增结果
        """
        order_no = f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}'
        total_amount = sum(item.get('price', 0) * item.get('quantity', 0) for item in order.items)

        order_record = OrderRecordModel(
            order_no=order_no,
            user_id=order.user_id,
            table_id=order.table_id,
            total_amount=total_amount,
            order_status='0',
            remark=order.remark,
            create_time=datetime.now(),
            update_time=datetime.now(),
        )

        db_order = await CanteenDao.add_order_dao(query_db, order_record)
        new_order_id = db_order.order_id

        detail_list = []
        for item in order.items:
            detail = OrderDetailModel(
                order_id=new_order_id,
                menu_id=item.get('menu_id'),
                menu_name=item.get('menu_name'),
                price=item.get('price'),
                quantity=item.get('quantity'),
                amount=item.get('price') * item.get('quantity'),
            )
            detail_list.append(detail)

        await CanteenDao.add_order_detail_dao(query_db, detail_list)
        await query_db.commit()

        result = CrudResponseModel(is_success=True, message='下单成功')
        result.result = {'orderNo': order_no, 'orderId': new_order_id}
        return result

    @classmethod
    async def edit_order_services(cls, query_db: AsyncSession, order: OrderRecordModel) -> CrudResponseModel:
        """
        编辑订单信息service

        :param query_db: orm对象
        :param order: 订单信息对象
        :return: 编辑结果
        """
        order.update_time = datetime.now()
        await CanteenDao.edit_order_dao(query_db, order.model_dump(exclude_unset=True))
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_order_services(cls, query_db: AsyncSession, order: OrderRecordModel) -> CrudResponseModel:
        """
        删除订单信息service

        :param query_db: orm对象
        :param order: 订单信息对象
        :return: 删除结果
        """
        await CanteenDao.delete_order_dao(query_db, order)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def get_table_list_services(
        cls, query_db: AsyncSession, query_object: DiningTablePageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取餐桌列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 餐桌列表信息对象
        """
        query_result = await CanteenDao.get_table_list(query_db, query_object, is_page)

        # 转换为驼峰命名
        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]

        return query_result

    @classmethod
    async def get_table_detail_services(cls, query_db: AsyncSession, table_id: int) -> dict[str, Any] | None:
        """
        获取餐桌详情信息service

        :param query_db: orm对象
        :param table_id: 餐桌ID
        :return: 餐桌详情信息对象
        """
        table_info = await CanteenDao.get_table_by_id(query_db, table_id)
        if table_info:
            return _to_camel(table_info)
        return None

    @classmethod
    async def add_table_services(cls, query_db: AsyncSession, table: DiningTableModel) -> CrudResponseModel:
        """
        新增餐桌信息service

        :param query_db: orm对象
        :param table: 餐桌信息对象
        :return: 新增结果
        """
        table.create_time = datetime.now()
        table.update_time = datetime.now()
        await CanteenDao.add_table_dao(query_db, table)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_table_services(cls, query_db: AsyncSession, table: DiningTableModel) -> CrudResponseModel:
        """
        编辑餐桌信息service

        :param query_db: orm对象
        :param table: 餐桌信息对象
        :return: 编辑结果
        """
        table.update_time = datetime.now()
        await CanteenDao.edit_table_dao(query_db, table.model_dump(exclude_unset=True))
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_table_services(cls, query_db: AsyncSession, table: DiningTableModel) -> CrudResponseModel:
        """
        删除餐桌信息service

        :param query_db: orm对象
        :param table: 餐桌信息对象
        :return: 删除结果
        """
        await CanteenDao.delete_table_dao(query_db, table)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def update_table_status_services(cls, query_db: AsyncSession, table_id: int, status: str) -> CrudResponseModel:
        """
        更新餐桌状态service

        :param query_db: orm对象
        :param table_id: 餐桌ID
        :param status: 状态
        :return: 更新结果
        """
        await CanteenDao.update_table_status_dao(query_db, table_id, status)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='状态更新成功')

    @classmethod
    async def get_staff_list_services(
        cls, query_db: AsyncSession, query_object: CanteenStaffPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取员工列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 员工列表信息对象
        """
        query_result = await CanteenDao.get_staff_list(query_db, query_object, is_page)

        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]

        return query_result

    @classmethod
    async def get_staff_detail_services(cls, query_db: AsyncSession, staff_id: int) -> dict[str, Any] | None:
        """
        获取员工详情信息service

        :param query_db: orm对象
        :param staff_id: 员工ID
        :return: 员工详情信息对象
        """
        staff_info = await CanteenDao.get_staff_by_id(query_db, staff_id)
        if staff_info:
            return _to_camel(staff_info)
        return None

    @classmethod
    async def add_staff_services(cls, query_db: AsyncSession, staff: CanteenStaffModel) -> CrudResponseModel:
        """
        新增员工信息service

        :param query_db: orm对象
        :param staff: 员工信息对象
        :return: 新增结果
        """
        staff.create_time = datetime.now()
        staff.update_time = datetime.now()
        await CanteenDao.add_staff_dao(query_db, staff)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_staff_services(cls, query_db: AsyncSession, staff: CanteenStaffModel) -> CrudResponseModel:
        """
        编辑员工信息service

        :param query_db: orm对象
        :param staff: 员工信息对象
        :return: 编辑结果
        """
        staff.update_time = datetime.now()
        await CanteenDao.edit_staff_dao(query_db, staff.model_dump(exclude_unset=True))
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_staff_services(cls, query_db: AsyncSession, staff: CanteenStaffModel) -> CrudResponseModel:
        """
        删除员工信息service

        :param query_db: orm对象
        :param staff: 员工信息对象
        :return: 删除结果
        """
        await CanteenDao.delete_staff_dao(query_db, staff)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def get_user_list_services(
        cls, query_db: AsyncSession, query_object: CanteenUserPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取用户列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 用户列表信息对象
        """
        query_result = await CanteenDao.get_user_list(query_db, query_object, is_page)

        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]

        return query_result

    @classmethod
    async def get_user_detail_services(cls, query_db: AsyncSession, user_id: int) -> dict[str, Any] | None:
        """
        获取用户详情信息service

        :param query_db: orm对象
        :param user_id: 用户ID
        :return: 用户详情信息对象
        """
        user_info = await CanteenDao.get_user_by_id(query_db, user_id)
        if user_info:
            return _to_camel(user_info)
        return None

    @classmethod
    async def add_user_services(cls, query_db: AsyncSession, user: CanteenUserModel) -> CrudResponseModel:
        """
        新增用户信息service

        :param query_db: orm对象
        :param user: 用户信息对象
        :return: 新增结果
        """
        user.create_time = datetime.now()
        user.update_time = datetime.now()
        await CanteenDao.add_user_dao(query_db, user)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_user_services(cls, query_db: AsyncSession, user: CanteenUserModel) -> CrudResponseModel:
        """
        编辑用户信息service

        :param query_db: orm对象
        :param user: 用户信息对象
        :return: 编辑结果
        """
        user.update_time = datetime.now()
        await CanteenDao.edit_user_dao(query_db, user.model_dump(exclude_unset=True))
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_user_services(cls, query_db: AsyncSession, user: CanteenUserModel) -> CrudResponseModel:
        """
        删除用户信息service

        :param query_db: orm对象
        :param user: 用户信息对象
        :return: 删除结果
        """
        await CanteenDao.delete_user_dao(query_db, user)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def reset_user_password_services(
        cls, query_db: AsyncSession, pwd_object: CanteenUserResetPwdModel
    ) -> CrudResponseModel:
        """
        重置用户密码service

        :param query_db: orm对象
        :param pwd_object: 重置密码对象
        :return: 重置结果
        """
        if not pwd_object.user_id:
            raise ServiceException('用户ID不能为空')
        if not pwd_object.new_password:
            raise ServiceException('新密码不能为空')

        await CanteenDao.reset_user_password_dao(query_db, pwd_object.user_id, pwd_object.new_password)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='密码重置成功')

    @classmethod
    async def get_inventory_list_services(
        cls, query_db: AsyncSession, query_object: CanteenInventoryPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取库存列表信息service
        """
        query_result = await CanteenDao.get_inventory_list(query_db, query_object, is_page)
        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]
        return query_result

    @classmethod
    async def get_inventory_detail_services(cls, query_db: AsyncSession, record_id: int) -> dict[str, Any] | None:
        """
        获取库存详情信息service
        """
        inventory_info = await CanteenDao.get_inventory_by_id(query_db, record_id)
        if inventory_info:
            return _to_camel(inventory_info)
        return None

    @classmethod
    async def add_inventory_services(cls, query_db: AsyncSession, inventory: CanteenInventoryModel) -> CrudResponseModel:
        """
        新增库存信息service
        """
        inventory.create_time = datetime.now()
        inventory.update_time = datetime.now()
        await CanteenDao.add_inventory_dao(query_db, inventory)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_inventory_services(cls, query_db: AsyncSession, inventory: CanteenInventoryModel) -> CrudResponseModel:
        """
        编辑库存信息service
        """
        inventory.update_time = datetime.now()
        await CanteenDao.edit_inventory_dao(query_db, inventory.model_dump(exclude_unset=True))
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_inventory_services(cls, query_db: AsyncSession, inventory: CanteenInventoryModel) -> CrudResponseModel:
        """
        删除库存信息service
        """
        await CanteenDao.delete_inventory_dao(query_db, inventory)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def get_profit_list_services(
        cls, query_db: AsyncSession, query_object: CanteenProfitPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取利润记录列表信息service
        """
        query_result = await CanteenDao.get_profit_list(query_db, query_object, is_page)
        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]
        return query_result

    @classmethod
    async def get_profit_detail_services(cls, query_db: AsyncSession, record_id: int) -> dict[str, Any] | None:
        """
        获取利润记录详情信息service
        """
        profit_info = await CanteenDao.get_profit_by_id(query_db, record_id)
        if profit_info:
            return _to_camel(profit_info)
        return None

    @classmethod
    async def add_profit_services(cls, query_db: AsyncSession, profit: CanteenProfitModel) -> CrudResponseModel:
        """
        新增利润记录service
        """
        profit.create_time = datetime.now()
        await CanteenDao.add_profit_dao(query_db, profit)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_profit_services(cls, query_db: AsyncSession, profit: CanteenProfitModel) -> CrudResponseModel:
        """
        编辑利润记录service
        """
        await CanteenDao.edit_profit_dao(query_db, profit.model_dump(exclude_unset=True))
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_profit_services(cls, query_db: AsyncSession, profit: CanteenProfitModel) -> CrudResponseModel:
        """
        删除利润记录service
        """
        await CanteenDao.delete_profit_dao(query_db, profit)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def get_revenue_expense_list_services(
        cls, query_db: AsyncSession, query_object: CanteenRevenueExpensePageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取收支记录列表信息service
        """
        query_result = await CanteenDao.get_revenue_expense_list(query_db, query_object, is_page)
        if isinstance(query_result, PageModel):
            query_result.rows = [_to_camel(row) for row in query_result.rows]
        elif isinstance(query_result, list):
            query_result = [_to_camel(row) for row in query_result]
        return query_result

    @classmethod
    async def get_revenue_expense_detail_services(cls, query_db: AsyncSession, record_id: int) -> dict[str, Any] | None:
        """
        获取收支记录详情信息service
        """
        revenue_expense_info = await CanteenDao.get_revenue_expense_by_id(query_db, record_id)
        if revenue_expense_info:
            return _to_camel(revenue_expense_info)
        return None

    @classmethod
    async def add_revenue_expense_services(cls, query_db: AsyncSession, revenue_expense: CanteenRevenueExpenseModel) -> CrudResponseModel:
        """
        新增收支记录service
        """
        revenue_expense.create_time = datetime.now()
        revenue_expense.update_time = datetime.now()
        await CanteenDao.add_revenue_expense_dao(query_db, revenue_expense)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_revenue_expense_services(cls, query_db: AsyncSession, revenue_expense: CanteenRevenueExpenseModel) -> CrudResponseModel:
        """
        编辑收支记录service
        """
        revenue_expense.update_time = datetime.now()
        await CanteenDao.edit_revenue_expense_dao(query_db, revenue_expense.model_dump(exclude_unset=True))
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_revenue_expense_services(cls, query_db: AsyncSession, revenue_expense: CanteenRevenueExpenseModel) -> CrudResponseModel:
        """
        删除收支记录service
        """
        await CanteenDao.delete_revenue_expense_dao(query_db, revenue_expense)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

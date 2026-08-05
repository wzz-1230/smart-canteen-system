from collections.abc import Sequence
from datetime import datetime, time
from typing import Any

from sqlalchemy import ColumnElement, and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_admin.entity.do.analytics_do import InventoryRecord, ProfitAnalysis, RevenueExpense
from module_admin.entity.do.canteen_do import CanteenMenu, CanteenStaff, CanteenUser, DiningTable, OrderDetail, OrderRecord
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
    DiningTableModel,
    DiningTablePageQueryModel,
    OrderDetailModel,
    OrderRecordModel,
    OrderRecordPageQueryModel,
)
from utils.page_util import PageUtil


class CanteenDao:
    """
    食堂管理模块数据库操作层
    """

    @classmethod
    async def get_menu_list(
        cls, db: AsyncSession, query_object: CanteenMenuPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取菜品列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 菜品列表信息对象
        """
        query = (
            select(CanteenMenu)
            .where(
                CanteenMenu.status == query_object.status if query_object.status else True,
                CanteenMenu.menu_type == query_object.menu_type if query_object.menu_type else True,
                CanteenMenu.menu_name.like(f'%{query_object.menu_name}%') if query_object.menu_name else True,
                CanteenMenu.create_time.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
            )
            .order_by(CanteenMenu.sort_order, desc(CanteenMenu.create_time))
            .distinct()
        )
        menu_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return menu_list

    @classmethod
    async def get_menu_by_id(cls, db: AsyncSession, menu_id: int) -> CanteenMenu | None:
        """
        根据菜品ID获取菜品信息

        :param db: orm对象
        :param menu_id: 菜品ID
        :return: 菜品信息对象
        """
        menu_info = (
            (await db.execute(select(CanteenMenu).where(CanteenMenu.menu_id == menu_id).distinct()))
            .scalars()
            .first()
        )

        return menu_info

    @classmethod
    async def add_menu_dao(cls, db: AsyncSession, menu: CanteenMenuModel) -> CanteenMenu:
        """
        新增菜品数据库操作

        :param db: orm对象
        :param menu: 菜品对象
        :return: 新增的菜品对象
        """
        db_menu = CanteenMenu(**menu.model_dump())
        db.add(db_menu)
        await db.flush()

        return db_menu

    @classmethod
    async def edit_menu_dao(cls, db: AsyncSession, menu: dict) -> None:
        """
        编辑菜品数据库操作

        :param db: orm对象
        :param menu: 需要更新的菜品字典
        :return:
        """
        menu_id = menu.pop('menu_id', None)
        if not menu_id:
            raise ValueError('menu_id 不能为空，无法更新菜品信息')
        if menu:
            await db.execute(update(CanteenMenu).where(CanteenMenu.menu_id == menu_id).values(**menu))

    @classmethod
    async def delete_menu_dao(cls, db: AsyncSession, menu: CanteenMenuModel) -> None:
        """
        删除菜品数据库操作

        :param db: orm对象
        :param menu: 菜品对象
        :return:
        """
        await db.execute(delete(CanteenMenu).where(CanteenMenu.menu_id == menu.menu_id))

    @classmethod
    async def get_order_list(
        cls, db: AsyncSession, query_object: OrderRecordPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取订单列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 订单列表信息对象
        """
        query = (
            select(OrderRecord)
            .where(
                OrderRecord.order_status == query_object.order_status if query_object.order_status else True,
                OrderRecord.order_no.like(f'%{query_object.order_no}%') if query_object.order_no else True,
                OrderRecord.user_id == query_object.user_id if query_object.user_id else True,
                OrderRecord.create_time.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
            )
            .order_by(desc(OrderRecord.create_time))
            .distinct()
        )
        order_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return order_list

    @classmethod
    async def get_order_by_id(cls, db: AsyncSession, order_id: int) -> OrderRecord | None:
        """
        根据订单ID获取订单信息

        :param db: orm对象
        :param order_id: 订单ID
        :return: 订单信息对象
        """
        order_info = (
            (await db.execute(select(OrderRecord).where(OrderRecord.order_id == order_id).distinct()))
            .scalars()
            .first()
        )

        return order_info

    @classmethod
    async def get_order_detail_list(cls, db: AsyncSession, order_id: int) -> Sequence[OrderDetail]:
        """
        根据订单ID获取订单详情列表

        :param db: orm对象
        :param order_id: 订单ID
        :return: 订单详情列表
        """
        detail_list = (
            (await db.execute(select(OrderDetail).where(OrderDetail.order_id == order_id).distinct()))
            .scalars()
            .all()
        )

        return detail_list

    @classmethod
    async def add_order_dao(cls, db: AsyncSession, order: OrderRecordModel) -> OrderRecord:
        """
        新增订单数据库操作

        :param db: orm对象
        :param order: 订单对象
        :return: 新增的订单对象
        """
        db_order = OrderRecord(**order.model_dump())
        db.add(db_order)
        await db.flush()

        return db_order

    @classmethod
    async def add_order_detail_dao(cls, db: AsyncSession, detail_list: list[OrderDetailModel]) -> None:
        """
        批量新增订单详情数据库操作

        :param db: orm对象
        :param detail_list: 订单详情列表
        :return:
        """
        for detail in detail_list:
            db_detail = OrderDetail(**detail.model_dump())
            db.add(db_detail)

    @classmethod
    async def edit_order_dao(cls, db: AsyncSession, order: dict) -> None:
        """
        编辑订单数据库操作

        :param db: orm对象
        :param order: 需要更新的订单字典
        :return:
        """
        order_id = order.pop('order_id', None)
        if not order_id:
            raise ValueError('order_id 不能为空，无法更新订单信息')
        if order:
            await db.execute(update(OrderRecord).where(OrderRecord.order_id == order_id).values(**order))

    @classmethod
    async def delete_order_dao(cls, db: AsyncSession, order: OrderRecordModel) -> None:
        """
        删除订单数据库操作

        :param db: orm对象
        :param order: 订单对象
        :return:
        """
        await db.execute(delete(OrderDetail).where(OrderDetail.order_id == order.order_id))
        await db.execute(delete(OrderRecord).where(OrderRecord.order_id == order.order_id))

    @classmethod
    async def get_table_list(
        cls, db: AsyncSession, query_object: DiningTablePageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取餐桌列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 餐桌列表信息对象
        """
        query = (
            select(DiningTable)
            .where(
                DiningTable.table_status == query_object.table_status if query_object.table_status else True,
                DiningTable.table_no.like(f'%{query_object.table_no}%') if query_object.table_no else True,
                DiningTable.table_name.like(f'%{query_object.table_name}%') if query_object.table_name else True,
            )
            .order_by(DiningTable.table_no)
            .distinct()
        )
        table_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return table_list

    @classmethod
    async def get_table_by_id(cls, db: AsyncSession, table_id: int) -> DiningTable | None:
        """
        根据餐桌ID获取餐桌信息

        :param db: orm对象
        :param table_id: 餐桌ID
        :return: 餐桌信息对象
        """
        table_info = (
            (await db.execute(select(DiningTable).where(DiningTable.table_id == table_id).distinct()))
            .scalars()
            .first()
        )

        return table_info

    @classmethod
    async def add_table_dao(cls, db: AsyncSession, table: DiningTableModel) -> DiningTable:
        """
        新增餐桌数据库操作

        :param db: orm对象
        :param table: 餐桌对象
        :return: 新增的餐桌对象
        """
        db_table = DiningTable(**table.model_dump())
        db.add(db_table)
        await db.flush()

        return db_table

    @classmethod
    async def edit_table_dao(cls, db: AsyncSession, table: dict) -> None:
        """
        编辑餐桌数据库操作

        :param db: orm对象
        :param table: 需要更新的餐桌字典
        :return:
        """
        table_id = table.pop('table_id', None)
        if not table_id:
            raise ValueError('table_id 不能为空，无法更新餐桌信息')
        if table:
            await db.execute(update(DiningTable).where(DiningTable.table_id == table_id).values(**table))

    @classmethod
    async def delete_table_dao(cls, db: AsyncSession, table: DiningTableModel) -> None:
        """
        删除餐桌数据库操作

        :param db: orm对象
        :param table: 餐桌对象
        :return:
        """
        await db.execute(delete(DiningTable).where(DiningTable.table_id == table.table_id))

    @classmethod
    async def update_table_status_dao(cls, db: AsyncSession, table_id: int, status: str) -> None:
        """
        更新餐桌状态数据库操作

        :param db: orm对象
        :param table_id: 餐桌ID
        :param status: 状态
        :return:
        """
        await db.execute(
            update(DiningTable).where(DiningTable.table_id == table_id).values(table_status=status)
        )

    @classmethod
    async def get_staff_list(
        cls, db: AsyncSession, query_object: CanteenStaffPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取员工列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 员工列表信息对象
        """
        query = (
            select(CanteenStaff)
            .where(
                CanteenStaff.status == query_object.status if query_object.status else True,
                CanteenStaff.staff_name.like(f'%{query_object.staff_name}%') if query_object.staff_name else True,
                CanteenStaff.position == query_object.position if query_object.position else True,
            )
            .order_by(desc(CanteenStaff.create_time))
            .distinct()
        )
        staff_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return staff_list

    @classmethod
    async def get_staff_by_id(cls, db: AsyncSession, staff_id: int) -> CanteenStaff | None:
        """
        根据员工ID获取员工信息

        :param db: orm对象
        :param staff_id: 员工ID
        :return: 员工信息对象
        """
        staff_info = (
            (await db.execute(select(CanteenStaff).where(CanteenStaff.staff_id == staff_id).distinct()))
            .scalars()
            .first()
        )
        return staff_info

    @classmethod
    async def add_staff_dao(cls, db: AsyncSession, staff: CanteenStaffModel) -> CanteenStaff:
        """
        新增员工数据库操作

        :param db: orm对象
        :param staff: 员工对象
        :return: 新增的员工对象
        """
        db_staff = CanteenStaff(**staff.model_dump())
        db.add(db_staff)
        await db.flush()
        return db_staff

    @classmethod
    async def edit_staff_dao(cls, db: AsyncSession, staff: dict) -> None:
        """
        编辑员工数据库操作

        :param db: orm对象
        :param staff: 需要更新的员工字典
        :return:
        """
        staff_id = staff.pop('staff_id', None)
        if not staff_id:
            raise ValueError('staff_id 不能为空，无法更新员工信息')
        if staff:
            await db.execute(update(CanteenStaff).where(CanteenStaff.staff_id == staff_id).values(**staff))

    @classmethod
    async def delete_staff_dao(cls, db: AsyncSession, staff: CanteenStaffModel) -> None:
        """
        删除员工数据库操作

        :param db: orm对象
        :param staff: 员工对象
        :return:
        """
        await db.execute(delete(CanteenStaff).where(CanteenStaff.staff_id == staff.staff_id))

    @classmethod
    async def get_user_list(
        cls, db: AsyncSession, query_object: CanteenUserPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取用户列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 用户列表信息对象
        """
        query = (
            select(CanteenUser)
            .where(
                CanteenUser.status == query_object.status if query_object.status else True,
                CanteenUser.user_name.like(f'%{query_object.user_name}%') if query_object.user_name else True,
                CanteenUser.nick_name.like(f'%{query_object.nick_name}%') if query_object.nick_name else True,
            )
            .order_by(desc(CanteenUser.create_time))
            .distinct()
        )
        user_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return user_list

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: int) -> CanteenUser | None:
        """
        根据用户ID获取用户信息

        :param db: orm对象
        :param user_id: 用户ID
        :return: 用户信息对象
        """
        user_info = (
            (await db.execute(select(CanteenUser).where(CanteenUser.user_id == user_id).distinct()))
            .scalars()
            .first()
        )
        return user_info

    @classmethod
    async def add_user_dao(cls, db: AsyncSession, user: CanteenUserModel) -> CanteenUser:
        """
        新增用户数据库操作

        :param db: orm对象
        :param user: 用户对象
        :return: 新增的用户对象
        """
        db_user = CanteenUser(**user.model_dump())
        db.add(db_user)
        await db.flush()
        return db_user

    @classmethod
    async def edit_user_dao(cls, db: AsyncSession, user: dict) -> None:
        """
        编辑用户数据库操作

        :param db: orm对象
        :param user: 需要更新的用户字典
        :return:
        """
        user_id = user.pop('user_id', None)
        if not user_id:
            raise ValueError('user_id 不能为空，无法更新用户信息')
        if user:
            await db.execute(update(CanteenUser).where(CanteenUser.user_id == user_id).values(**user))

    @classmethod
    async def delete_user_dao(cls, db: AsyncSession, user: CanteenUserModel) -> None:
        """
        删除用户数据库操作

        :param db: orm对象
        :param user: 用户对象
        :return:
        """
        await db.execute(delete(CanteenUser).where(CanteenUser.user_id == user.user_id))

    @classmethod
    async def reset_user_password_dao(cls, db: AsyncSession, user_id: int, new_password: str) -> None:
        """
        重置用户密码数据库操作

        :param db: orm对象
        :param user_id: 用户ID
        :param new_password: 新密码
        :return:
        """
        await db.execute(
            update(CanteenUser).where(CanteenUser.user_id == user_id).values(password=new_password)
        )

    @classmethod
    async def get_inventory_list(
        cls, db: AsyncSession, query_object: CanteenInventoryPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取库存列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 库存列表信息对象
        """
        query = (
            select(InventoryRecord)
            .where(
                InventoryRecord.status == query_object.status if query_object.status else True,
                InventoryRecord.item_type == query_object.item_type if query_object.item_type else True,
                InventoryRecord.item_name.like(f'%{query_object.item_name}%') if query_object.item_name else True,
            )
            .order_by(desc(InventoryRecord.create_time))
            .distinct()
        )
        inventory_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return inventory_list

    @classmethod
    async def get_inventory_by_id(cls, db: AsyncSession, record_id: int) -> InventoryRecord | None:
        """
        根据记录ID获取库存信息

        :param db: orm对象
        :param record_id: 记录ID
        :return: 库存信息对象
        """
        inventory_info = (
            (await db.execute(select(InventoryRecord).where(InventoryRecord.record_id == record_id).distinct()))
            .scalars()
            .first()
        )
        return inventory_info

    @classmethod
    async def add_inventory_dao(cls, db: AsyncSession, inventory: CanteenInventoryModel) -> InventoryRecord:
        """
        新增库存数据库操作

        :param db: orm对象
        :param inventory: 库存对象
        :return: 新增的库存对象
        """
        db_inventory = InventoryRecord(**inventory.model_dump())
        db.add(db_inventory)
        await db.flush()
        return db_inventory

    @classmethod
    async def edit_inventory_dao(cls, db: AsyncSession, inventory: dict) -> None:
        """
        编辑库存数据库操作

        :param db: orm对象
        :param inventory: 需要更新的库存字典
        :return:
        """
        record_id = inventory.pop('record_id', None)
        if not record_id:
            raise ValueError('record_id 不能为空，无法更新库存信息')
        if inventory:
            await db.execute(update(InventoryRecord).where(InventoryRecord.record_id == record_id).values(**inventory))

    @classmethod
    async def delete_inventory_dao(cls, db: AsyncSession, inventory: CanteenInventoryModel) -> None:
        """
        删除库存数据库操作

        :param db: orm对象
        :param inventory: 库存对象
        :return:
        """
        await db.execute(delete(InventoryRecord).where(InventoryRecord.record_id == inventory.record_id))

    @classmethod
    async def get_profit_list(
        cls, db: AsyncSession, query_object: CanteenProfitPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取利润记录列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 利润记录列表信息对象
        """
        query = (
            select(ProfitAnalysis)
            .where(
                ProfitAnalysis.period_type == query_object.period_type if query_object.period_type else True,
                ProfitAnalysis.period_name.like(f'%{query_object.period_name}%') if query_object.period_name else True,
            )
            .order_by(desc(ProfitAnalysis.create_time))
            .distinct()
        )
        profit_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return profit_list

    @classmethod
    async def get_profit_by_id(cls, db: AsyncSession, record_id: int) -> ProfitAnalysis | None:
        """
        根据记录ID获取利润记录信息

        :param db: orm对象
        :param record_id: 记录ID
        :return: 利润记录信息对象
        """
        profit_info = (
            (await db.execute(select(ProfitAnalysis).where(ProfitAnalysis.record_id == record_id).distinct()))
            .scalars()
            .first()
        )
        return profit_info

    @classmethod
    async def add_profit_dao(cls, db: AsyncSession, profit: CanteenProfitModel) -> ProfitAnalysis:
        """
        新增利润记录数据库操作

        :param db: orm对象
        :param profit: 利润记录对象
        :return: 新增的利润记录对象
        """
        db_profit = ProfitAnalysis(**profit.model_dump())
        db.add(db_profit)
        await db.flush()
        return db_profit

    @classmethod
    async def edit_profit_dao(cls, db: AsyncSession, profit: dict) -> None:
        """
        编辑利润记录数据库操作

        :param db: orm对象
        :param profit: 需要更新的利润记录字典
        :return:
        """
        record_id = profit.pop('record_id', None)
        if not record_id:
            raise ValueError('record_id 不能为空，无法更新利润记录信息')
        if profit:
            await db.execute(update(ProfitAnalysis).where(ProfitAnalysis.record_id == record_id).values(**profit))

    @classmethod
    async def delete_profit_dao(cls, db: AsyncSession, profit: CanteenProfitModel) -> None:
        """
        删除利润记录数据库操作

        :param db: orm对象
        :param profit: 利润记录对象
        :return:
        """
        await db.execute(delete(ProfitAnalysis).where(ProfitAnalysis.record_id == profit.record_id))

    @classmethod
    async def get_revenue_expense_list(
        cls, db: AsyncSession, query_object: CanteenRevenueExpensePageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取收支记录列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 收支记录列表信息对象
        """
        query = (
            select(RevenueExpense)
            .where(
                RevenueExpense.status == query_object.status if query_object.status else True,
                RevenueExpense.record_type == query_object.record_type if query_object.record_type else True,
                RevenueExpense.category == query_object.category if query_object.category else True,
                RevenueExpense.item_name.like(f'%{query_object.item_name}%') if query_object.item_name else True,
            )
            .order_by(desc(RevenueExpense.create_time))
            .distinct()
        )
        revenue_expense_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return revenue_expense_list

    @classmethod
    async def get_revenue_expense_by_id(cls, db: AsyncSession, record_id: int) -> RevenueExpense | None:
        """
        根据记录ID获取收支记录信息

        :param db: orm对象
        :param record_id: 记录ID
        :return: 收支记录信息对象
        """
        revenue_expense_info = (
            (await db.execute(select(RevenueExpense).where(RevenueExpense.record_id == record_id).distinct()))
            .scalars()
            .first()
        )
        return revenue_expense_info

    @classmethod
    async def add_revenue_expense_dao(cls, db: AsyncSession, revenue_expense: CanteenRevenueExpenseModel) -> RevenueExpense:
        """
        新增收支记录数据库操作

        :param db: orm对象
        :param revenue_expense: 收支记录对象
        :return: 新增的收支记录对象
        """
        db_revenue_expense = RevenueExpense(**revenue_expense.model_dump())
        db.add(db_revenue_expense)
        await db.flush()
        return db_revenue_expense

    @classmethod
    async def edit_revenue_expense_dao(cls, db: AsyncSession, revenue_expense: dict) -> None:
        """
        编辑收支记录数据库操作

        :param db: orm对象
        :param revenue_expense: 需要更新的收支记录字典
        :return:
        """
        record_id = revenue_expense.pop('record_id', None)
        if not record_id:
            raise ValueError('record_id 不能为空，无法更新收支记录信息')
        if revenue_expense:
            await db.execute(update(RevenueExpense).where(RevenueExpense.record_id == record_id).values(**revenue_expense))

    @classmethod
    async def delete_revenue_expense_dao(cls, db: AsyncSession, revenue_expense: CanteenRevenueExpenseModel) -> None:
        """
        删除收支记录数据库操作

        :param db: orm对象
        :param revenue_expense: 收支记录对象
        :return:
        """
        await db.execute(delete(RevenueExpense).where(RevenueExpense.record_id == revenue_expense.record_id))
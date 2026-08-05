from datetime import datetime, timedelta

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.canteen_do import CanteenUser, OrderDetail, OrderRecord
from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.income_expense_do import IncomeExpense
from module_admin.entity.do.inventory_do import Inventory
from module_admin.entity.do.log_do import SysOperLog, SysLogininfor
from module_admin.entity.do.role_do import SysRole
from module_admin.entity.do.user_do import SysUser, SysUserRole


class VisualizationDao:
    """
    可视化模块数据库操作层
    """

    # -------------------- 食堂销售相关 --------------------

    @classmethod
    async def get_canteen_summary(cls, db: AsyncSession) -> dict:
        """
        获取食堂销售汇总信息
        """
        total_amount_stmt = select(func.coalesce(func.sum(OrderRecord.total_amount), 0.0))
        total_orders_stmt = select(func.count(OrderRecord.order_id))
        member_count_stmt = select(func.count(CanteenUser.user_id))

        total_amount = (await db.execute(total_amount_stmt)).scalar() or 0.0
        total_orders = (await db.execute(total_orders_stmt)).scalar() or 0
        member_count = (await db.execute(member_count_stmt)).scalar() or 0

        avg_amount = float(total_amount) / total_orders if total_orders else 0.0

        return {
            'total_amount': float(total_amount),
            'total_orders': int(total_orders),
            'avg_amount': round(avg_amount, 2),
            'member_count': int(member_count),
        }

    @classmethod
    async def get_hot_dishes_top(cls, db: AsyncSession, top_n: int = 5) -> list[dict]:
        """
        获取热销菜品 TOP N
        """
        stmt = (
            select(
                OrderDetail.menu_name,
                func.sum(OrderDetail.quantity).label('total_quantity'),
                func.sum(OrderDetail.amount).label('total_amount'),
            )
            .group_by(OrderDetail.menu_name)
            .order_by(func.sum(OrderDetail.quantity).desc())
            .limit(top_n)
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'menu_name': row.menu_name or '未命名',
                'total_quantity': int(row.total_quantity or 0),
                'total_amount': float(row.total_amount or 0.0),
            }
            for row in rows
        ]

    @classmethod
    async def get_daily_trend(cls, db: AsyncSession, days: int = 30) -> list[dict]:
        """
        获取过去 N 天的日销售趋势（每日销售额 + 订单数）
        """
        start_date = datetime.now() - timedelta(days=days - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = (
            select(
                func.date_format(OrderRecord.create_time, '%Y-%m-%d').label('date'),
                func.coalesce(func.sum(OrderRecord.total_amount), 0.0).label('amount'),
                func.count(OrderRecord.order_id).label('order_count'),
            )
            .where(and_(OrderRecord.create_time >= start_date))
            .group_by(func.date_format(OrderRecord.create_time, '%Y-%m-%d'))
            .order_by('date')
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        data_map = {row.date: {'amount': float(row.amount or 0.0), 'order_count': int(row.order_count or 0)} for row in rows}

        full_dates = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            item = data_map.get(date_str, {'amount': 0.0, 'order_count': 0})
            full_dates.append(
                {
                    'date': date_str,
                    'amount': round(float(item['amount']), 2),
                    'order_count': int(item['order_count']),
                }
            )
        return full_dates

    @classmethod
    async def get_dish_ranking(cls, db: AsyncSession, top_n: int = 20) -> list[dict]:
        """
        获取菜品销售排行
        """
        stmt = (
            select(
                OrderDetail.menu_id,
                OrderDetail.menu_name,
                func.sum(OrderDetail.quantity).label('total_quantity'),
                func.sum(OrderDetail.amount).label('total_amount'),
            )
            .group_by(OrderDetail.menu_id, OrderDetail.menu_name)
            .order_by(func.sum(OrderDetail.amount).desc())
            .limit(top_n)
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'menu_id': row.menu_id,
                'menu_name': row.menu_name or '未命名',
                'total_quantity': int(row.total_quantity or 0),
                'total_amount': round(float(row.total_amount or 0.0), 2),
            }
            for row in rows
        ]

    # -------------------- 日志分析相关 --------------------

    @classmethod
    async def get_log_summary(cls, db: AsyncSession) -> dict:
        """
        获取系统日志监控汇总
        """
        total_request_stmt = select(func.count(SysOperLog.oper_id))
        success_request_stmt = select(func.count(SysOperLog.oper_id)).where(SysOperLog.status == 0)
        failed_request_stmt = select(func.count(SysOperLog.oper_id)).where(SysOperLog.status != 0)
        avg_response_stmt = select(func.avg(SysOperLog.cost_time)).where(SysOperLog.cost_time.isnot(None))

        total_login_stmt = select(func.count(SysLogininfor.info_id))
        success_login_stmt = select(func.count(SysLogininfor.info_id)).where(SysLogininfor.status == '0')
        failed_login_stmt = select(func.count(SysLogininfor.info_id)).where(SysLogininfor.status != '0')

        total_request = (await db.execute(total_request_stmt)).scalar() or 0
        success_request = (await db.execute(success_request_stmt)).scalar() or 0
        failed_request = (await db.execute(failed_request_stmt)).scalar() or 0
        avg_response = (await db.execute(avg_response_stmt)).scalar() or 0.0

        total_login = (await db.execute(total_login_stmt)).scalar() or 0
        success_login = (await db.execute(success_login_stmt)).scalar() or 0
        failed_login = (await db.execute(failed_login_stmt)).scalar() or 0

        return {
            'total_request': int(total_request),
            'success_request': int(success_request),
            'failed_request': int(failed_request),
            'avg_response_time': round(float(avg_response or 0.0), 2),
            'total_login': int(total_login),
            'success_login': int(success_login),
            'failed_login': int(failed_login),
        }

    @classmethod
    async def get_log_trend(cls, db: AsyncSession, days: int = 7) -> list[dict]:
        """
        获取近 N 天请求趋势
        """
        start_date = datetime.now() - timedelta(days=days - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = (
            select(
                func.date_format(SysOperLog.oper_time, '%Y-%m-%d').label('date'),
                func.count(SysOperLog.oper_id).label('total'),
                func.sum(case((SysOperLog.status == 0, 1), else_=0)).label('success'),
                func.sum(case((SysOperLog.status != 0, 1), else_=0)).label('failed'),
            )
            .where(SysOperLog.oper_time >= start_date)
            .group_by(func.date_format(SysOperLog.oper_time, '%Y-%m-%d'))
            .order_by('date')
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        data_map = {
            row.date: {
                'total': int(row.total or 0),
                'success': int(row.success or 0),
                'failed': int(row.failed or 0),
            }
            for row in rows
        }

        full_dates = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            item = data_map.get(date_str, {'total': 0, 'success': 0, 'failed': 0})
            full_dates.append(
                {
                    'date': date_str,
                    'total': int(item['total']),
                    'success': int(item['success']),
                    'failed': int(item['failed']),
                }
            )
        return full_dates

    @classmethod
    async def get_log_type_distribution(cls, db: AsyncSession, top_n: int = 10) -> list[dict]:
        """
        请求类型/模块分布
        """
        stmt = (
            select(
                SysOperLog.title.label('title'),
                func.count(SysOperLog.oper_id).label('count'),
            )
            .group_by(SysOperLog.title)
            .order_by(func.count(SysOperLog.oper_id).desc())
            .limit(top_n)
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'title': row.title or '未分类',
                'count': int(row.count or 0),
            }
            for row in rows
        ]

    # -------------------- 用户与部门分析 --------------------

    @classmethod
    async def get_user_summary(cls, db: AsyncSession) -> dict:
        """
        用户与部门汇总
        """
        total_user_stmt = select(func.count(SysUser.user_id)).where(SysUser.del_flag == '0')
        active_user_stmt = select(func.count(SysUser.user_id)).where(
            and_(SysUser.del_flag == '0', SysUser.status == '0')
        )
        dept_stmt = select(func.count(SysDept.dept_id)).where(SysDept.status == '0')

        total_user = (await db.execute(total_user_stmt)).scalar() or 0
        active_user = (await db.execute(active_user_stmt)).scalar() or 0
        dept_count = (await db.execute(dept_stmt)).scalar() or 0

        return {
            'total_user': int(total_user),
            'active_user': int(active_user),
            'disabled_user': int(total_user - active_user),
            'dept_count': int(dept_count),
        }

    @classmethod
    async def get_user_by_dept(cls, db: AsyncSession) -> list[dict]:
        """
        用户按部门分布
        """
        stmt = (
            select(
                SysDept.dept_name,
                func.count(SysUser.user_id).label('user_count'),
            )
            .select_from(SysDept)
            .outerjoin(SysUser, SysUser.dept_id == SysDept.dept_id)
            .where(and_(SysDept.status == '0', SysUser.del_flag == '0'))
            .group_by(SysDept.dept_id, SysDept.dept_name)
            .order_by(func.count(SysUser.user_id).desc())
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'dept_name': row.dept_name or '未分配部门',
                'user_count': int(row.user_count or 0),
            }
            for row in rows
        ]

    @classmethod
    async def get_user_by_status(cls, db: AsyncSession) -> list[dict]:
        """
        用户按状态分布
        """
        stmt = (
            select(
                SysUser.status,
                func.count(SysUser.user_id).label('user_count'),
            )
            .where(SysUser.del_flag == '0')
            .group_by(SysUser.status)
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        status_map = {'0': '正常', '1': '停用'}
        total = sum(int(row.user_count or 0) for row in rows)
        return [
            {
                'status': status_map.get(row.status, row.status or '未知'),
                'status_code': row.status,
                'user_count': int(row.user_count or 0),
                'ratio': round((int(row.user_count or 0) / total * 100), 2) if total else 0.0,
            }
            for row in rows
        ]

    @classmethod
    async def get_canteen_hourly_distribution(cls, db: AsyncSession, days: int = 7) -> list[dict]:
        """
        获取食堂销售按小时分布（0-23小时）
        """
        start_date = datetime.now() - timedelta(days=days - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = (
            select(
                func.date_format(OrderRecord.create_time, '%H').label('hour'),
                func.coalesce(func.sum(OrderRecord.total_amount), 0.0).label('amount'),
                func.count(OrderRecord.order_id).label('count'),
            )
            .where(and_(OrderRecord.create_time >= start_date))
            .group_by(func.date_format(OrderRecord.create_time, '%H'))
            .order_by('hour')
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        data_map = {row.hour: {'amount': float(row.amount or 0.0), 'count': int(row.count or 0)} for row in rows}

        full_hours = []
        for h in range(24):
            hour_str = f'{h:02d}'
            item = data_map.get(hour_str, {'amount': 0.0, 'count': 0})
            full_hours.append(
                {
                    'hour': hour_str,
                    'amount': round(float(item['amount']), 2),
                    'count': int(item['count']),
                }
            )
        return full_hours

    @classmethod
    async def get_log_login_stats(cls, db: AsyncSession, days: int = 7) -> list[dict]:
        """
        获取登录成功/失败按日统计
        """
        start_date = datetime.now() - timedelta(days=days - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = (
            select(
                func.date_format(SysLogininfor.login_time, '%Y-%m-%d').label('date'),
                func.sum(case((SysLogininfor.status == '0', 1), else_=0)).label('success_count'),
                func.sum(case((SysLogininfor.status != '0', 1), else_=0)).label('fail_count'),
            )
            .where(SysLogininfor.login_time >= start_date)
            .group_by(func.date_format(SysLogininfor.login_time, '%Y-%m-%d'))
            .order_by('date')
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        data_map = {row.date: {'success_count': int(row.success_count or 0), 'fail_count': int(row.fail_count or 0)} for row in rows}

        full_dates = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            item = data_map.get(date_str, {'success_count': 0, 'fail_count': 0})
            full_dates.append(
                {
                    'date': date_str,
                    'success_count': int(item['success_count']),
                    'fail_count': int(item['fail_count']),
                }
            )
        return full_dates

    @classmethod
    async def get_user_register_trend(cls, db: AsyncSession, days: int = 30) -> list[dict]:
        """
        获取用户注册趋势（近 N 天）
        """
        start_date = datetime.now() - timedelta(days=days - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = (
            select(
                func.date_format(SysUser.create_time, '%Y-%m-%d').label('date'),
                func.count(SysUser.user_id).label('count'),
            )
            .where(and_(SysUser.del_flag == '0', SysUser.create_time >= start_date))
            .group_by(func.date_format(SysUser.create_time, '%Y-%m-%d'))
            .order_by('date')
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        data_map = {row.date: int(row.count or 0) for row in rows}

        full_dates = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            item = data_map.get(date_str, 0)
            full_dates.append(
                {
                    'date': date_str,
                    'count': int(item),
                }
            )
        return full_dates

    @classmethod
    async def get_user_by_role(cls, db: AsyncSession) -> list[dict]:
        """
        获取用户按角色分布
        """
        stmt = (
            select(
                SysRole.role_name,
                func.count(SysUserRole.user_id).label('user_count'),
            )
            .select_from(SysRole)
            .outerjoin(SysUserRole, SysUserRole.role_id == SysRole.role_id)
            .where(and_(SysRole.del_flag == '0', SysRole.status == '0'))
            .group_by(SysRole.role_id, SysRole.role_name)
            .order_by(func.count(SysUserRole.user_id).desc())
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        total = sum(int(row.user_count or 0) for row in rows)
        return [
            {
                'role_name': row.role_name or '未知角色',
                'user_count': int(row.user_count or 0),
                'ratio': round((int(row.user_count or 0) / total * 100), 2) if total else 0.0,
            }
            for row in rows
        ]

    # -------------------- 库存管理相关 --------------------

    @classmethod
    async def get_inventory_summary(cls, db: AsyncSession) -> dict:
        """获取库存汇总信息：总物品数、总价值、低库存物品数、分类数量分布"""
        total_items_stmt = select(func.count(Inventory.inventory_id))
        total_value_stmt = select(func.coalesce(func.sum(Inventory.total_value), 0.0))
        low_stock_stmt = select(func.count(Inventory.inventory_id)).where(Inventory.status != '正常')
        category_count_stmt = select(func.count(func.distinct(Inventory.category))).where(
            and_(Inventory.category.isnot(None), Inventory.category != '')
        )

        total_items = (await db.execute(total_items_stmt)).scalar() or 0
        total_value = (await db.execute(total_value_stmt)).scalar() or 0.0
        low_stock_count = (await db.execute(low_stock_stmt)).scalar() or 0
        category_count = (await db.execute(category_count_stmt)).scalar() or 0

        return {
            'total_items': int(total_items),
            'total_value': round(float(total_value), 2),
            'low_stock_count': int(low_stock_count),
            'category_count': int(category_count),
        }

    @classmethod
    async def get_inventory_category_distribution(cls, db: AsyncSession) -> list[dict]:
        """按分类统计库存数量和价值"""
        stmt = (
            select(
                Inventory.category,
                func.count(Inventory.inventory_id).label('item_count'),
                func.coalesce(func.sum(Inventory.quantity), 0.0).label('total_quantity'),
                func.coalesce(func.sum(Inventory.total_value), 0.0).label('total_value'),
            )
            .group_by(Inventory.category)
            .order_by(func.sum(Inventory.total_value).desc())
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'category': row.category or '未分类',
                'item_count': int(row.item_count or 0),
                'total_quantity': round(float(row.total_quantity or 0.0), 2),
                'total_value': round(float(row.total_value or 0.0), 2),
            }
            for row in rows
        ]

    @classmethod
    async def get_inventory_status_distribution(cls, db: AsyncSession) -> list[dict]:
        """按状态统计"""
        stmt = (
            select(
                Inventory.status,
                func.count(Inventory.inventory_id).label('item_count'),
                func.coalesce(func.sum(Inventory.total_value), 0.0).label('total_value'),
            )
            .group_by(Inventory.status)
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'status': row.status or '未知',
                'item_count': int(row.item_count or 0),
                'total_value': round(float(row.total_value or 0.0), 2),
            }
            for row in rows
        ]

    @classmethod
    async def get_inventory_top_items(cls, db: AsyncSession, top_n: int = 10) -> list[dict]:
        """TOP N 高价值库存物品"""
        stmt = (
            select(
                Inventory.item_name,
                Inventory.category,
                Inventory.quantity,
                Inventory.unit,
                Inventory.unit_price,
                Inventory.total_value,
                Inventory.status,
            )
            .order_by(Inventory.total_value.desc())
            .limit(top_n)
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'item_name': row.item_name or '未命名',
                'category': row.category or '未分类',
                'quantity': round(float(row.quantity or 0.0), 2),
                'unit': row.unit or '',
                'unit_price': round(float(row.unit_price or 0.0), 2),
                'total_value': round(float(row.total_value or 0.0), 2),
                'status': row.status or '正常',
            }
            for row in rows
        ]

    @classmethod
    async def get_inventory_low_stock(cls, db: AsyncSession) -> list[dict]:
        """低库存物品列表"""
        stmt = (
            select(
                Inventory.item_name,
                Inventory.category,
                Inventory.quantity,
                Inventory.min_quantity,
                Inventory.location,
                Inventory.status,
            )
            .where(Inventory.status != '正常')
            .order_by(Inventory.quantity.asc())
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'item_name': row.item_name or '未命名',
                'category': row.category or '未分类',
                'quantity': round(float(row.quantity or 0.0), 2),
                'min_quantity': round(float(row.min_quantity or 0.0), 2),
                'location': row.location or '',
                'status': row.status or '低库存',
            }
            for row in rows
        ]

    # -------------------- 收支管理相关 --------------------

    @classmethod
    async def get_income_expense_summary(cls, db: AsyncSession) -> dict:
        """获取收支汇总：总收入、总支出、利润、收入笔数、支出笔数"""
        total_income_stmt = select(func.coalesce(func.sum(IncomeExpense.amount), 0.0)).where(IncomeExpense.record_type == '收入')
        total_expense_stmt = select(func.coalesce(func.sum(IncomeExpense.amount), 0.0)).where(IncomeExpense.record_type == '支出')
        income_count_stmt = select(func.count(IncomeExpense.record_id)).where(IncomeExpense.record_type == '收入')
        expense_count_stmt = select(func.count(IncomeExpense.record_id)).where(IncomeExpense.record_type == '支出')

        total_income = (await db.execute(total_income_stmt)).scalar() or 0.0
        total_expense = (await db.execute(total_expense_stmt)).scalar() or 0.0
        income_count = (await db.execute(income_count_stmt)).scalar() or 0
        expense_count = (await db.execute(expense_count_stmt)).scalar() or 0

        return {
            'total_income': round(float(total_income), 2),
            'total_expense': round(float(total_expense), 2),
            'profit': round(float(total_income) - float(total_expense), 2),
            'income_count': int(income_count),
            'expense_count': int(expense_count),
        }

    @classmethod
    async def get_income_expense_category(cls, db: AsyncSession) -> list[dict]:
        """按分类统计收支金额"""
        stmt = (
            select(
                IncomeExpense.category,
                IncomeExpense.record_type,
                func.coalesce(func.sum(IncomeExpense.amount), 0.0).label('total_amount'),
                func.count(IncomeExpense.record_id).label('record_count'),
            )
            .group_by(IncomeExpense.category, IncomeExpense.record_type)
            .order_by(func.sum(IncomeExpense.amount).desc())
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'category': row.category or '未分类',
                'record_type': row.record_type or '未知',
                'total_amount': round(float(row.total_amount or 0.0), 2),
                'record_count': int(row.record_count or 0),
            }
            for row in rows
        ]

    @classmethod
    async def get_income_expense_daily_trend(cls, db: AsyncSession, days: int = 30) -> list[dict]:
        """近 N 天的每日收入/支出趋势"""
        start_date = datetime.now() - timedelta(days=days - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        income_stmt = (
            select(
                func.date_format(IncomeExpense.record_date, '%Y-%m-%d').label('date'),
                func.coalesce(func.sum(IncomeExpense.amount), 0.0).label('income'),
            )
            .where(and_(IncomeExpense.record_type == '收入', IncomeExpense.record_date >= start_date))
            .group_by(func.date_format(IncomeExpense.record_date, '%Y-%m-%d'))
        )
        income_result = await db.execute(income_stmt)
        income_rows = income_result.fetchall()
        income_map = {row.date: float(row.income or 0.0) for row in income_rows}

        expense_stmt = (
            select(
                func.date_format(IncomeExpense.record_date, '%Y-%m-%d').label('date'),
                func.coalesce(func.sum(IncomeExpense.amount), 0.0).label('expense'),
            )
            .where(and_(IncomeExpense.record_type == '支出', IncomeExpense.record_date >= start_date))
            .group_by(func.date_format(IncomeExpense.record_date, '%Y-%m-%d'))
        )
        expense_result = await db.execute(expense_stmt)
        expense_rows = expense_result.fetchall()
        expense_map = {row.date: float(row.expense or 0.0) for row in expense_rows}

        full_dates = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            income = income_map.get(date_str, 0.0)
            expense = expense_map.get(date_str, 0.0)
            full_dates.append(
                {
                    'date': date_str,
                    'income': round(income, 2),
                    'expense': round(expense, 2),
                    'profit': round(income - expense, 2),
                }
            )
        return full_dates

    @classmethod
    async def get_income_expense_payment_method(cls, db: AsyncSession) -> list[dict]:
        """按支付方式统计"""
        stmt = (
            select(
                IncomeExpense.payment_method,
                func.coalesce(func.sum(IncomeExpense.amount), 0.0).label('total_amount'),
                func.count(IncomeExpense.record_id).label('record_count'),
            )
            .group_by(IncomeExpense.payment_method)
            .order_by(func.sum(IncomeExpense.amount).desc())
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'payment_method': row.payment_method or '未分类',
                'total_amount': round(float(row.total_amount or 0.0), 2),
                'record_count': int(row.record_count or 0),
            }
            for row in rows
        ]

    @classmethod
    async def get_income_expense_top_records(cls, db: AsyncSession, top_n: int = 10) -> list[dict]:
        """TOP N 大额收支记录"""
        stmt = (
            select(
                IncomeExpense.record_type,
                IncomeExpense.category,
                IncomeExpense.amount,
                IncomeExpense.payment_method,
                IncomeExpense.description,
                IncomeExpense.record_date,
                IncomeExpense.operator,
            )
            .order_by(IncomeExpense.amount.desc())
            .limit(top_n)
        )
        result = await db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                'record_type': row.record_type or '未知',
                'category': row.category or '未分类',
                'amount': round(float(row.amount or 0.0), 2),
                'payment_method': row.payment_method or '',
                'description': row.description or '',
                'record_date': row.record_date.strftime('%Y-%m-%d %H:%M:%S') if row.record_date else '',
                'operator': row.operator or '',
            }
            for row in rows
        ]

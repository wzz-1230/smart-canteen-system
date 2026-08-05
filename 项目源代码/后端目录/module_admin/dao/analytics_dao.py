from collections.abc import Sequence
from datetime import datetime, time
from typing import Any

from sqlalchemy import ColumnElement, and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.analytics_do import InventoryRecord, ProfitAnalysis, RevenueExpense
from utils.page_util import PageUtil


class AnalyticsDao:
    """
    数据分析模块数据库操作层
    """

    # -------------------- 库存相关 --------------------

    @classmethod
    async def get_inventory_list(
        cls, db: AsyncSession, query_object: Any, is_page: bool = False
    ) -> Any:
        """
        获取库存记录列表
        """
        conditions = []
        if hasattr(query_object, 'item_name') and query_object.item_name:
            conditions.append(InventoryRecord.item_name.like(f'%{query_object.item_name}%'))
        if hasattr(query_object, 'item_type') and query_object.item_type:
            conditions.append(InventoryRecord.item_type == query_object.item_type)
        if hasattr(query_object, 'status') and query_object.status:
            conditions.append(InventoryRecord.status == query_object.status)
        if (
            hasattr(query_object, 'begin_time')
            and query_object.begin_time
            and hasattr(query_object, 'end_time')
            and query_object.end_time
        ):
            conditions.append(
                InventoryRecord.record_date.between(
                    datetime.strptime(query_object.begin_time, '%Y-%m-%d'),
                    datetime.combine(
                        datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)
                    ),
                )
            )

        query = select(InventoryRecord).where(and_(*conditions)).order_by(InventoryRecord.record_id.desc())
        result = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return result

    @classmethod
    async def get_inventory_by_id(cls, db: AsyncSession, record_id: int) -> InventoryRecord | None:
        """
        根据ID获取库存记录
        """
        result = (
            (await db.execute(select(InventoryRecord).where(InventoryRecord.record_id == record_id)))
            .scalars()
            .first()
        )
        return result

    @classmethod
    async def add_inventory_dao(cls, db: AsyncSession, inventory: dict) -> InventoryRecord:
        """
        新增库存记录
        """
        db_obj = InventoryRecord(**inventory)
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def edit_inventory_dao(cls, db: AsyncSession, inventory: dict) -> None:
        """
        编辑库存记录
        """
        record_id = inventory.pop('record_id', None)
        if record_id:
            await db.execute(
                update(InventoryRecord).where(InventoryRecord.record_id == record_id).values(**inventory)
            )

    @classmethod
    async def delete_inventory_dao(cls, db: AsyncSession, record_id: int) -> None:
        """
        删除库存记录
        """
        from sqlalchemy import delete

        await db.execute(delete(InventoryRecord).where(InventoryRecord.record_id == record_id))

    @classmethod
    async def get_inventory_summary(cls, db: AsyncSession) -> dict:
        """
        获取库存汇总统计
        """
        total_items_result = (
            (await db.execute(select(func.count(InventoryRecord.record_id))))
        ).scalar() or 0

        total_value_result = (
            (await db.execute(select(func.sum(InventoryRecord.total_value))))
        ).scalar() or 0

        low_stock_result = (
            (await db.execute(select(func.count(InventoryRecord.record_id)).where(InventoryRecord.status != '0')))
        ).scalar() or 0

        avg_turnover_result = (
            (await db.execute(select(func.avg(InventoryRecord.turnover_rate))))
        ).scalar() or 0

        return {
            'total_items': total_items_result,
            'total_value': total_value_result,
            'low_stock_items': low_stock_result,
            'avg_turnover_rate': avg_turnover_result,
        }

    @classmethod
    async def get_inventory_turnover_trend(cls, db: AsyncSession, limit: int = 10) -> list[dict]:
        """
        获取库存周转趋势数据
        """
        query = (
            select(InventoryRecord.item_name, InventoryRecord.turnover_rate, InventoryRecord.total_value)
            .order_by(InventoryRecord.record_date.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        rows = result.all()
        return [
            {'name': row.item_name, 'value': float(row.turnover_rate or 0), 'total_value': float(row.total_value or 0)}
            for row in rows
        ]

    @classmethod
    async def get_inventory_type_distribution(cls, db: AsyncSession) -> list[dict]:
        """
        获取物品类型分布
        """
        type_map = {'0': '食材', '1': '调料', '2': '餐具', '3': '饮品'}
        query = select(InventoryRecord.item_type, func.sum(InventoryRecord.total_value)).group_by(
            InventoryRecord.item_type
        )
        result = await db.execute(query)
        rows = result.all()

        total = sum(float(row[1] or 0) for row in rows)
        return [
            {
                'name': type_map.get(str(row[0]), '其他'),
                'value': float(row[1] or 0),
                'percentage': round((float(row[1] or 0) / total * 100) if total > 0 else 0, 2),
            }
            for row in rows
        ]

    # -------------------- 收支相关 --------------------

    @classmethod
    async def get_revenue_expense_list(
        cls, db: AsyncSession, query_object: Any, is_page: bool = False
    ) -> Any:
        """
        获取收支明细列表
        """
        conditions = []
        if hasattr(query_object, 'record_type') and query_object.record_type:
            conditions.append(RevenueExpense.record_type == query_object.record_type)
        if hasattr(query_object, 'category') and query_object.category:
            conditions.append(RevenueExpense.category.like(f'%{query_object.category}%'))
        if hasattr(query_object, 'item_name') and query_object.item_name:
            conditions.append(RevenueExpense.item_name.like(f'%{query_object.item_name}%'))
        if (
            hasattr(query_object, 'begin_time')
            and query_object.begin_time
            and hasattr(query_object, 'end_time')
            and query_object.end_time
        ):
            conditions.append(
                RevenueExpense.record_date.between(
                    datetime.strptime(query_object.begin_time, '%Y-%m-%d'),
                    datetime.combine(
                        datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)
                    ),
                )
            )

        query = select(RevenueExpense).where(and_(*conditions)).order_by(RevenueExpense.record_date.desc())
        result = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return result

    @classmethod
    async def get_revenue_expense_by_id(cls, db: AsyncSession, record_id: int) -> RevenueExpense | None:
        """
        根据ID获取收支明细
        """
        result = (
            (await db.execute(select(RevenueExpense).where(RevenueExpense.record_id == record_id)))
            .scalars()
            .first()
        )
        return result

    @classmethod
    async def add_revenue_expense_dao(cls, db: AsyncSession, data: dict) -> RevenueExpense:
        """
        新增收支明细
        """
        db_obj = RevenueExpense(**data)
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def edit_revenue_expense_dao(cls, db: AsyncSession, data: dict) -> None:
        """
        编辑收支明细
        """
        record_id = data.pop('record_id', None)
        if record_id:
            await db.execute(
                update(RevenueExpense).where(RevenueExpense.record_id == record_id).values(**data)
            )

    @classmethod
    async def delete_revenue_expense_dao(cls, db: AsyncSession, record_id: int) -> None:
        """
        删除收支明细
        """
        from sqlalchemy import delete

        await db.execute(delete(RevenueExpense).where(RevenueExpense.record_id == record_id))

    @classmethod
    async def get_revenue_expense_summary(cls, db: AsyncSession) -> dict:
        """
        获取收支汇总统计
        """
        total_revenue = (
            (await db.execute(select(func.sum(RevenueExpense.amount)).where(RevenueExpense.record_type == '0')))
        ).scalar() or 0

        total_cost = (
            (await db.execute(select(func.sum(RevenueExpense.amount)).where(RevenueExpense.record_type == '1')))
        ).scalar() or 0

        return {
            'total_revenue': float(total_revenue),
            'total_cost': float(total_cost),
            'total_profit': float(total_revenue - total_cost),
            'profit_rate': round(((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0, 2),
        }

    @classmethod
    async def get_revenue_expense_trend(cls, db: AsyncSession, limit: int = 12) -> list[dict]:
        """
        获取收支趋势数据（按月汇总）
        """
        from sqlalchemy import func, cast

        if False:
            # sqlite placeholder
            pass

        # 按日期分组获取每月收入和支出
        query = (
            select(
                RevenueExpense.record_type,
                func.strftime('%Y-%m', RevenueExpense.record_date).label('month'),
                func.sum(RevenueExpense.amount).label('total'),
            )
            .group_by('month', RevenueExpense.record_type)
            .order_by('month')
        )
        result = await db.execute(query)
        rows = result.all()

        # 重组数据: 按月汇总收入和支出
        month_map: dict[str, dict[str, float]] = {}
        for row in rows:
            month = row[1]
            total = float(row[2] or 0)
            if month not in month_map:
                month_map[month] = {'revenue': 0, 'cost': 0}
            if row[0] == '0':
                month_map[month]['revenue'] = total
            else:
                month_map[month]['cost'] = total

        # 排序并限制数量
        sorted_months = sorted(month_map.keys())[-limit:]
        result_list = []
        for month in sorted_months:
            data = month_map[month]
            result_list.append(
                {
                    'name': month,
                    'revenue': data['revenue'],
                    'cost': data['cost'],
                    'profit': data['revenue'] - data['cost'],
                }
            )
        return result_list

    @classmethod
    async def get_expense_category_distribution(cls, db: AsyncSession) -> list[dict]:
        """
        获取支出分类分布
        """
        query = (
            select(RevenueExpense.category, func.sum(RevenueExpense.amount))
            .where(RevenueExpense.record_type == '1')
            .group_by(RevenueExpense.category)
        )
        result = await db.execute(query)
        rows = result.all()

        total = sum(float(row[1] or 0) for row in rows)
        return [
            {
                'name': row[0] or '其他',
                'value': float(row[1] or 0),
                'percentage': round((float(row[1] or 0) / total * 100) if total > 0 else 0, 2),
            }
            for row in rows
        ]

    @classmethod
    async def get_revenue_category_distribution(cls, db: AsyncSession) -> list[dict]:
        """
        获取收入分类分布
        """
        query = (
            select(RevenueExpense.category, func.sum(RevenueExpense.amount))
            .where(RevenueExpense.record_type == '0')
            .group_by(RevenueExpense.category)
        )
        result = await db.execute(query)
        rows = result.all()

        total = sum(float(row[1] or 0) for row in rows)
        return [
            {
                'name': row[0] or '其他',
                'value': float(row[1] or 0),
                'percentage': round((float(row[1] or 0) / total * 100) if total > 0 else 0, 2),
            }
            for row in rows
        ]

    # -------------------- 利润相关 --------------------

    @classmethod
    async def get_profit_list(cls, db: AsyncSession, query_object: Any, is_page: bool = False) -> Any:
        """
        获取利润分析列表
        """
        conditions = []
        if hasattr(query_object, 'period_type') and query_object.period_type:
            conditions.append(ProfitAnalysis.period_type == query_object.period_type)
        if hasattr(query_object, 'period_name') and query_object.period_name:
            conditions.append(ProfitAnalysis.period_name.like(f'%{query_object.period_name}%'))
        if (
            hasattr(query_object, 'begin_time')
            and query_object.begin_time
            and hasattr(query_object, 'end_time')
            and query_object.end_time
        ):
            conditions.append(
                ProfitAnalysis.start_date.between(
                    datetime.strptime(query_object.begin_time, '%Y-%m-%d'),
                    datetime.strptime(query_object.end_time, '%Y-%m-%d'),
                )
            )

        query = select(ProfitAnalysis).where(and_(*conditions)).order_by(ProfitAnalysis.start_date.desc())
        result = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return result

    @classmethod
    async def get_profit_by_id(cls, db: AsyncSession, record_id: int) -> ProfitAnalysis | None:
        """
        根据ID获取利润分析
        """
        result = (
            (await db.execute(select(ProfitAnalysis).where(ProfitAnalysis.record_id == record_id)))
            .scalars()
            .first()
        )
        return result

    @classmethod
    async def add_profit_dao(cls, db: AsyncSession, data: dict) -> ProfitAnalysis:
        """
        新增利润分析
        """
        db_obj = ProfitAnalysis(**data)
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def edit_profit_dao(cls, db: AsyncSession, data: dict) -> None:
        """
        编辑利润分析
        """
        record_id = data.pop('record_id', None)
        if record_id:
            await db.execute(update(ProfitAnalysis).where(ProfitAnalysis.record_id == record_id).values(**data))

    @classmethod
    async def delete_profit_dao(cls, db: AsyncSession, record_id: int) -> None:
        """
        删除利润分析
        """
        from sqlalchemy import delete

        await db.execute(delete(ProfitAnalysis).where(ProfitAnalysis.record_id == record_id))

    @classmethod
    async def get_profit_summary(cls, db: AsyncSession) -> dict:
        """
        获取利润汇总统计
        """
        total_revenue = (
            (await db.execute(select(func.sum(ProfitAnalysis.revenue))))
        ).scalar() or 0

        total_cost = (
            (await db.execute(select(func.sum(ProfitAnalysis.cost))))
        ).scalar() or 0

        total_profit = (
            (await db.execute(select(func.sum(ProfitAnalysis.profit))))
        ).scalar() or 0

        avg_profit_rate = (
            (await db.execute(select(func.avg(ProfitAnalysis.profit_rate))))
        ).scalar() or 0

        total_orders = (
            (await db.execute(select(func.sum(ProfitAnalysis.order_count))))
        ).scalar() or 0

        avg_order_amount = (
            (await db.execute(select(func.avg(ProfitAnalysis.avg_order_amount))))
        ).scalar() or 0

        return {
            'total_revenue': float(total_revenue),
            'total_cost': float(total_cost),
            'total_profit': float(total_profit),
            'avg_profit_rate': float(avg_profit_rate),
            'total_orders': int(total_orders),
            'avg_order_amount': float(avg_order_amount),
        }

    @classmethod
    async def get_profit_trend(cls, db: AsyncSession, limit: int = 12) -> list[dict]:
        """
        获取利润趋势数据
        """
        query = (
            select(
                ProfitAnalysis.period_name,
                ProfitAnalysis.revenue,
                ProfitAnalysis.cost,
                ProfitAnalysis.profit,
                ProfitAnalysis.profit_rate,
            )
            .order_by(ProfitAnalysis.start_date)
            .limit(limit)
        )
        result = await db.execute(query)
        rows = result.all()

        return [
            {
                'name': row.period_name,
                'revenue': float(row.revenue or 0),
                'cost': float(row.cost or 0),
                'profit': float(row.profit or 0),
                'profit_rate': float(row.profit_rate or 0),
            }
            for row in rows
        ]

    @classmethod
    async def get_cost_structure_distribution(cls, db: AsyncSession) -> list[dict]:
        """
        获取成本结构分布
        """
        labor_cost = ((await db.execute(select(func.sum(ProfitAnalysis.labor_cost))))).scalar() or 0
        material_cost = ((await db.execute(select(func.sum(ProfitAnalysis.material_cost))))).scalar() or 0
        utility_cost = ((await db.execute(select(func.sum(ProfitAnalysis.utility_cost))))).scalar() or 0
        other_cost = ((await db.execute(select(func.sum(ProfitAnalysis.other_cost))))).scalar() or 0

        items = [
            {'name': '人工成本', 'value': float(labor_cost)},
            {'name': '食材成本', 'value': float(material_cost)},
            {'name': '水电成本', 'value': float(utility_cost)},
            {'name': '其他成本', 'value': float(other_cost)},
        ]
        total = sum(item['value'] for item in items)
        for item in items:
            item['percentage'] = round((item['value'] / total * 100) if total > 0 else 0, 2)
        return items

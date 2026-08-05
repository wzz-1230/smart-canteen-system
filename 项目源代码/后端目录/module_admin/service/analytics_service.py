from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from module_admin.dao.analytics_dao import AnalyticsDao
from module_admin.entity.vo.analytics_vo import (
    AnalyticsSummaryModel,
    InventoryPageQueryModel,
    ProfitPageQueryModel,
    RevenueExpensePageQueryModel,
)
from utils.common_util import CamelCaseUtil


class AnalyticsService:
    """
    数据分析模块服务层
    """

    # 数据转换工具方法
    @classmethod
    def _to_camel(cls, data: Any) -> Any:
        """将数据转换为驼峰命名"""
        if isinstance(data, dict):
            return {CamelCaseUtil.snake_to_camel(k): cls._to_camel(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls._to_camel(item) for item in data]
        elif hasattr(data, '__dict__') and not isinstance(data, (str, int, float, bool)):
            result = {}
            for k, v in vars(data).items():
                if not k.startswith('_'):
                    result[CamelCaseUtil.snake_to_camel(k)] = cls._to_camel(v)
            return result
        else:
            return data

    # -------------------- 库存服务 --------------------

    @classmethod
    async def get_inventory_list_services(
        cls, db: AsyncSession, query_object: InventoryPageQueryModel, is_page: bool = False
    ) -> Any:
        """获取库存记录列表"""
        query_result = await AnalyticsDao.get_inventory_list(db, query_object, is_page)
        if isinstance(query_result, list):
            return [cls._to_camel(row) for row in query_result]
        elif hasattr(query_result, 'rows'):
            query_result.rows = [cls._to_camel(row) for row in query_result.rows]
        return query_result

    @classmethod
    async def add_inventory_services(cls, db: AsyncSession, inventory_data: dict) -> CrudResponseModel:
        """新增库存记录"""
        inventory_data['create_time'] = datetime.now()
        inventory_data['update_time'] = datetime.now()
        await AnalyticsDao.add_inventory_dao(db, inventory_data)
        await db.commit()
        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_inventory_services(cls, db: AsyncSession, inventory_data: dict) -> CrudResponseModel:
        """编辑库存记录"""
        inventory_data['update_time'] = datetime.now()
        await AnalyticsDao.edit_inventory_dao(db, inventory_data)
        await db.commit()
        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_inventory_services(cls, db: AsyncSession, record_id: int) -> CrudResponseModel:
        """删除库存记录"""
        await AnalyticsDao.delete_inventory_dao(db, record_id)
        await db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    # -------------------- 收支服务 --------------------

    @classmethod
    async def get_revenue_expense_list_services(
        cls, db: AsyncSession, query_object: RevenueExpensePageQueryModel, is_page: bool = False
    ) -> Any:
        """获取收支明细列表"""
        query_result = await AnalyticsDao.get_revenue_expense_list(db, query_object, is_page)
        if isinstance(query_result, list):
            return [cls._to_camel(row) for row in query_result]
        elif hasattr(query_result, 'rows'):
            query_result.rows = [cls._to_camel(row) for row in query_result.rows]
        return query_result

    @classmethod
    async def add_revenue_expense_services(cls, db: AsyncSession, data: dict) -> CrudResponseModel:
        """新增收支明细"""
        data['create_time'] = datetime.now()
        data['update_time'] = datetime.now()
        await AnalyticsDao.add_revenue_expense_dao(db, data)
        await db.commit()
        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_revenue_expense_services(cls, db: AsyncSession, data: dict) -> CrudResponseModel:
        """编辑收支明细"""
        data['update_time'] = datetime.now()
        await AnalyticsDao.edit_revenue_expense_dao(db, data)
        await db.commit()
        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_revenue_expense_services(cls, db: AsyncSession, record_id: int) -> CrudResponseModel:
        """删除收支明细"""
        await AnalyticsDao.delete_revenue_expense_dao(db, record_id)
        await db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    # -------------------- 利润服务 --------------------

    @classmethod
    async def get_profit_list_services(
        cls, db: AsyncSession, query_object: ProfitPageQueryModel, is_page: bool = False
    ) -> Any:
        """获取利润分析列表"""
        query_result = await AnalyticsDao.get_profit_list(db, query_object, is_page)
        if isinstance(query_result, list):
            return [cls._to_camel(row) for row in query_result]
        elif hasattr(query_result, 'rows'):
            query_result.rows = [cls._to_camel(row) for row in query_result.rows]
        return query_result

    @classmethod
    async def add_profit_services(cls, db: AsyncSession, data: dict) -> CrudResponseModel:
        """新增利润分析"""
        data['create_time'] = datetime.now()
        await AnalyticsDao.add_profit_dao(db, data)
        await db.commit()
        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_profit_services(cls, db: AsyncSession, data: dict) -> CrudResponseModel:
        """编辑利润分析"""
        await AnalyticsDao.edit_profit_dao(db, data)
        await db.commit()
        return CrudResponseModel(is_success=True, message='修改成功')

    @classmethod
    async def delete_profit_services(cls, db: AsyncSession, record_id: int) -> CrudResponseModel:
        """删除利润分析"""
        await AnalyticsDao.delete_profit_dao(db, record_id)
        await db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    # -------------------- 汇总统计服务 --------------------

    @classmethod
    async def get_analytics_summary_services(cls, db: AsyncSession) -> AnalyticsSummaryModel:
        """获取综合数据分析汇总"""
        inventory_summary = await AnalyticsDao.get_inventory_summary(db)
        revenue_summary = await AnalyticsDao.get_revenue_expense_summary(db)
        profit_summary = await AnalyticsDao.get_profit_summary(db)

        summary = AnalyticsSummaryModel(
            total_revenue=max(float(revenue_summary.get('total_revenue', 0)), float(profit_summary.get('total_revenue', 0))),
            total_cost=max(float(revenue_summary.get('total_cost', 0)), float(profit_summary.get('total_cost', 0))),
            total_profit=max(float(revenue_summary.get('total_profit', 0)), float(profit_summary.get('total_profit', 0))),
            profit_rate=profit_summary.get('avg_profit_rate', 0),
            total_orders=profit_summary.get('total_orders', 0),
            total_items=inventory_summary.get('total_items', 0),
            low_stock_items=inventory_summary.get('low_stock_items', 0),
            avg_turnover_rate=inventory_summary.get('avg_turnover_rate', 0),
            avg_order_amount=profit_summary.get('avg_order_amount', 0),
        )
        return summary

    @classmethod
    async def get_inventory_turnover_trend_services(cls, db: AsyncSession) -> list[dict]:
        """获取库存周转趋势"""
        data = await AnalyticsDao.get_inventory_turnover_trend(db)
        return [cls._to_camel(item) for item in data]

    @classmethod
    async def get_inventory_type_distribution_services(cls, db: AsyncSession) -> list[dict]:
        """获取物品类型分布"""
        return await AnalyticsDao.get_inventory_type_distribution(db)

    @classmethod
    async def get_revenue_expense_trend_services(cls, db: AsyncSession) -> list[dict]:
        """获取收支趋势"""
        return await AnalyticsDao.get_revenue_expense_trend(db)

    @classmethod
    async def get_revenue_category_distribution_services(cls, db: AsyncSession) -> list[dict]:
        """获取收入分类分布"""
        return await AnalyticsDao.get_revenue_category_distribution(db)

    @classmethod
    async def get_expense_category_distribution_services(cls, db: AsyncSession) -> list[dict]:
        """获取支出分类分布"""
        return await AnalyticsDao.get_expense_category_distribution(db)

    @classmethod
    async def get_profit_trend_services(cls, db: AsyncSession) -> list[dict]:
        """获取利润趋势"""
        return await AnalyticsDao.get_profit_trend(db)

    @classmethod
    async def get_cost_structure_distribution_services(cls, db: AsyncSession) -> list[dict]:
        """获取成本结构分布"""
        return await AnalyticsDao.get_cost_structure_distribution(db)

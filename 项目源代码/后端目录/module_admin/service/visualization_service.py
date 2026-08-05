from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.dao.visualization_dao import VisualizationDao


class VisualizationService:
    """
    可视化模块服务层
    """

    # -------------------- 食堂销售 --------------------

    @classmethod
    async def get_canteen_sales_summary(cls, db: AsyncSession) -> dict[str, Any]:
        """获取食堂销售汇总信息"""
        summary = await VisualizationDao.get_canteen_summary(db)
        hot_dishes = await VisualizationDao.get_hot_dishes_top(db, top_n=5)
        daily_trend = await VisualizationDao.get_daily_trend(db, days=30)
        return {
            **summary,
            'hot_dishes': hot_dishes,
            'daily_trend': daily_trend,
        }

    @classmethod
    async def get_canteen_sales_daily_trend(cls, db: AsyncSession, days: int = 30) -> list[dict]:
        """获取日销售趋势"""
        return await VisualizationDao.get_daily_trend(db, days=days)

    @classmethod
    async def get_canteen_sales_dish_ranking(cls, db: AsyncSession, top_n: int = 20) -> list[dict]:
        """获取菜品销售排行"""
        return await VisualizationDao.get_dish_ranking(db, top_n=top_n)

    # -------------------- 日志监控 --------------------

    @classmethod
    async def get_log_analysis_summary(cls, db: AsyncSession) -> dict[str, Any]:
        """获取系统日志监控汇总"""
        summary = await VisualizationDao.get_log_summary(db)
        trend = await VisualizationDao.get_log_trend(db, days=7)
        return {
            **summary,
            'recent_trend': trend,
        }

    @classmethod
    async def get_log_analysis_trend(cls, db: AsyncSession, days: int = 7) -> list[dict]:
        """获取请求趋势数据"""
        return await VisualizationDao.get_log_trend(db, days=days)

    @classmethod
    async def get_log_analysis_type_distribution(cls, db: AsyncSession, top_n: int = 10) -> list[dict]:
        """获取请求类型分布"""
        return await VisualizationDao.get_log_type_distribution(db, top_n=top_n)

    # -------------------- 用户与部门 --------------------

    @classmethod
    async def get_user_analysis_summary(cls, db: AsyncSession) -> dict[str, Any]:
        """获取用户与部门分析汇总"""
        return await VisualizationDao.get_user_summary(db)

    @classmethod
    async def get_user_analysis_dept_distribution(cls, db: AsyncSession) -> list[dict]:
        """获取用户按部门分布"""
        return await VisualizationDao.get_user_by_dept(db)

    @classmethod
    async def get_user_analysis_status_distribution(cls, db: AsyncSession) -> list[dict]:
        """获取用户按状态分布"""
        return await VisualizationDao.get_user_by_status(db)

    # -------------------- 食堂销售（新增） --------------------

    @classmethod
    async def get_canteen_sales_hourly_distribution(cls, db: AsyncSession, days: int = 7) -> list[dict]:
        """获取食堂销售按小时分布"""
        return await VisualizationDao.get_canteen_hourly_distribution(db, days=days)

    # -------------------- 日志监控（新增） --------------------

    @classmethod
    async def get_log_analysis_login_stats(cls, db: AsyncSession, days: int = 7) -> list[dict]:
        """获取登录成功/失败统计"""
        return await VisualizationDao.get_log_login_stats(db, days=days)

    # -------------------- 用户与部门（新增） --------------------

    @classmethod
    async def get_user_analysis_register_trend(cls, db: AsyncSession, days: int = 30) -> list[dict]:
        """获取用户注册趋势"""
        return await VisualizationDao.get_user_register_trend(db, days=days)

    @classmethod
    async def get_user_analysis_role_distribution(cls, db: AsyncSession) -> list[dict]:
        """获取用户按角色分布"""
        return await VisualizationDao.get_user_by_role(db)

    # -------------------- 库存管理 --------------------

    @classmethod
    async def get_inventory_summary(cls, db: AsyncSession) -> dict:
        """获取库存汇总信息（总览 + 分类分布 + 状态分布 + TOP物品 + 低库存预警）"""
        summary = await VisualizationDao.get_inventory_summary(db)
        category_distribution = await VisualizationDao.get_inventory_category_distribution(db)
        status_distribution = await VisualizationDao.get_inventory_status_distribution(db)
        top_items = await VisualizationDao.get_inventory_top_items(db, top_n=10)
        low_stock_items = await VisualizationDao.get_inventory_low_stock(db)
        return {
            **summary,
            'category_distribution': category_distribution,
            'status_distribution': status_distribution,
            'top_items': top_items,
            'low_stock_items': low_stock_items,
        }

    @classmethod
    async def get_inventory_category(cls, db: AsyncSession) -> list[dict]:
        """获取库存分类分布"""
        return await VisualizationDao.get_inventory_category_distribution(db)

    @classmethod
    async def get_inventory_top_items(cls, db: AsyncSession, top_n: int = 10) -> list[dict]:
        """获取 TOP N 高价值库存"""
        return await VisualizationDao.get_inventory_top_items(db, top_n=top_n)

    # -------------------- 收支管理 --------------------

    @classmethod
    async def get_income_expense_summary(cls, db: AsyncSession) -> dict:
        """获取收支汇总（总览 + 分类分布 + 日趋势 + 支付方式 + TOP记录）"""
        summary = await VisualizationDao.get_income_expense_summary(db)
        category_distribution = await VisualizationDao.get_income_expense_category(db)
        daily_trend = await VisualizationDao.get_income_expense_daily_trend(db, days=30)
        payment_method_distribution = await VisualizationDao.get_income_expense_payment_method(db)
        top_records = await VisualizationDao.get_income_expense_top_records(db, top_n=10)
        return {
            **summary,
            'category_distribution': category_distribution,
            'daily_trend': daily_trend,
            'payment_method_distribution': payment_method_distribution,
            'top_records': top_records,
        }

    @classmethod
    async def get_income_expense_trend(cls, db: AsyncSession, days: int = 30) -> list[dict]:
        """获取收支日趋势"""
        return await VisualizationDao.get_income_expense_daily_trend(db, days=days)

    @classmethod
    async def get_income_expense_top_records(cls, db: AsyncSession, top_n: int = 10) -> list[dict]:
        """获取 TOP N 大额收支"""
        return await VisualizationDao.get_income_expense_top_records(db, top_n=top_n)

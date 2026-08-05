from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel
from module_admin.entity.vo.analytics_vo import (
    AnalyticsSummaryModel,
    InventoryPageQueryModel,
    ProfitPageQueryModel,
    RevenueExpensePageQueryModel,
)
from module_admin.service.analytics_service import AnalyticsService
from utils.response_util import ResponseUtil


analytics_controller = APIRouterPro(
    prefix='/analytics', order_num=14, tags=['数据分析-库存周转收支趋势利润分析'], dependencies=[]
)


# -------------------- 综合汇总接口 --------------------

@analytics_controller.get(
    '/summary',
    summary='获取数据分析汇总信息',
    description='获取库存、收支、利润综合汇总数据',
    response_model=DataResponseModel[AnalyticsSummaryModel],
)
async def get_analytics_summary(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    summary = await AnalyticsService.get_analytics_summary_services(query_db)
    return ResponseUtil.success(data=summary)


# -------------------- 库存相关接口 --------------------

@analytics_controller.get(
    '/inventory/list',
    summary='获取库存记录列表',
    description='分页查询库存记录',
    response_model=PageResponseModel,
)
async def get_inventory_list(
    request: Request,
    page_query: Annotated[InventoryPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AnalyticsService.get_inventory_list_services(query_db, page_query, is_page=True)
    return ResponseUtil.success(model_content=result)


@analytics_controller.get(
    '/inventory/turnover-trend',
    summary='获取库存周转趋势数据',
    description='获取库存周转率和价值趋势数据，用于图表展示',
    response_model=DataResponseModel,
)
async def get_inventory_turnover_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await AnalyticsService.get_inventory_turnover_trend_services(query_db)
    return ResponseUtil.success(data=data)


@analytics_controller.get(
    '/inventory/type-distribution',
    summary='获取物品类型分布',
    description='获取库存物品按类型分布的统计数据',
    response_model=DataResponseModel,
)
async def get_inventory_type_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await AnalyticsService.get_inventory_type_distribution_services(query_db)
    return ResponseUtil.success(data=data)


# -------------------- 收支相关接口 --------------------

@analytics_controller.get(
    '/revenue-expense/list',
    summary='获取收支明细列表',
    description='分页查询收支明细记录',
    response_model=PageResponseModel,
)
async def get_revenue_expense_list(
    request: Request,
    page_query: Annotated[RevenueExpensePageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AnalyticsService.get_revenue_expense_list_services(query_db, page_query, is_page=True)
    return ResponseUtil.success(model_content=result)


@analytics_controller.get(
    '/revenue-expense/trend',
    summary='获取收支趋势数据',
    description='获取按月份统计的收支和利润趋势数据',
    response_model=DataResponseModel,
)
async def get_revenue_expense_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await AnalyticsService.get_revenue_expense_trend_services(query_db)
    return ResponseUtil.success(data=data)


@analytics_controller.get(
    '/revenue-expense/revenue-distribution',
    summary='获取收入分类分布',
    description='获取按分类统计的收入分布数据（饼图/环形图）',
    response_model=DataResponseModel,
)
async def get_revenue_category_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await AnalyticsService.get_revenue_category_distribution_services(query_db)
    return ResponseUtil.success(data=data)


@analytics_controller.get(
    '/revenue-expense/expense-distribution',
    summary='获取支出分类分布',
    description='获取按分类统计的支出分布数据（饼图/环形图）',
    response_model=DataResponseModel,
)
async def get_expense_category_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await AnalyticsService.get_expense_category_distribution_services(query_db)
    return ResponseUtil.success(data=data)


# -------------------- 利润相关接口 --------------------

@analytics_controller.get(
    '/profit/list',
    summary='获取利润分析列表',
    description='分页查询利润分析记录',
    response_model=PageResponseModel,
)
async def get_profit_list(
    request: Request,
    page_query: Annotated[ProfitPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AnalyticsService.get_profit_list_services(query_db, page_query, is_page=True)
    return ResponseUtil.success(model_content=result)


@analytics_controller.get(
    '/profit/trend',
    summary='获取利润趋势数据',
    description='获取利润趋势数据，用于折线图展示',
    response_model=DataResponseModel,
)
async def get_profit_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await AnalyticsService.get_profit_trend_services(query_db)
    return ResponseUtil.success(data=data)


@analytics_controller.get(
    '/profit/cost-structure',
    summary='获取成本结构分布',
    description='获取成本结构分布数据（人工/食材/水电/其他）',
    response_model=DataResponseModel,
)
async def get_cost_structure_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await AnalyticsService.get_cost_structure_distribution_services(query_db)
    return ResponseUtil.success(data=data)

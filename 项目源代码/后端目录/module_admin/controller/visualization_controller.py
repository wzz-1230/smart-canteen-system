from typing import Annotated

from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_admin.service.visualization_service import VisualizationService
from utils.response_util import ResponseUtil


visualization_controller = APIRouterPro(
    prefix='/visualization', order_num=15, tags=['数据分析-可视化'], dependencies=[]
)


# -------------------- 食堂销售接口 --------------------


@visualization_controller.get(
    '/canteen-sales/summary',
    summary='食堂销售汇总',
    description='获取食堂销售汇总信息（总销售额、总订单数、客单价、会员数、热销菜品TOP5、近30天趋势）',
    response_model=DataResponseModel,
)
async def get_canteen_sales_summary(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_canteen_sales_summary(query_db)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/canteen-sales/daily-trend',
    summary='每日销售趋势',
    description='获取近30天每日销售额和订单数（双轴数据）',
    response_model=DataResponseModel,
)
async def get_canteen_sales_daily_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_canteen_sales_daily_trend(query_db, days=30)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/canteen-sales/dish-ranking',
    summary='菜品销售排行',
    description='获取各菜品销量与销售额排行',
    response_model=DataResponseModel,
)
async def get_canteen_sales_dish_ranking(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_canteen_sales_dish_ranking(query_db, top_n=20)
    return ResponseUtil.success(data=data)


# -------------------- 日志分析接口 --------------------


@visualization_controller.get(
    '/log-analysis/summary',
    summary='系统日志监控汇总',
    description='获取系统请求总数、成功数、失败数、平均响应时间、近7天趋势',
    response_model=DataResponseModel,
)
async def get_log_analysis_summary(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_log_analysis_summary(query_db)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/log-analysis/trend',
    summary='请求趋势数据',
    description='获取近7天按日统计的请求总量、成功数、失败数',
    response_model=DataResponseModel,
)
async def get_log_analysis_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_log_analysis_trend(query_db, days=7)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/log-analysis/type-distribution',
    summary='请求类型分布',
    description='获取按操作模块统计的请求数量（饼图数据）',
    response_model=DataResponseModel,
)
async def get_log_analysis_type_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_log_analysis_type_distribution(query_db, top_n=10)
    return ResponseUtil.success(data=data)


# -------------------- 用户与部门分析接口 --------------------


@visualization_controller.get(
    '/user-analysis/summary',
    summary='用户与部门分析汇总',
    description='获取总用户数、活跃用户数、部门数量',
    response_model=DataResponseModel,
)
async def get_user_analysis_summary(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_user_analysis_summary(query_db)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/user-analysis/dept-distribution',
    summary='用户按部门分布',
    description='获取各部门用户数量统计（饼图/柱状图数据）',
    response_model=DataResponseModel,
)
async def get_user_analysis_dept_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_user_analysis_dept_distribution(query_db)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/user-analysis/status-distribution',
    summary='用户状态分布',
    description='获取启用/停用用户数量统计',
    response_model=DataResponseModel,
)
async def get_user_analysis_status_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_user_analysis_status_distribution(query_db)
    return ResponseUtil.success(data=data)


# -------------------- 食堂销售（新增接口） --------------------


@visualization_controller.get(
    '/canteen-sales/hourly-distribution',
    summary='食堂销售时段分布',
    description='获取近 N 天内食堂按小时统计的销售额和订单数',
    response_model=DataResponseModel,
)
async def get_canteen_sales_hourly_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_canteen_sales_hourly_distribution(query_db, days=7)
    return ResponseUtil.success(data=data)


# -------------------- 日志分析（新增接口） --------------------


@visualization_controller.get(
    '/log-analysis/login-stats',
    summary='登录成功/失败统计',
    description='获取近 N 天内系统登录成功和失败次数的按日统计',
    response_model=DataResponseModel,
)
async def get_log_analysis_login_stats(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_log_analysis_login_stats(query_db, days=7)
    return ResponseUtil.success(data=data)


# -------------------- 用户与部门（新增接口） --------------------


@visualization_controller.get(
    '/user-analysis/register-trend',
    summary='用户注册趋势',
    description='获取近 N 天内用户新增注册数量的按日统计',
    response_model=DataResponseModel,
)
async def get_user_analysis_register_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_user_analysis_register_trend(query_db, days=30)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/user-analysis/role-distribution',
    summary='用户角色分布',
    description='获取各角色下的用户数量统计',
    response_model=DataResponseModel,
)
async def get_user_analysis_role_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_user_analysis_role_distribution(query_db)
    return ResponseUtil.success(data=data)


# -------------------- 库存管理接口 --------------------


@visualization_controller.get(
    '/inventory/summary',
    summary='库存汇总',
    description='获取库存汇总信息、分类分布、状态分布、TOP物品、低库存预警',
    response_model=DataResponseModel,
)
async def get_inventory_summary(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_inventory_summary(query_db)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/inventory/category',
    summary='库存分类分布',
    description='按分类统计库存',
    response_model=DataResponseModel,
)
async def get_inventory_category(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_inventory_category(query_db)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/inventory/top-items',
    summary='TOP库存物品',
    description='获取TOP N高价值库存物品',
    response_model=DataResponseModel,
)
async def get_inventory_top_items(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    top_n: int = 10,
) -> Response:
    data = await VisualizationService.get_inventory_top_items(query_db, top_n=top_n)
    return ResponseUtil.success(data=data)


# -------------------- 收支管理接口 --------------------


@visualization_controller.get(
    '/income-expense/summary',
    summary='收支汇总',
    description='获取收支汇总信息、分类分布、日趋势、支付方式、TOP记录',
    response_model=DataResponseModel,
)
async def get_income_expense_summary(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    data = await VisualizationService.get_income_expense_summary(query_db)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/income-expense/trend',
    summary='收支趋势',
    description='获取近N天每日收支趋势',
    response_model=DataResponseModel,
)
async def get_income_expense_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    days: int = 30,
) -> Response:
    data = await VisualizationService.get_income_expense_trend(query_db, days=days)
    return ResponseUtil.success(data=data)


@visualization_controller.get(
    '/income-expense/top-records',
    summary='TOP大额收支',
    description='获取TOP N大额收支记录',
    response_model=DataResponseModel,
)
async def get_income_expense_top_records(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    top_n: int = 10,
) -> Response:
    data = await VisualizationService.get_income_expense_top_records(query_db, top_n=top_n)
    return ResponseUtil.success(data=data)

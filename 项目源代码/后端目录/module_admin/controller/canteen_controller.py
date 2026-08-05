from typing import Annotated, Any

from fastapi import Body, Path, Query, Request, Response
from fastapi.responses import StreamingResponse
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, DynamicResponseModel, PageResponseModel
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
    OrderRecordModel,
    OrderRecordPageQueryModel,
)
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.canteen_service import CanteenService
from utils.log_util import logger
from utils.response_util import ResponseUtil


canteen_controller = APIRouterPro(
    prefix='/canteen', order_num=10, tags=['食堂管理'], dependencies=[PreAuthDependency()]
)


@canteen_controller.get(
    '/menu/list',
    summary='获取菜品列表接口',
    description='用于获取菜品分页列表',
    response_model=PageResponseModel[CanteenMenuModel],
    dependencies=[UserInterfaceAuthDependency(['system:canteen:menu:list', 'system:canteen:orderonline:list'])],
)
@Log(title='菜品管理', business_type=BusinessType.OTHER)
async def get_canteen_menu_list(
    request: Request,
    menu_page_query: Annotated[CanteenMenuPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    menu_page_query_result = await CanteenService.get_menu_list_services(
        query_db, menu_page_query, is_page=True
    )
    logger.info('获取菜品列表成功')

    return ResponseUtil.success(model_content=menu_page_query_result)


@canteen_controller.get(
    '/menu/{menu_id}',
    summary='获取菜品详情接口',
    description='用于获取菜品详情信息',
    response_model=DataResponseModel[CanteenMenuModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:menu:query')],
)
@Log(title='菜品管理', business_type=BusinessType.OTHER)
async def get_canteen_menu_detail(
    request: Request,
    menu_id: Annotated[int, Path(description='菜品ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    menu_detail_result = await CanteenService.get_menu_detail_services(query_db, menu_id)
    logger.info('获取菜品详情成功')

    return ResponseUtil.success(data=menu_detail_result)


@canteen_controller.post(
    '/menu',
    summary='新增菜品接口',
    description='用于新增菜品信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:menu:add')],
)
@ValidateFields(CanteenMenuModel)
@Log(title='菜品管理', business_type=BusinessType.INSERT)
async def add_canteen_menu(
    request: Request,
    menu: CanteenMenuModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_menu_result = await CanteenService.add_menu_services(query_db, menu)
    logger.info('新增菜品成功')

    return ResponseUtil.success(model_content=add_menu_result)


@canteen_controller.put(
    '/menu',
    summary='编辑菜品接口',
    description='用于编辑菜品信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:menu:edit')],
)
@ValidateFields(CanteenMenuModel)
@Log(title='菜品管理', business_type=BusinessType.UPDATE)
async def edit_canteen_menu(
    request: Request,
    menu: CanteenMenuModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_menu_result = await CanteenService.edit_menu_services(query_db, menu)
    logger.info('编辑菜品成功')

    return ResponseUtil.success(model_content=edit_menu_result)


@canteen_controller.delete(
    '/menu/{menu_id}',
    summary='删除菜品接口',
    description='用于删除菜品信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:menu:delete')],
)
@Log(title='菜品管理', business_type=BusinessType.DELETE)
async def delete_canteen_menu(
    request: Request,
    menu_id: Annotated[int, Path(description='菜品ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_menu_result = await CanteenService.delete_menu_services(
        query_db, CanteenMenuModel(menu_id=menu_id)
    )
    logger.info('删除菜品成功')

    return ResponseUtil.success(model_content=delete_menu_result)


@canteen_controller.get(
    '/order/list',
    summary='获取订单列表接口',
    description='用于获取订单分页列表',
    response_model=PageResponseModel[OrderRecordModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:order:list')],
)
@Log(title='订单管理', business_type=BusinessType.OTHER)
async def get_canteen_order_list(
    request: Request,
    order_page_query: Annotated[OrderRecordPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    order_page_query_result = await CanteenService.get_order_list_services(
        query_db, order_page_query, is_page=True
    )
    logger.info('获取订单列表成功')

    return ResponseUtil.success(model_content=order_page_query_result)


@canteen_controller.get(
    '/order/{order_id}',
    summary='获取订单详情接口',
    description='用于获取订单详情信息',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('system:canteen:order:query')],
)
@Log(title='订单管理', business_type=BusinessType.OTHER)
async def get_canteen_order_detail(
    request: Request,
    order_id: Annotated[int, Path(description='订单ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    order_detail_result = await CanteenService.get_order_detail_services(query_db, order_id)
    logger.info('获取订单详情成功')

    return ResponseUtil.success(data=order_detail_result)


@canteen_controller.post(
    '/order',
    summary='新增订单接口',
    description='用于新增订单信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency(['system:canteen:order:add', 'system:canteen:orderonline:list'])],
)
@ValidateFields(OrderCreateModel)
@Log(title='订单管理', business_type=BusinessType.INSERT)
async def add_canteen_order(
    request: Request,
    order: OrderCreateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_order_result = await CanteenService.add_order_services(query_db, order)
    logger.info('新增订单成功')

    return ResponseUtil.success(model_content=add_order_result)


@canteen_controller.put(
    '/order',
    summary='编辑订单接口',
    description='用于编辑订单信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:order:edit')],
)
@ValidateFields(OrderRecordModel)
@Log(title='订单管理', business_type=BusinessType.UPDATE)
async def edit_canteen_order(
    request: Request,
    order: OrderRecordModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_order_result = await CanteenService.edit_order_services(query_db, order)
    logger.info('编辑订单成功')

    return ResponseUtil.success(model_content=edit_order_result)


@canteen_controller.delete(
    '/order/{order_id}',
    summary='删除订单接口',
    description='用于删除订单信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:order:delete')],
)
@Log(title='订单管理', business_type=BusinessType.DELETE)
async def delete_canteen_order(
    request: Request,
    order_id: Annotated[int, Path(description='订单ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_order_result = await CanteenService.delete_order_services(
        query_db, OrderRecordModel(order_id=order_id)
    )
    logger.info('删除订单成功')

    return ResponseUtil.success(model_content=delete_order_result)


@canteen_controller.get(
    '/table/list',
    summary='获取餐桌列表接口',
    description='用于获取餐桌分页列表',
    response_model=PageResponseModel[DiningTableModel],
    dependencies=[UserInterfaceAuthDependency(['system:canteen:table:list', 'system:canteen:orderonline:list'])],
)
@Log(title='餐桌管理', business_type=BusinessType.OTHER)
async def get_canteen_table_list(
    request: Request,
    table_page_query: Annotated[DiningTablePageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    table_page_query_result = await CanteenService.get_table_list_services(
        query_db, table_page_query, is_page=True
    )
    logger.info('获取餐桌列表成功')

    return ResponseUtil.success(model_content=table_page_query_result)


@canteen_controller.get(
    '/table/{table_id}',
    summary='获取餐桌详情接口',
    description='用于获取餐桌详情信息',
    response_model=DataResponseModel[DiningTableModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:table:query')],
)
@Log(title='餐桌管理', business_type=BusinessType.OTHER)
async def get_canteen_table_detail(
    request: Request,
    table_id: Annotated[int, Path(description='餐桌ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    table_detail_result = await CanteenService.get_table_detail_services(query_db, table_id)
    logger.info('获取餐桌详情成功')

    return ResponseUtil.success(data=table_detail_result)


@canteen_controller.post(
    '/table',
    summary='新增餐桌接口',
    description='用于新增餐桌信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:table:add')],
)
@ValidateFields(DiningTableModel)
@Log(title='餐桌管理', business_type=BusinessType.INSERT)
async def add_canteen_table(
    request: Request,
    table: DiningTableModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_table_result = await CanteenService.add_table_services(query_db, table)
    logger.info('新增餐桌成功')

    return ResponseUtil.success(model_content=add_table_result)


@canteen_controller.put(
    '/table',
    summary='编辑餐桌接口',
    description='用于编辑餐桌信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:table:edit')],
)
@ValidateFields(DiningTableModel)
@Log(title='餐桌管理', business_type=BusinessType.UPDATE)
async def edit_canteen_table(
    request: Request,
    table: DiningTableModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_table_result = await CanteenService.edit_table_services(query_db, table)
    logger.info('编辑餐桌成功')

    return ResponseUtil.success(model_content=edit_table_result)


@canteen_controller.delete(
    '/table/{table_id}',
    summary='删除餐桌接口',
    description='用于删除餐桌信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:table:delete')],
)
@Log(title='餐桌管理', business_type=BusinessType.DELETE)
async def delete_canteen_table(
    request: Request,
    table_id: Annotated[int, Path(description='餐桌ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_table_result = await CanteenService.delete_table_services(
        query_db, DiningTableModel(table_id=table_id)
    )
    logger.info('删除餐桌成功')

    return ResponseUtil.success(model_content=delete_table_result)


@canteen_controller.put(
    '/table/{table_id}/status/{status}',
    summary='更新餐桌状态接口',
    description='用于更新餐桌状态',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:table:edit')],
)
@Log(title='餐桌管理', business_type=BusinessType.UPDATE)
async def update_canteen_table_status(
    request: Request,
    table_id: Annotated[int, Path(description='餐桌ID')],
    status: Annotated[str, Path(description='状态')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    update_status_result = await CanteenService.update_table_status_services(query_db, table_id, status)
    logger.info('更新餐桌状态成功')

    return ResponseUtil.success(model_content=update_status_result)


@canteen_controller.post(
    '/ai/chat',
    summary='食堂 AI 对话接口',
    description='基于数据库实时信息，回答用户关于菜品、订单、餐桌的问题',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:ai:chat')],
)
@Log(title='食堂 AI 对话', business_type=BusinessType.OTHER)
async def canteen_ai_chat(
    request: Request,
    payload: Annotated[dict, Body()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    from module_admin.service.canteen_chat_service import chat as canteen_chat

    question = str((payload or {}).get('question') or '')
    user_id: int | None = None
    try:
        user_obj = getattr(current_user, 'user', None)
        if user_obj is not None:
            uid = getattr(user_obj, 'user_id', None)
            if uid is not None:
                user_id = int(uid)
    except Exception:
        user_id = None
    logger.info(f'用户提问食堂 AI: {question} (user_id={user_id})')
    answer = await canteen_chat(query_db, question, user_id=user_id)

    return ResponseUtil.success(dict_content={'reply': answer, 'question': question})


@canteen_controller.get(
    '/staff/list',
    summary='获取员工列表接口',
    description='用于获取员工分页列表',
    response_model=PageResponseModel[CanteenStaffModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:staff:list')],
)
@Log(title='员工管理', business_type=BusinessType.OTHER)
async def get_canteen_staff_list(
    request: Request,
    staff_page_query: Annotated[CanteenStaffPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    staff_page_query_result = await CanteenService.get_staff_list_services(
        query_db, staff_page_query, is_page=True
    )
    logger.info('获取员工列表成功')
    return ResponseUtil.success(model_content=staff_page_query_result)


@canteen_controller.get(
    '/staff/{staff_id}',
    summary='获取员工详情接口',
    description='用于获取员工详情信息',
    response_model=DataResponseModel[CanteenStaffModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:staff:query')],
)
@Log(title='员工管理', business_type=BusinessType.OTHER)
async def get_canteen_staff_detail(
    request: Request,
    staff_id: Annotated[int, Path(description='员工ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    staff_detail_result = await CanteenService.get_staff_detail_services(query_db, staff_id)
    logger.info('获取员工详情成功')
    return ResponseUtil.success(data=staff_detail_result)


@canteen_controller.post(
    '/staff',
    summary='新增员工接口',
    description='用于新增员工信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:staff:add')],
)
@ValidateFields(CanteenStaffModel)
@Log(title='员工管理', business_type=BusinessType.INSERT)
async def add_canteen_staff(
    request: Request,
    staff: CanteenStaffModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_staff_result = await CanteenService.add_staff_services(query_db, staff)
    logger.info('新增员工成功')
    return ResponseUtil.success(model_content=add_staff_result)


@canteen_controller.put(
    '/staff',
    summary='编辑员工接口',
    description='用于编辑员工信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:staff:edit')],
)
@ValidateFields(CanteenStaffModel)
@Log(title='员工管理', business_type=BusinessType.UPDATE)
async def edit_canteen_staff(
    request: Request,
    staff: CanteenStaffModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_staff_result = await CanteenService.edit_staff_services(query_db, staff)
    logger.info('编辑员工成功')
    return ResponseUtil.success(model_content=edit_staff_result)


@canteen_controller.delete(
    '/staff/{staff_id}',
    summary='删除员工接口',
    description='用于删除员工信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:staff:delete')],
)
@Log(title='员工管理', business_type=BusinessType.DELETE)
async def delete_canteen_staff(
    request: Request,
    staff_id: Annotated[int, Path(description='员工ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_staff_result = await CanteenService.delete_staff_services(
        query_db, CanteenStaffModel(staff_id=staff_id)
    )
    logger.info('删除员工成功')
    return ResponseUtil.success(model_content=delete_staff_result)


@canteen_controller.get(
    '/user/list',
    summary='获取用户列表接口',
    description='用于获取用户分页列表',
    response_model=PageResponseModel[CanteenUserModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:user:list')],
)
@Log(title='用户管理', business_type=BusinessType.OTHER)
async def get_canteen_user_list(
    request: Request,
    user_page_query: Annotated[CanteenUserPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    user_page_query_result = await CanteenService.get_user_list_services(
        query_db, user_page_query, is_page=True
    )
    logger.info('获取用户列表成功')
    return ResponseUtil.success(model_content=user_page_query_result)


@canteen_controller.get(
    '/user/{user_id}',
    summary='获取用户详情接口',
    description='用于获取用户详情信息',
    response_model=DataResponseModel[CanteenUserModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:user:query')],
)
@Log(title='用户管理', business_type=BusinessType.OTHER)
async def get_canteen_user_detail(
    request: Request,
    user_id: Annotated[int, Path(description='用户ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    user_detail_result = await CanteenService.get_user_detail_services(query_db, user_id)
    logger.info('获取用户详情成功')
    return ResponseUtil.success(data=user_detail_result)


@canteen_controller.post(
    '/user',
    summary='新增用户接口',
    description='用于新增用户信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:user:add')],
)
@ValidateFields(CanteenUserModel)
@Log(title='用户管理', business_type=BusinessType.INSERT)
async def add_canteen_user(
    request: Request,
    user: CanteenUserModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_user_result = await CanteenService.add_user_services(query_db, user)
    logger.info('新增用户成功')
    return ResponseUtil.success(model_content=add_user_result)


@canteen_controller.put(
    '/user',
    summary='编辑用户接口',
    description='用于编辑用户信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:user:edit')],
)
@ValidateFields(CanteenUserModel)
@Log(title='用户管理', business_type=BusinessType.UPDATE)
async def edit_canteen_user(
    request: Request,
    user: CanteenUserModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_user_result = await CanteenService.edit_user_services(query_db, user)
    logger.info('编辑用户成功')
    return ResponseUtil.success(model_content=edit_user_result)


@canteen_controller.delete(
    '/user/{user_id}',
    summary='删除用户接口',
    description='用于删除用户信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:user:delete')],
)
@Log(title='用户管理', business_type=BusinessType.DELETE)
async def delete_canteen_user(
    request: Request,
    user_id: Annotated[int, Path(description='用户ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_user_result = await CanteenService.delete_user_services(
        query_db, CanteenUserModel(user_id=user_id)
    )
    logger.info('删除用户成功')
    return ResponseUtil.success(model_content=delete_user_result)


@canteen_controller.put(
    '/user/reset-password',
    summary='重置用户密码接口',
    description='用于重置用户密码',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:user:edit')],
)
@Log(title='用户管理', business_type=BusinessType.UPDATE)
async def reset_canteen_user_password(
    request: Request,
    pwd_object: CanteenUserResetPwdModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    reset_pwd_result = await CanteenService.reset_user_password_services(query_db, pwd_object)
    logger.info('重置用户密码成功')
    return ResponseUtil.success(model_content=reset_pwd_result)


@canteen_controller.get(
    '/inventory/list',
    summary='获取库存列表接口',
    description='用于获取库存分页列表',
    response_model=PageResponseModel[CanteenInventoryModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:inventory:list')],
)
@Log(title='库存管理', business_type=BusinessType.OTHER)
async def get_canteen_inventory_list(
    request: Request,
    inventory_page_query: Annotated[CanteenInventoryPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    inventory_page_query_result = await CanteenService.get_inventory_list_services(
        query_db, inventory_page_query, is_page=True
    )
    logger.info('获取库存列表成功')
    return ResponseUtil.success(model_content=inventory_page_query_result)


@canteen_controller.get(
    '/inventory/{record_id}',
    summary='获取库存详情接口',
    description='用于获取库存详情信息',
    response_model=DataResponseModel[CanteenInventoryModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:inventory:query')],
)
@Log(title='库存管理', business_type=BusinessType.OTHER)
async def get_canteen_inventory_detail(
    request: Request,
    record_id: Annotated[int, Path(description='记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    inventory_detail_result = await CanteenService.get_inventory_detail_services(query_db, record_id)
    logger.info('获取库存详情成功')
    return ResponseUtil.success(data=inventory_detail_result)


@canteen_controller.post(
    '/inventory',
    summary='新增库存接口',
    description='用于新增库存信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:inventory:add')],
)
@ValidateFields(CanteenInventoryModel)
@Log(title='库存管理', business_type=BusinessType.INSERT)
async def add_canteen_inventory(
    request: Request,
    inventory: CanteenInventoryModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_inventory_result = await CanteenService.add_inventory_services(query_db, inventory)
    logger.info('新增库存成功')
    return ResponseUtil.success(model_content=add_inventory_result)


@canteen_controller.put(
    '/inventory',
    summary='编辑库存接口',
    description='用于编辑库存信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:inventory:edit')],
)
@ValidateFields(CanteenInventoryModel)
@Log(title='库存管理', business_type=BusinessType.UPDATE)
async def edit_canteen_inventory(
    request: Request,
    inventory: CanteenInventoryModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_inventory_result = await CanteenService.edit_inventory_services(query_db, inventory)
    logger.info('编辑库存成功')
    return ResponseUtil.success(model_content=edit_inventory_result)


@canteen_controller.delete(
    '/inventory/{record_id}',
    summary='删除库存接口',
    description='用于删除库存信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:inventory:delete')],
)
@Log(title='库存管理', business_type=BusinessType.DELETE)
async def delete_canteen_inventory(
    request: Request,
    record_id: Annotated[int, Path(description='记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_inventory_result = await CanteenService.delete_inventory_services(
        query_db, CanteenInventoryModel(record_id=record_id)
    )
    logger.info('删除库存成功')
    return ResponseUtil.success(model_content=delete_inventory_result)


@canteen_controller.get(
    '/profit/list',
    summary='获取利润记录列表接口',
    description='用于获取利润记录分页列表',
    response_model=PageResponseModel[CanteenProfitModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:profit:list')],
)
@Log(title='利润管理', business_type=BusinessType.OTHER)
async def get_canteen_profit_list(
    request: Request,
    profit_page_query: Annotated[CanteenProfitPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    profit_page_query_result = await CanteenService.get_profit_list_services(
        query_db, profit_page_query, is_page=True
    )
    logger.info('获取利润记录列表成功')
    return ResponseUtil.success(model_content=profit_page_query_result)


@canteen_controller.get(
    '/profit/{record_id}',
    summary='获取利润记录详情接口',
    description='用于获取利润记录详情信息',
    response_model=DataResponseModel[CanteenProfitModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:profit:query')],
)
@Log(title='利润管理', business_type=BusinessType.OTHER)
async def get_canteen_profit_detail(
    request: Request,
    record_id: Annotated[int, Path(description='记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    profit_detail_result = await CanteenService.get_profit_detail_services(query_db, record_id)
    logger.info('获取利润记录详情成功')
    return ResponseUtil.success(data=profit_detail_result)


@canteen_controller.post(
    '/profit',
    summary='新增利润记录接口',
    description='用于新增利润记录信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:profit:add')],
)
@ValidateFields(CanteenProfitModel)
@Log(title='利润管理', business_type=BusinessType.INSERT)
async def add_canteen_profit(
    request: Request,
    profit: CanteenProfitModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_profit_result = await CanteenService.add_profit_services(query_db, profit)
    logger.info('新增利润记录成功')
    return ResponseUtil.success(model_content=add_profit_result)


@canteen_controller.put(
    '/profit',
    summary='编辑利润记录接口',
    description='用于编辑利润记录信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:profit:edit')],
)
@ValidateFields(CanteenProfitModel)
@Log(title='利润管理', business_type=BusinessType.UPDATE)
async def edit_canteen_profit(
    request: Request,
    profit: CanteenProfitModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_profit_result = await CanteenService.edit_profit_services(query_db, profit)
    logger.info('编辑利润记录成功')
    return ResponseUtil.success(model_content=edit_profit_result)


@canteen_controller.delete(
    '/profit/{record_id}',
    summary='删除利润记录接口',
    description='用于删除利润记录信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:profit:delete')],
)
@Log(title='利润管理', business_type=BusinessType.DELETE)
async def delete_canteen_profit(
    request: Request,
    record_id: Annotated[int, Path(description='记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_profit_result = await CanteenService.delete_profit_services(
        query_db, CanteenProfitModel(record_id=record_id)
    )
    logger.info('删除利润记录成功')
    return ResponseUtil.success(model_content=delete_profit_result)


# ===== 智能体 (Agent) 相关接口 =====

@canteen_controller.post(
    '/agent/chat',
    summary='食堂智能体对话接口',
    description='基于扣子智能体（Coze Bot）+ 数据库实时知识库，回答菜品、订单、餐桌的问题，支持流式响应',
    response_class=StreamingResponse,
)
@Log(title='食堂智能体对话', business_type=BusinessType.OTHER)
async def canteen_agent_chat(
    request: Request,
    payload: Annotated[dict, Body()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    食堂智能体对话接口。优先使用扣子智能体（Coze Bot）进行流式对话。
    如果未配置扣子 API Key 或 Bot ID，则回退到本地模拟。
    """
    from module_admin.service.coze_service import CozeService
    from module_admin.service.canteen_knowledge_service import CanteenKnowledgeService

    message = str((payload or {}).get('message') or '')
    user_id: int | None = None
    try:
        user_obj = getattr(current_user, 'user', None)
        if user_obj is not None:
            uid = getattr(user_obj, 'user_id', None)
            if uid is not None:
                user_id = int(uid)
    except Exception:
        user_id = None

    logger.info(f'[扣子智能体] 用户提问: {message} (user_id={user_id})')

    # 判断是否配置了扣子 API
    coze_configured = bool(CozeService._get_api_key()) and bool(CozeService._get_bot_id())
    logger.info(f'[扣子智能体] 扣子配置状态: {coze_configured}')

    async def _stream_coze_reply():
        """异步生成器：调用扣子智能体流式回复，带智能去重和后处理"""
        try:
            # 从数据库获取知识库内容，注入到系统提示词
            knowledge_base: list[str] = []
            try:
                menu_data = await CanteenKnowledgeService.get_menu_knowledge(query_db)
                knowledge_base.extend(menu_data)
                logger.info(f'[扣子智能体] 知识库加载成功: {len(menu_data)} 条菜品信息')
            except Exception as e:
                logger.warning(f'[扣子智能体] 知识库加载失败: {e}')

            # 调用扣子智能体，收集所有内容
            all_chunks: list[str] = []
            async for chunk in CozeService.chat_with_coze(
                user_id=user_id if user_id else 1,
                message=message,
                conversation_id=None,
                bot_name='canteen',
                knowledge_base=knowledge_base,
                stream=True,
            ):
                all_chunks.append(chunk)

            # 合并所有内容
            full_text = ''.join(all_chunks)

            # ===== 0. 清理HTML属性代码（确保输出纯文本，无class/loading/onerror等属性）=====
            import re as _html_re
            full_text = _html_re.sub(r'\s+(?:class|id|style|loading|onerror|onload|onclick|onmouseover)\s*=\s*"[^"]*"', '', full_text)
            full_text = _html_re.sub(r"\s+(?:class|id|style|loading|onerror|onload|onclick|onmouseover)\s*=\s*'[^']*'", '', full_text)
            full_text = _html_re.sub(r'\s*/>', '', full_text)

            # ===== 智能后处理：去重和清理 =====
            # 1. 按段落分割（双换行）
            paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]

            # 2. 去重：检测重复段落
            seen_paragraphs = set()
            unique_paragraphs = []
            for para in paragraphs:
                # 简化比较：去除空白和标点后比较
                normalized = ''.join(para.split())
                if len(normalized) > 20 and normalized in seen_paragraphs:
                    # 重复的大段落，跳过
                    logger.info(f'[扣子智能体] 检测到重复段落，已去除: {para[:50]}...')
                    continue
                if len(normalized) > 20:
                    seen_paragraphs.add(normalized)
                unique_paragraphs.append(para)

            # 3. 重新组合
            processed_text = '\n\n'.join(unique_paragraphs)

            # 4. 清理多余的符号（如末尾重复的问题、多余的感叹号等）
            # 检测末尾是否有类似用户问题的内容（扣子有时会额外输出问题）
            # 简单策略：如果末尾段落包含"？"且长度<30，且不是正常回答的一部分，去除
            lines = processed_text.split('\n')
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                # 去除明显的多余符号行
                if not stripped:
                    cleaned_lines.append(line)
                    continue
                # 如果整行只有标点符号，去除
                if all(c in '，。！？、,.!?' for c in stripped):
                    continue
                cleaned_lines.append(line)
            
            final_text = '\n'.join(cleaned_lines).strip()

            # ===== 流式输出处理后的内容 =====
            # 按字符分批输出，模拟打字效果
            chunk_size = 3
            for i in range(0, len(final_text), chunk_size):
                yield final_text[i:i+chunk_size]

            if not final_text:
                yield '\n（智能体未返回有效内容，请稍后重试）'

            logger.info(f'[扣子智能体] 回复生成完成: {len(final_text)} 字符，原始 {len(full_text)} 字符')

        except Exception as e:
            logger.error(f'[扣子智能体] 对话异常: {e}')
            import traceback
            logger.error(traceback.format_exc())
            yield f'⚠️ 智能体服务异常: {str(e)}'

    return StreamingResponse(
        _stream_coze_reply(),
        media_type='text/plain; charset=utf-8',
    )


@canteen_controller.post(
    '/agent/knowledge',
    summary='获取食堂知识库',
    description='根据查询类型返回对应的知识库内容',
    response_model=DynamicResponseModel,
)
@Log(title='食堂知识库查询', business_type=BusinessType.OTHER)
async def canteen_agent_knowledge(
    request: Request,
    payload: Annotated[dict, Body()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取食堂知识库内容。
    queryType: all, menu, inventory, finance, order, staff, table, recent
    """
    from module_admin.service.canteen_knowledge_service import CanteenKnowledgeService

    query_type = str((payload or {}).get('queryType') or 'all')
    logger.info(f'获取食堂知识库: {query_type}')

    try:
        knowledge_lines: list[str] = []

        if query_type == 'menu' or query_type == 'all':
            menu_data = await CanteenKnowledgeService.get_menu_knowledge(query_db)
            knowledge_lines.extend(menu_data)

        if query_type == 'inventory' or query_type == 'all':
            inventory_data = await CanteenKnowledgeService.get_inventory_knowledge(query_db)
            knowledge_lines.extend(inventory_data)

        if query_type == 'finance' or query_type == 'all':
            finance_data = await CanteenKnowledgeService.get_finance_knowledge(query_db)
            knowledge_lines.extend(finance_data)

        if query_type == 'order' or query_type == 'all':
            order_data = await CanteenKnowledgeService.get_order_knowledge(query_db)
            knowledge_lines.extend(order_data)

        if query_type == 'staff' or query_type == 'all':
            staff_data = await CanteenKnowledgeService.get_staff_knowledge(query_db)
            knowledge_lines.extend(staff_data)

        if query_type == 'table' or query_type == 'all':
            table_data = await CanteenKnowledgeService.get_table_knowledge(query_db)
            knowledge_lines.extend(table_data)

        if query_type == 'recent':
            recent_data = await CanteenKnowledgeService.get_recent_data_knowledge(query_db)
            knowledge_lines.extend(recent_data)

        content = '\n'.join(knowledge_lines)
        return ResponseUtil.success(dict_content={'content': content, 'queryType': query_type})
    except Exception as e:
        logger.warning(f'获取知识库失败: {e}')
        return ResponseUtil.success(dict_content={'content': f'知识库加载失败: {str(e)}', 'queryType': query_type})


@canteen_controller.get(
    '/agent/config',
    summary='获取智能体配置',
    description='返回当前智能体的配置信息（如模式、图片前缀等）',
    response_model=DynamicResponseModel,
)
async def canteen_agent_config(
    request: Request,
) -> Response:
    """
    返回智能体配置信息。
    - mode: coze 或 local（取决于是否配置了扣子 API Key 和 Bot ID）
    - image_prefix: 图片URL前缀
    - has_coze: 是否配置了扣子智能体
    """
    from module_admin.service.coze_service import CozeService

    has_coze = bool(CozeService._get_api_key()) and bool(CozeService._get_bot_id())
    mode = 'coze' if has_coze else 'local'

    config = {
        'mode': mode,
        'has_coze': has_coze,
        'has_llm': has_coze,
        'image_prefix': '/static/canteen-menu-images/',
        'description': '食堂智能助手 - 基于扣子智能体和数据库知识库',
    }
    return ResponseUtil.success(dict_content=config)


@canteen_controller.get(
    '/revenue-expense/list',
    summary='获取收支记录列表接口',
    description='用于获取收支记录分页列表',
    response_model=PageResponseModel[CanteenRevenueExpenseModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:revenue:list')],
)
@Log(title='收支管理', business_type=BusinessType.OTHER)
async def get_canteen_revenue_expense_list(
    request: Request,
    revenue_expense_page_query: Annotated[CanteenRevenueExpensePageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    revenue_expense_page_query_result = await CanteenService.get_revenue_expense_list_services(
        query_db, revenue_expense_page_query, is_page=True
    )
    logger.info('获取收支记录列表成功')
    return ResponseUtil.success(model_content=revenue_expense_page_query_result)


@canteen_controller.get(
    '/revenue-expense/{record_id}',
    summary='获取收支记录详情接口',
    description='用于获取收支记录详情信息',
    response_model=DataResponseModel[CanteenRevenueExpenseModel],
    dependencies=[UserInterfaceAuthDependency('system:canteen:revenue:query')],
)
@Log(title='收支管理', business_type=BusinessType.OTHER)
async def get_canteen_revenue_expense_detail(
    request: Request,
    record_id: Annotated[int, Path(description='记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    revenue_expense_detail_result = await CanteenService.get_revenue_expense_detail_services(query_db, record_id)
    logger.info('获取收支记录详情成功')
    return ResponseUtil.success(data=revenue_expense_detail_result)


@canteen_controller.post(
    '/revenue-expense',
    summary='新增收支记录接口',
    description='用于新增收支记录信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:revenue:add')],
)
@ValidateFields(CanteenRevenueExpenseModel)
@Log(title='收支管理', business_type=BusinessType.INSERT)
async def add_canteen_revenue_expense(
    request: Request,
    revenue_expense: CanteenRevenueExpenseModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_revenue_expense_result = await CanteenService.add_revenue_expense_services(query_db, revenue_expense)
    logger.info('新增收支记录成功')
    return ResponseUtil.success(model_content=add_revenue_expense_result)


@canteen_controller.put(
    '/revenue-expense',
    summary='编辑收支记录接口',
    description='用于编辑收支记录信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:revenue:edit')],
)
@ValidateFields(CanteenRevenueExpenseModel)
@Log(title='收支管理', business_type=BusinessType.UPDATE)
async def edit_canteen_revenue_expense(
    request: Request,
    revenue_expense: CanteenRevenueExpenseModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_revenue_expense_result = await CanteenService.edit_revenue_expense_services(query_db, revenue_expense)
    logger.info('编辑收支记录成功')
    return ResponseUtil.success(model_content=edit_revenue_expense_result)


@canteen_controller.delete(
    '/revenue-expense/{record_id}',
    summary='删除收支记录接口',
    description='用于删除收支记录信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:canteen:revenue:delete')],
)
@Log(title='收支管理', business_type=BusinessType.DELETE)
async def delete_canteen_revenue_expense(
    request: Request,
    record_id: Annotated[int, Path(description='记录ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_revenue_expense_result = await CanteenService.delete_revenue_expense_services(
        query_db, CanteenRevenueExpenseModel(record_id=record_id)
    )
    logger.info('删除收支记录成功')
    return ResponseUtil.success(model_content=delete_revenue_expense_result)
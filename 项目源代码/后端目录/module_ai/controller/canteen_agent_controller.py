"""
扣子智能体对话控制器
提供食堂智能体的API接口
"""
from typing import Annotated, Optional

from fastapi import Body, Depends, Request, Response
from fastapi.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.annotation.rate_limit_annotation import ApiRateLimit, ApiRateLimitPreset
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency
from common.constant import ApiNamespace
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.coze_service import CozeService
from module_admin.service.canteen_knowledge_service import CanteenKnowledgeService
from utils.log_util import logger
from utils.response_util import ResponseUtil

canteen_agent_controller = APIRouterPro(
    prefix='/canteen/agent',
    order_num=20,
    tags=['AI管理-食堂智能体'],
    dependencies=[],  # 不强制登录，由业务逻辑判断
)


@canteen_agent_controller.post(
    '/chat',
    summary='食堂智能体对话',
    description='调用扣子智能体或本地模拟，基于食堂知识库进行对话',
    response_class=StreamingResponse,
)
@ApiRateLimit(namespace=ApiNamespace.AI_CHAT_SEND, preset=ApiRateLimitPreset.USER_INTERACTIVE_HIGH_FREQ)
async def canteen_agent_chat(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[Optional[CurrentUserModel], CurrentUserDependency()],
    message: Annotated[str, Body(embed=True, description='用户消息', min_length=1, max_length=1000)],
    conversation_id: Annotated[Optional[str], Body(embed=True, description='会话ID')] = None,
    use_knowledge: Annotated[bool, Body(embed=True, description='是否使用知识库')] = True,
) -> StreamingResponse:
    """
    食堂智能体对话接口

    - **message**: 用户的问题或消息
    - **conversation_id**: 会话ID，用于连续对话
    - **use_knowledge**: 是否附加知识库内容
    """
    # 获取用户ID（未登录用户使用guest）
    user_id = current_user.user.user_id if current_user and current_user.user else 0
    user_name = current_user.user.user_name if current_user and current_user.user else '访客'

    logger.info(f'用户{user_name}({user_id})调用食堂智能体: {message[:50]}...')

    # 获取知识库内容
    knowledge_base = []
    if use_knowledge:
        try:
            knowledge_base = await CanteenKnowledgeService.analyze_query_and_get_knowledge(query_db, message)
            logger.info(f'获取知识库内容: {len(knowledge_base)} 条')
        except Exception as e:
            logger.error(f'获取知识库失败: {e}')

    # 调用智能体
    chat_stream = CozeService.chat_with_coze(
        user_id=user_id,
        message=message,
        conversation_id=conversation_id,
        bot_name='canteen',
        knowledge_base=knowledge_base,
        stream=True,
    )

    return StreamingResponse(content=chat_stream, media_type='text/event-stream')


@canteen_agent_controller.post(
    '/knowledge',
    summary='获取食堂知识库',
    description='获取食堂数据库中的知识库内容',
    response_model=DataResponseModel[dict],
)
async def get_canteen_knowledge(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    query_type: Annotated[str, Body(embed=True, description='查询类型: all/menu/inventory/finance/order/staff/table')] = 'all',
) -> Response:
    """
    获取食堂知识库内容

    - **query_type**: 查询类型，可选:
        - all: 所有知识库（默认）
        - menu: 菜单信息
        - inventory: 库存信息
        - finance: 财务收支
        - order: 订单销售
        - staff: 员工信息
        - table: 餐桌信息
    """
    try:
        knowledge = await CanteenKnowledgeService.generate_knowledge_base(query_db, query_type)
        result = {
            'type': query_type,
            'count': len(knowledge),
            'content': '\n'.join(knowledge),
            'list': knowledge
        }
        logger.info(f'获取{query_type}知识库成功，共{len(knowledge)}条')
        return ResponseUtil.success(data=result)
    except Exception as e:
        logger.error(f'获取知识库失败: {e}')
        return ResponseUtil.success(data={'error': str(e)})


@canteen_agent_controller.get(
    '/config',
    summary='获取智能体配置',
    description='获取扣子智能体的配置信息',
    response_model=DataResponseModel[dict],
)
async def get_agent_config(request: Request) -> Response:
    """获取智能体配置状态"""
    from config.env import AppConfig
    import os

    api_key = getattr(AppConfig, 'coze_api_key', None) or os.environ.get('COZE_API_KEY', '')
    bot_id = getattr(AppConfig, 'coze_canteen_bot_id', None) or os.environ.get('COZE_CANTEEN_BOT_ID', '')

    config = {
        'has_api_key': bool(api_key),
        'has_bot_id': bool(bot_id),
        'api_key_preview': api_key[:8] + '...' if len(api_key) > 8 else '',
        'bot_id_preview': bot_id[:8] + '...' if len(bot_id) > 8 else '',
        'mode': 'coze' if (api_key and bot_id) else 'local',
        'description': {
            'coze': '已配置扣子智能体，将使用扣子平台进行智能对话',
            'local': '未配置扣子智能体，当前使用本地模拟对话（支持基础问答）'
        }.get('coze' if (api_key and bot_id) else 'local', '本地模式')
    }

    logger.info(f'智能体配置查询: 模式={config["mode"]}')
    return ResponseUtil.success(data=config)


@canteen_agent_controller.post(
    '/quick-analyze',
    summary='快速智能分析',
    description='基于知识库快速生成分析报告',
    response_model=DataResponseModel[dict],
)
async def quick_analyze(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    query_type: Annotated[str, Body(embed=True, description='分析类型')] = 'overview',
) -> Response:
    """
    快速智能分析（非流式）

    - **query_type**: 分析类型: overview, menu_analysis, inventory_status, finance_summary
    """
    try:
        # 获取基础知识库
        knowledge = await CanteenKnowledgeService.generate_knowledge_base(query_db, 'all')

        # 根据类型生成分析
        analysis = []
        if query_type == 'overview':
            analysis = knowledge
        elif query_type == 'menu_analysis':
            analysis = await CanteenKnowledgeService.get_menu_knowledge(query_db)
        elif query_type == 'inventory_status':
            analysis = await CanteenKnowledgeService.get_inventory_knowledge(query_db)
        elif query_type == 'finance_summary':
            analysis = await CanteenKnowledgeService.get_finance_knowledge(query_db)
        else:
            analysis = knowledge

        result = {
            'type': query_type,
            'analysis': analysis,
            'summary': '\n'.join(analysis[:50])
        }
        return ResponseUtil.success(data=result)

    except Exception as e:
        logger.error(f'快速分析失败: {e}')
        return ResponseUtil.error(msg=f'分析失败: {str(e)}')

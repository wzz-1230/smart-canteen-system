from typing import Annotated, Any

from fastapi import Body, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_admin.service.ai_service import AiService
from utils.log_util import logger
from utils.response_util import ResponseUtil


ai_controller = APIRouterPro(prefix='/ai', order_num=20, tags=['AI管理-DeepSeek对话'], dependencies=[])


class ChatMessageModel(BaseModel):
    role: str = Field('user', description='角色：system/user/assistant')
    content: str = Field('', description='消息内容')


class ChatRequestModel(BaseModel):
    messages: list[ChatMessageModel] = Field(..., description='消息列表')
    model: str | None = Field(None, description='模型名称')
    temperature: float = Field(0.7, ge=0.0, le=2.0, description='采样温度')
    max_tokens: int = Field(2048, gt=0, description='最大生成长度')
    stream: bool = Field(True, description='是否流式返回')


class AnalyzeRequestModel(BaseModel):
    model_config = ConfigDict(extra='allow')

    dataType: str | None = Field(None, description='数据类型，如 user-dept-distribution、log-analysis-trend 等')
    dataSummary: dict | str = Field({}, description='数据摘要内容，支持结构化对象或字符串')
    userQuestion: str = Field('', description='分析提示词/问题描述')
    analysis_request: str | None = Field(None, description='自定义分析要求（兼容旧格式）')
    data_summary: str = Field('', description='数据摘要内容（兼容旧格式）')
    model: str | None = Field(None, description='模型名称')
    temperature: float = Field(0.5, ge=0.0, le=2.0, description='采样温度')


@ai_controller.post(
    '/chat',
    summary='DeepSeek 对话接口',
    description='调用 DeepSeek 大模型进行对话，支持流式返回',
    response_class=StreamingResponse,
    responses={
        200: {
            'description': '对话返回结果',
            'content': {
                'text/plain': {},
                'text/event-stream': {},
            },
        }
    },
)
async def chat(
    request: Request,
    payload: Annotated[ChatRequestModel, Body(...)],
) -> Response:
    messages = [m.model_dump() for m in payload.messages]

    logger.info('调用 DeepSeek 对话接口')

    if payload.stream:
        async def _stream_wrapper() -> Any:
            async for chunk in AiService.chat_services(
                messages=messages,
                model=payload.model,
                temperature=payload.temperature,
                max_tokens=payload.max_tokens,
                stream=True,
            ):
                yield chunk

        return StreamingResponse(_stream_wrapper(), media_type='text/plain; charset=utf-8')

    result = await AiService.chat_services(
        messages=messages,
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        stream=False,
    )
    return ResponseUtil.success(data=result)


@ai_controller.post(
    '/analyze',
    summary='AI 数据分析接口',
    description='根据数据摘要调用大模型进行分析，用于可视化页面的 AI 分析',
    response_model=DataResponseModel,
)
async def analyze(
    request: Request,
    payload: Annotated[AnalyzeRequestModel, Body(...)],
) -> Response:
    import json

    logger.info(f'调用 DeepSeek 数据分析接口，数据类型: {payload.dataType}')

    # 兼容处理：优先使用新格式 (dataSummary + userQuestion)
    # 回退到旧格式 (data_summary + analysis_request)
    if payload.dataSummary:
        if isinstance(payload.dataSummary, dict):
            # 结构化数据：转换为 JSON 字符串便于 AI 模型阅读
            data_summary_str = json.dumps(payload.dataSummary, ensure_ascii=False, indent=2)
        else:
            data_summary_str = str(payload.dataSummary)
    else:
        data_summary_str = payload.data_summary

    analysis_request = payload.userQuestion if payload.userQuestion else payload.analysis_request

    result = await AiService.analyze_services(
        data_summary=data_summary_str,
        analysis_request=analysis_request,
        data_type=payload.dataType,
        model=payload.model,
        temperature=payload.temperature,
    )
    return ResponseUtil.success(data=result)


@ai_controller.get(
    '/models',
    summary='获取支持的模型列表',
    description='返回支持的 DeepSeek 模型列表',
    response_model=DataResponseModel,
)
async def get_models(request: Request) -> Response:
    return ResponseUtil.success(data={'models': AiService.SUPPORTED_MODELS})

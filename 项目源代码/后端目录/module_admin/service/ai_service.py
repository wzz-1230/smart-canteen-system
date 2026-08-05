import json
from typing import Any, AsyncGenerator

import httpx


class AiService:
    """
    DeepSeek 大模型服务层（通过 硅基流动 SiliconFlow API 调用）
    """

    API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
    API_KEY = 'sk-rhqyaqvntmrzpxnjdxnwftlxxlgkyrdonsqtpzxlvkmvajau'
    DEFAULT_MODEL = 'deepseek-ai/DeepSeek-V3.2'
    SUPPORTED_MODELS = [
        'deepseek-ai/DeepSeek-V3',
        'deepseek-ai/DeepSeek-V3.1-Terminus',
        'deepseek-ai/DeepSeek-V3.2',
        'deepseek-ai/DeepSeek-R1',
        'Qwen/Qwen2.5-72B-Instruct',
        'Qwen/QwQ-32B',
    ]

    @classmethod
    def _get_headers(cls) -> dict:
        """构造请求头"""
        return {
            'Authorization': f'Bearer {cls.API_KEY}',
            'Content-Type': 'application/json',
        }

    @classmethod
    def chat_services(
        cls,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        stream: bool = True,
    ) -> Any:
        """
        调用 DeepSeek 对话接口

        :param messages: 消息列表，格式如 [{"role": "user", "content": "你好"}]
        :param model: 模型名称
        :param temperature: 采样温度
        :param max_tokens: 最大生成长度
        :param top_p: nucleus sampling
        :param stream: 是否流式返回
        :return: 流式响应（若 stream=True 返回 async generator 字符串块
        """
        selected_model = model if model in cls.SUPPORTED_MODELS else cls.DEFAULT_MODEL

        payload = {
            'model': selected_model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'top_p': top_p,
            'stream': stream,
        }

        if stream:
            return cls._stream_request(payload)
        return cls._sync_request(payload)

    @classmethod
    async def _stream_request(cls, payload: dict) -> AsyncGenerator[str, None]:
        """
        流式请求调用（SSE 风格），按块产出 content
        """
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                'POST',
                cls.API_URL,
                headers=cls._get_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    line = line.strip()
                    if line.startswith('data:'):
                        data_str = line[5:].strip()
                        if data_str == '[DONE]':
                            break
                        try:
                            data_obj = json.loads(data_str)
                            delta = data_obj.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content
                        except Exception:
                            continue

    @classmethod
    async def _sync_request(cls, payload: dict) -> dict:
        """非流式请求，返回完整 JSON"""
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                cls.API_URL,
                headers=cls._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return {'content': content, 'raw': data}

    @classmethod
    async def analyze_services(
        cls,
        data_summary: str,
        analysis_request: str | None = None,
        data_type: str | None = None,
        model: str | None = None,
        temperature: float = 0.5,
    ) -> dict:
        """
        调用大模型进行数据分析（用于可视化页面的 AI 分析）

        :param data_summary: 数据摘要内容（JSON 字符串或纯文本）
        :param analysis_request: 自定义分析要求/提示词
        :param data_type: 数据类型标识，用于定制分析角色
        :param model: 模型名称
        :param temperature: 采样温度
        :return: 分析结果（文本）
        """
        selected_model = model if model in cls.SUPPORTED_MODELS else cls.DEFAULT_MODEL

        # 根据 data_type 设置不同的系统角色和提示词
        type_roles = {
            # 食堂销售相关
            'canteen-sales-trend': '餐饮行业资深数据分析师，擅长食堂销售趋势分析、销售预测、客流管理',
            'canteen-dish-ranking': '餐饮行业资深数据分析师，擅长菜品销售分析、菜单优化、定价策略、利润分析',
            'canteen-hourly-distribution': '餐饮行业资深数据分析师，擅长时段销售分析、排班优化、时段营销策略',
            'canteen-sales-overall': '餐饮行业资深数据分析师，擅长食堂销售综合分析、菜品优化、时段管理、运营策略',
            # 系统日志相关
            'log-analysis-trend': '系统运维分析师，擅长请求趋势分析、系统性能评估、异常检测',
            'log-type-distribution': '系统运维和安全分析师，擅长操作类型分析、系统资源优化、接口性能分析',
            'log-login-stats': '系统安全分析师，擅长登录安全分析、暴力破解检测、用户行为分析、风险评估',
            'log-analysis-overall': '资深系统运维和安全分析师，擅长日志综合分析、性能优化、安全风险评估',
            # 用户与部门相关
            'user-dept-distribution': '组织管理和人力资源分析师，擅长部门结构分析、人员配置优化、组织架构设计',
            'user-register-trend': '用户增长分析师，擅长用户增长趋势分析、获客策略、用户留存优化',
            'user-role-distribution': '权限管理和安全审计师，擅长角色权限分析、最小权限原则落实、安全风险评估',
            'user-analysis-overall': '资深组织管理和人力资源分析师，擅长用户与部门综合分析、组织架构优化、权限管理策略',
            # 库存管理相关
            'inventory-category': '资深库存管理和供应链分析师，擅长库存分类分析、库存结构优化、采购策略建议',
            'inventory-top-items': '资深库存管理和供应链分析师，擅长高价值物品分析、库存成本优化、重要物资管理',
            'inventory-low-stock': '资深库存管理和供应链分析师，擅长低库存预警、补货策略、缺货风险评估',
            'inventory-overall': '资深库存管理和供应链分析师，擅长库存综合分析、库存优化策略、成本控制建议',
            'inventory-summary': '资深库存管理和供应链分析师，擅长库存汇总分析、库存健康度评估、优化建议',
            # 收支管理相关
            'income-expense-trend': '资深财务和经营分析师，擅长收支趋势分析、现金流预测、经营状况评估',
            'income-expense-category': '资深财务和经营分析师，擅长收支分类分析、成本结构优化、利润分析',
            'income-expense-top-records': '资深财务和经营分析师，擅长大额收支分析、风险识别、审计建议',
            'income-expense-overall': '资深财务和经营分析师，擅长收支综合分析、经营状况评估、财务管理建议',
            'income-expense-summary': '资深财务和经营分析师，擅长收支汇总分析、财务健康度评估、经营优化建议',
        }

        default_role = (
            '专业的数据分析师。请根据提供的数据进行深入分析，'
            '找出关键洞察、趋势变化、异常数据，并给出合理的业务建议。'
        )

        system_role = type_roles.get(data_type, default_role)
        system_prompt = (
            f'你是一位{system_role}。'
            '请根据提供的真实业务数据进行深入分析。'
            '分析时请：1) 基于实际数据得出结论，不做无依据推测；'
            '2) 识别关键洞察、趋势变化、异常数据；'
            '3) 给出具体、可执行的业务建议；'
            '4) 回答条理清晰、数据准确、结论明确。'
        )

        # 构建用户消息内容：包含数据摘要和分析要求
        data_desc = (
            f'【待分析数据】\n'
            f'数据类型：{data_type or "未指定"}\n\n'
            f'【数据内容】\n{data_summary}\n\n'
            f'【分析要求】\n{analysis_request or "请对以上数据进行全面分析，给出关键洞察和优化建议"}'
        )

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': data_desc},
        ]

        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f'AI分析请求 - data_type: {data_type}, '
            f'data_summary长度: {len(data_summary)} 字符, '
            f'analysis_request长度: {len(analysis_request or "")} 字符'
        )

        payload = {
            'model': selected_model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': 4096,
            'stream': False,
        }

        result = await cls._sync_request(payload)
        content = result.get('content', '')
        logger.info(f'AI分析完成，返回内容长度: {len(content)} 字符')

        return {
            'content': content,
            'analysis': content,  # 兼容前端的不同字段名
            'data_type': data_type,
            'model': selected_model,
        }

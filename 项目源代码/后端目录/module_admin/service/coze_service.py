"""
扣子(Coze)智能体服务
用于调用扣子平台的智能体，实现食堂知识库问答
"""
import json
import time
import asyncio
import httpx
from typing import AsyncGenerator, List, Dict, Optional

from common.constant import ApiNamespace
from config.env import AppConfig
from utils.log_util import logger


class CozeService:
    """扣子智能体服务
    
    使用方式：
    1. 配置扣子 API Key（必须）
    2. 在扣子平台创建一个简单的智能体（Bot），获取 Bot ID（必须）
    3. 系统会将数据库中的知识库内容注入对话
    4. 大模型会基于知识库内容生成专业回答
    """

    # 扣子API配置
    COZE_API_BASE = "https://api.coze.cn"
    COZE_CHAT_API = f"{COZE_API_BASE}/v3/chat"

    # 智能体配置
    DEFAULT_COZE_BOTS = {
        "canteen": {
            "name": "食堂智能助手",
            "description": "基于食堂知识库，解答菜品、库存、收支等问题",
            "bot_id": "",
        }
    }

    @classmethod
    def _get_api_key(cls) -> str:
        """获取扣子API Key"""
        api_key = getattr(AppConfig, 'coze_api_key', None)
        if not api_key:
            import os
            api_key = os.environ.get('COZE_API_KEY', '')
        return api_key

    @classmethod
    def _get_bot_id(cls, bot_name: str = "canteen") -> str:
        """获取智能体Bot ID"""
        bot_id = getattr(AppConfig, f'coze_{bot_name}_bot_id', None)
        if not bot_id:
            import os
            bot_id = os.environ.get(f'COZE_{bot_name.upper()}_BOT_ID', '')
        return bot_id

    @classmethod
    def _build_system_prompt(cls, knowledge_base: Optional[List[str]]) -> str:
        """构建系统提示词，引导大模型基于知识库回答"""
        prompt_parts = [
            "你是一个专业的食堂智能助手。基于知识库回答用户问题。",
            "",
            "【核心规则 - 必须严格遵守：",
            "1. 只基于知识库回答，不要编造数据",
            "2. 回复简洁，避免冗长",
            "3. 菜品信息附带图片，格式严格为：![菜品名](http://localhost:9099/static/canteen-menu-images/菜名.png)",
            "4. 绝对不要输出任何HTML代码！不要输出<img>标签！不要输出class、style、onerror等HTML属性！",
            "5. 图片必须使用标准Markdown格式：![图片描述](图片URL)",
            "6. 列表不要重复相同内容",
            "7. 不输出多余符号",
            "8. 用户问推荐，推荐3-5道相关即可",
            "9. 只输出纯文本和Markdown图片，不要输出任何HTML标签或属性！",
            "",
            "【知识库内容：",
        ]
        
        if knowledge_base:
            # 只取前25条内容，避免知识库过长
            limited_kb = knowledge_base[:25]
            prompt_parts.extend(limited_kb)
            if len(knowledge_base) > 25:
                prompt_parts.append(f"\n... 还有更多菜品数据（共 {len(knowledge_base)} 项）")
        else:
            prompt_parts.append("（暂无知识库数据）")
        
        prompt_parts.append("\n请基于以上知识库简洁回答用户问题。")
        
        return "\n".join(prompt_parts)

    @classmethod
    async def chat_with_coze(
        cls,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None,
        bot_name: str = "canteen",
        knowledge_base: Optional[List[str]] = None,
        stream: bool = True,
    ) -> AsyncGenerator[str, None]:
        """
        调用扣子智能体进行对话（只使用扣子平台，不降级到本地模拟）

        Args:
            user_id: 用户ID
            message: 用户消息
            conversation_id: 会话ID，用于连续对话
            bot_name: 智能体名称
            knowledge_base: 附加知识库内容
            stream: 是否流式返回

        Yields:
            回复内容片段
        """
        api_key = cls._get_api_key()
        bot_id = cls._get_bot_id(bot_name)

        # 验证配置
        if not api_key:
            yield "⚠️ 未配置扣子API Key，请在 .env.dev 文件中配置"
            return

        if not bot_id:
            yield f"⚠️ 未配置 {bot_name} 智能体的 Bot ID，请在 .env.dev 文件中配置 coze_{bot_name}_bot_id"
            return

        logger.info(f"调用扣子智能体: bot_id={bot_id}, message_length={len(message)}")

        # 构建请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # 构建系统提示词 + 用户问题
        system_prompt = cls._build_system_prompt(knowledge_base)
        final_message = f"{system_prompt}\n\n用户问题：{message}"

        payload = {
            "bot_id": bot_id,
            "user_id": f"user_{user_id}",
            "stream": stream,
            "auto_save_history": True,
            "additional_messages": [
                {
                    "role": "user",
                    "content": final_message,
                    "content_type": "text",
                }
            ],
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        try:
            timeout = httpx.Timeout(120.0, connect=30.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    cls.COZE_CHAT_API,
                    headers=headers,
                    json=payload,
                ) as response:
                    # 检查HTTP状态码
                    if response.status_code != 200:
                        error_content = await response.aread()
                        logger.error(f"扣子API调用失败: status={response.status_code}, error={error_content}")

                        if response.status_code == 401:
                            yield "⚠️ 扣子API Key无效或已过期，请重新配置"
                        elif response.status_code == 403:
                            yield "⚠️ 没有权限访问扣子智能体，请检查智能体配置"
                        elif response.status_code == 404:
                            yield "⚠️ Bot ID不正确，请检查扣子智能体的 Bot ID"
                        else:
                            yield f"⚠️ 智能体调用失败（状态码: {response.status_code}）"
                        return

                    # 处理流式响应 - 智能区分流式(delta)和完整(completed)内容
                    full_response = ""         # 累积的已输出内容
                    current_event = ""
                    buffer = ""
                    message_seen = set()       # 已处理的消息ID去重
                    delta_output_count = 0    # delta事件已输出的内容块数（用于判断是否已有流式内容）
                    delta_content_total = 0   # delta事件累计输出的字符数

                    import re as _re

                    def _clean_html_attrs(text: str) -> str:
                        """清理内容中的HTML标签和属性代码 - 确保输出纯文本和Markdown图片"""
                        if not text:
                            return text
                        cleaned = text

                        # 0. 清理扣子平台内部系统标记（如 {"msg_type":"...", "data":"..."}）
                        # 这些标记不应出现在给用户的回复中
                        cleaned = _re.sub(r'\{"msg_type"[^}]*\}', '', cleaned)
                        cleaned = _re.sub(r'\["msg_type"[^}\]]*\}', '', cleaned)
                        cleaned = _re.sub(r'"from_module"[^,}]*', '', cleaned)
                        cleaned = _re.sub(r'"from_unit"[^,}]*', '', cleaned)

                        # 1. 检测并转换完整的<img>标签为Markdown格式
                        # 匹配: <img src="URL" alt="描述" .../> 或 <img src='URL' .../>
                        def _img_to_markdown(match: _re.Match) -> str:
                            img_tag = match.group(0)
                            # 提取src属性
                            src_match = _re.search(r'src\s*=\s*["\']([^"\']+)["\']', img_tag)
                            # 提取alt属性
                            alt_match = _re.search(r'alt\s*=\s*["\']([^"\']*)["\']', img_tag)
                            src = src_match.group(1) if src_match else ''
                            alt = alt_match.group(1) if alt_match else '图片'
                            if src:
                                return f'![{alt}]({src})'
                            return ''

                        # 替换所有<img>标签
                        cleaned = _re.sub(r'<img\b[^>]*>', _img_to_markdown, cleaned, flags=_re.IGNORECASE)
                        cleaned = _re.sub(r'<img\b[^>]*/>', _img_to_markdown, cleaned, flags=_re.IGNORECASE)

                        # 2. 移除其他所有HTML标签（如<div>、<span>、<br>等）
                        cleaned = _re.sub(r'<[^>]+>', '', cleaned)

                        # 3. 移除独立的HTML属性片段（如 ' class="ai-image" loading="lazy"'）
                        # 这些可能是<img>标签被截断后残留的属性
                        cleaned = _re.sub(r'\s+(?:class|id|style|loading|onerror|onload|onclick|onmouseover|onmouseout|src|alt|title|width|height|border)\s*=\s*"[^"]*"', '', cleaned)
                        cleaned = _re.sub(r"\s+(?:class|id|style|loading|onerror|onload|onclick|onmouseover|onmouseout|src|alt|title|width|height|border)\s*=\s*'[^']*'", '', cleaned)

                        # 4. 移除孤立的结束标签碎片
                        cleaned = _re.sub(r'\s*/>', '', cleaned)
                        cleaned = _re.sub(r'\s*/$', '', cleaned)

                        # 5. 清理多余的空行（连续两个以上换行）
                        cleaned = _re.sub(r'\n{3,}', '\n\n', cleaned)

                        return cleaned

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        # 解析事件类型
                        if line.startswith("event:"):
                            current_event = line[6:].strip()
                        elif line.startswith("data:"):
                            data_str = line[5:].strip()

                            # 处理可能的多行JSON（累积）
                            buffer += data_str

                            try:
                                data = json.loads(buffer)
                                buffer = ""  # 成功解析后清空缓冲

                                # ===== 事件内容提取 =====
                                content = None
                                msg_id = None

                                # --- 情况1: conversation.message.delta (流式增量内容) ---
                                if current_event == "conversation.message.delta":
                                    if isinstance(data, dict) and "content" in data and isinstance(data["content"], str):
                                        content = data["content"]
                                        if content and content.strip():
                                            delta_output_count += 1
                                            delta_content_total += len(content)
                                            # 清理HTML属性后输出
                                            cleaned_content = _clean_html_attrs(content)
                                            if cleaned_content and cleaned_content.strip():
                                                full_response += cleaned_content
                                                yield cleaned_content
                                            continue  # delta事件处理完毕，直接继续

                                # --- 情况2: conversation.message.completed (完整消息) ---
                                elif current_event == "conversation.message.completed":
                                    # completed事件可能有两种情况：
                                    # a) messages数组 - 包含完整回答
                                    # b) content字段 - 完整消息内容
                                    temp_content = None

                                    if isinstance(data, dict) and "messages" in data and isinstance(data["messages"], list):
                                        for msg in data["messages"]:
                                            if isinstance(msg, dict) and msg.get("content"):
                                                msg_role = msg.get("role", "")
                                                msg_type = msg.get("type", "")
                                                mid = msg.get("id", "") or msg.get("msg_id", "")
                                                if msg_role in ["assistant", "answer"] or msg_type in ["answer", "text"]:
                                                    if mid and mid in message_seen:
                                                        continue
                                                    temp_content = msg["content"]
                                                    if mid:
                                                        message_seen.add(mid)
                                                    break

                                    elif isinstance(data, dict) and "content" in data and isinstance(data["content"], str):
                                        mid = data.get("id", "") or data.get("msg_id", "")
                                        if mid and mid in message_seen:
                                            continue
                                        temp_content = data["content"]
                                        if mid:
                                            message_seen.add(mid)

                                    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
                                        data_obj = data["data"]
                                        if "content" in data_obj and isinstance(data_obj["content"], str):
                                            mid = data_obj.get("id", "") or data_obj.get("msg_id", "")
                                            if mid and mid in message_seen:
                                                continue
                                            temp_content = data_obj["content"]
                                            if mid:
                                                message_seen.add(mid)

                                    # 如果从completed事件提取到了内容
                                    if temp_content and isinstance(temp_content, str):
                                        cleaned_temp = temp_content.strip()

                                        # ===== 智能去重检查 =====
                                        # 如果delta事件已经输出了大量内容（>100字符），并且与completed内容高度重叠，就跳过
                                        if delta_content_total >= 100 and cleaned_temp:
                                            # 计算内容重叠度 - 检查completed内容的前100字符是否出现在已输出内容中
                                            overlap_check_len = min(len(cleaned_temp), 100)
                                            temp_prefix = cleaned_temp[:overlap_check_len]
                                            # 去除空白字符后比较
                                            temp_norm = ''.join(temp_prefix.split())
                                            full_norm = ''.join(full_response.split())

                                            # 如果completed内容的开头部分已出现在已输出内容中，说明是重复内容
                                            if temp_norm and len(full_norm) > 50 and temp_norm in full_norm:
                                                logger.info(f"[扣子智能体] 智能去重：completed内容与delta流式内容重复，跳过")
                                                continue

                                            # 另一种检查：内容开头是否与已输出内容开头相同
                                            full_start = ''.join(full_response[:overlap_check_len].split())
                                            if temp_norm and full_start and temp_norm == full_start:
                                                logger.info(f"[扣子智能体] 智能去重：completed内容开头与delta内容开头相同，跳过")
                                                continue

                                        # ===== 后续问题建议过滤 =====
                                        is_follow_up = False
                                        # 特征1: 短文本(<80字符)且是问句
                                        if len(cleaned_temp) <= 80 and cleaned_temp.endswith(("?", "？", "!", "！")):
                                            question_keywords = ["吗", "哪", "什么", "是否", "推荐", "怎么", "如何", "有哪些", "在哪里", "多少钱"]
                                            if any(kw in cleaned_temp for kw in question_keywords):
                                                if not ("¥" in cleaned_temp or "元" in cleaned_temp or "：" in cleaned_temp or ":" in cleaned_temp):
                                                    is_follow_up = True
                                                    logger.info(f"[扣子智能体] 过滤后续问题建议(问句): {cleaned_temp[:60]}")

                                        # 特征2: 短文本(<80字符)且包含典型后续问题关键词
                                        if not is_follow_up and len(cleaned_temp) <= 80:
                                            follow_up_prefixes = [
                                                "推荐", "有哪些", "什么是", "如何", "怎么",
                                                "在哪", "哪里", "哪些", "有没有", "请问",
                                                "能不", "能推荐", "介绍", "说说", "聊聊"
                                            ]
                                            for prefix in follow_up_prefixes:
                                                if prefix in cleaned_temp:
                                                    if not ("¥" in cleaned_temp or "元" in cleaned_temp or "：" in cleaned_temp or ":" in cleaned_temp):
                                                        is_follow_up = True
                                                        logger.info(f"[扣子智能体] 过滤后续问题建议(短语): {cleaned_temp[:60]}")
                                                        break

                                        # 特征3: 包含特定标记
                                        if not is_follow_up and ("msg_type" in cleaned_temp or "from_module" in cleaned_temp):
                                            is_follow_up = True

                                        # 特征4: 内容看起来像独立的问句
                                        if not is_follow_up and len(cleaned_temp) <= 100:
                                            question_words = ["吗", "呢", "哪", "什么", "是否", "怎么", "如何", "谁", "？", "?"]
                                            qw_count = sum(1 for qw in question_words if qw in cleaned_temp)
                                            if qw_count >= 1 and not ("¥" in cleaned_temp or "元" in cleaned_temp or "上架" in cleaned_temp):
                                                is_follow_up = True
                                                logger.info(f"[扣子智能体] 过滤后续问题建议(疑问词): {cleaned_temp[:60]}")

                                        if is_follow_up:
                                            continue

                                        # ===== 最终输出 =====
                                        # 如果delta事件输出很少或没有内容，就输出completed事件的内容
                                        # （这种情况发生在扣子没有使用delta流式输出时）
                                        if delta_content_total < 100:
                                            # 清理HTML属性后输出
                                            cleaned_final = _clean_html_attrs(temp_content)
                                            if cleaned_final and cleaned_final.strip():
                                                full_response += cleaned_final
                                                yield cleaned_final
                                                logger.info(f"[扣子智能体] 输出completed事件内容: {len(cleaned_final)}字符")
                                        else:
                                            # 已有delta流式内容，检查是否有补充价值
                                            logger.info(f"[扣子智能体] 已通过delta流式输出{delta_content_total}字符，跳过completed内容以避免重复")
                                            continue

                                # --- 情况3: 其他事件格式（兼容模式）---
                                else:
                                    # 兼容旧版本处理逻辑
                                    if isinstance(data, dict) and "messages" in data and isinstance(data["messages"], list):
                                        for msg in data["messages"]:
                                            if isinstance(msg, dict) and msg.get("content"):
                                                msg_role = msg.get("role", "")
                                                if msg_role in ["assistant", "answer"]:
                                                    content = msg["content"]
                                                    break
                                    elif isinstance(data, dict) and "content" in data and isinstance(data["content"], str):
                                        content = data["content"]

                                    if content and isinstance(content, str) and content.strip():
                                        # 清理HTML属性
                                        cleaned_content = _clean_html_attrs(content.strip())

                                        if not cleaned_content or not cleaned_content.strip():
                                            continue

                                        # 后续问题建议过滤
                                        is_follow_up = False
                                        if len(cleaned_content) <= 80 and cleaned_content.endswith(("?", "？", "!", "！")):
                                            question_keywords = ["吗", "哪", "什么", "是否", "推荐", "怎么", "如何", "有哪些"]
                                            if any(kw in cleaned_content for kw in question_keywords):
                                                if not ("¥" in cleaned_content or "元" in cleaned_content):
                                                    is_follow_up = True
                                                    logger.info(f"[扣子智能体] 过滤后续问题建议: {cleaned_content[:60]}")

                                        if not is_follow_up and len(cleaned_content) <= 80:
                                            follow_up_prefixes = ["推荐", "有哪些", "什么是", "如何", "怎么"]
                                            for prefix in follow_up_prefixes:
                                                if prefix in cleaned_content:
                                                    if not ("¥" in cleaned_content or "元" in cleaned_content):
                                                        is_follow_up = True
                                                        logger.info(f"[扣子智能体] 过滤后续问题建议: {cleaned_content[:60]}")
                                                        break

                                        if is_follow_up:
                                            continue

                                        # 去重检查
                                        is_duplicate = False
                                        if len(cleaned_content) > 50:
                                            normalized_new = ''.join(cleaned_content.split())
                                            normalized_full = ''.join(full_response.split())
                                            if len(normalized_full) > 50 and normalized_new in normalized_full:
                                                is_duplicate = True

                                        if not is_duplicate:
                                            full_response += cleaned_content
                                            yield cleaned_content

                            except json.JSONDecodeError:
                                # JSON 不完整，继续累积
                                continue
                            except Exception as e:
                                logger.warning(f"解析响应行失败: {e}")
                                continue

                    # 如果流式响应没有返回有效内容
                    if not full_response:
                        logger.warning("扣子智能体未返回有效内容")
                        yield "（智能体正在思考中，请重新发送问题...）"

        except Exception as e:
            logger.error(f"调用扣子智能体异常: {str(e)}")
            import traceback
            logger.error(f"异常详情: {traceback.format_exc()}")
            yield f"⚠️ 智能体服务异常，请稍后重试（错误: {type(e).__name__}）"

    @classmethod
    async def _simulate_canteen_agent(
        cls,
        message: str,
        knowledge_base: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        本地模拟食堂智能体（当没有配置扣子Bot时使用）
        基于简单的关键词匹配和知识库内容生成回复
        """
        import random

        # 基础问候和菜单查询
        message_lower = message.lower()

        # 知识库内容优先
        if knowledge_base and len(knowledge_base) > 0:
            # 如果有知识库内容，基于知识库回复
            intro_text = "根据食堂系统的数据，我来为您解答：\n\n"
            yield intro_text

            # 逐段流式返回知识库内容
            for item in knowledge_base[:5]:
                text = f"• {item}\n"
                for char in text:
                    yield char
                    await asyncio.sleep(0.01)

            yield "\n如果需要更详细的分析，请在扣子平台配置智能体后获得更强的分析能力。"
            return

        # 简单的本地对话模拟
        responses = []

        # 关键词匹配
        if any(kw in message for kw in ['菜', '菜单', '菜品', '今天有什么', '推荐']):
            responses = [
                "根据我们的食堂数据库，目前有以下菜品信息可以查询：\n\n",
                "• 菜单数据：包含40种菜品，涵盖红烧肉、宫保鸡丁、鱼香肉丝等\n",
                "• 菜品价格：从18元到38元不等\n",
                "• 每日菜单会根据库存动态调整\n\n",
                "您可以询问具体的菜品信息，或者在AI分析页面查看详细的菜品推荐分析。"
            ]

        elif any(kw in message_lower for kw in ['库存', '剩余', '缺货', '采购']):
            responses = [
                "关于食堂库存情况：\n\n",
                "• 当前库存记录共101条\n",
                "• 包含肉类、蔬菜、粮油等多个分类\n",
                "• 系统会自动记录出入库情况并计算周转率\n\n",
                "您可以在库存看板查看详细的库存状态分析，或查询具体物资的库存余量。"
            ]

        elif any(kw in message_lower for kw in ['收入', '支出', '利润', '多少钱', '财务', '成本']):
            responses = [
                "关于食堂财务状况：\n\n",
                "• 收支记录：共101条记录\n",
                "• 利润数据：按日/周/月统计利润\n",
                "• 收入来源：主要来自菜品销售\n",
                "• 支出项目：食材采购、水电燃气、人工成本等\n\n",
                "您可以在收支看板查看详细的财务分析，包括利润率、成本结构等。"
            ]

        elif any(kw in message_lower for kw in ['订单', '点单', '销售', '顾客']):
            responses = [
                "关于食堂订单和销售情况：\n\n",
                "• 订单记录：共21条订单\n",
                "• 支付方式：支付宝、微信支付、银行卡等\n",
                "• 订单状态：支持下单、支付、完成等多种状态\n",
                "• 顾客信息：系统记录用户信息和消费情况\n\n",
                "您可以在食堂销售看板查看销售趋势分析。"
            ]

        elif any(kw in message_lower for kw in ['员工', '厨师', '服务员', '人员']):
            responses = [
                "食堂员工信息：\n\n",
                "• 员工人数：共5名员工\n",
                "• 岗位类型：厨师、服务员、收银员等\n",
                "• 员工信息：包含联系方式、入职时间等\n\n",
                "如需查看详细信息，请在员工管理页面操作。"
            ]

        elif any(kw in message_lower for kw in ['你好', 'hi', 'hello', '在吗', '您好']):
            responses = [
                "您好！我是食堂智能助手 🍜\n\n",
                "我可以帮您：\n",
                "• 查询菜品信息和推荐\n",
                "• 了解库存状态和采购建议\n",
                "• 分析收入支出和利润情况\n",
                "• 查询订单和销售数据\n\n",
                "请问您想了解什么？"
            ]

        else:
            responses = [
                "我是食堂智能助手，基于食堂系统数据库为您提供服务。\n\n",
                "您可以询问：\n",
                "• 今天有什么菜品推荐？\n",
                "• 库存情况如何？\n",
                "• 本月收入和利润是多少？\n",
                "• 最近的销售趋势如何？\n\n",
                "如需更强大的智能分析能力，建议在扣子平台创建智能体并配置到系统中。"
            ]

        # 流式返回
        for response in responses:
            for char in response:
                yield char
                await asyncio.sleep(0.01)

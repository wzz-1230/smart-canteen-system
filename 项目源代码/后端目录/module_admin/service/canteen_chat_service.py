"""
食堂 AI 对话服务。
- 通过关键词识别用户意图（查询菜品 / 查询订单 / 查询餐桌 / 闲聊）
- 读取数据库实时数据拼接结构化回答
- 优先调用大模型（如果配置了密钥）对结构化结果自然语言润色
- 大模型不可用时直接回退为结构化文本（Markdown）
"""
from __future__ import annotations

import json
import os
from datetime import datetime, time
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.env import AppConfig
from module_admin.entity.do.canteen_do import CanteenMenu, DiningTable, OrderDetail, OrderRecord


# ---- 工具函数：数据库查询 ----


async def _fetch_menus(db: AsyncSession, keyword: str | None = None) -> list[dict[str, Any]]:
    query = select(CanteenMenu).where(CanteenMenu.status == '0')
    if keyword:
        like = f'%{keyword}%'
        query = query.where(
            and_(CanteenMenu.status == '0', CanteenMenu.menu_name.like(like))
        )
    query = query.order_by(CanteenMenu.sort_order, desc(CanteenMenu.create_time)).limit(30)
    rows = (await db.execute(query)).scalars().all()
    result = []
    for r in rows:
        item = {
            'menu_id': r.menu_id,
            'menu_name': r.menu_name,
            'menu_type': r.menu_type,
            'price': r.price,
            'description': r.description or '',
            'image_url': r.image_url or '',
        }
        result.append(item)
    return result


async def _fetch_orders(db: AsyncSession, user_id: int | None = None) -> list[dict[str, Any]]:
    query = select(OrderRecord)
    if user_id:
        query = query.where(OrderRecord.user_id == user_id)
    query = query.order_by(desc(OrderRecord.create_time)).limit(10)
    rows = (await db.execute(query)).scalars().all()
    order_ids = [r.order_id for r in rows]
    details: dict[int, list[dict[str, Any]]] = {}
    if order_ids:
        detail_rows = (
            (await db.execute(select(OrderDetail).where(OrderDetail.order_id.in_(order_ids))))
            .scalars()
            .all()
        )
        for d in detail_rows:
            details.setdefault(d.order_id, []).append({
                'menu_name': d.menu_name,
                'quantity': d.quantity,
                'price': d.price,
                'amount': d.amount,
            })
    result = []
    for r in rows:
        result.append({
            'order_id': r.order_id,
            'order_no': r.order_no,
            'total_amount': r.total_amount,
            'order_status': r.order_status,
            'create_time': r.create_time.strftime('%Y-%m-%d %H:%M') if r.create_time else '',
            'items': details.get(r.order_id, []),
        })
    return result


async def _fetch_tables(db: AsyncSession, status: str | None = None) -> list[dict[str, Any]]:
    query = select(DiningTable)
    if status is not None:
        query = query.where(DiningTable.table_status == status)
    query = query.order_by(DiningTable.table_no).limit(50)
    rows = (await db.execute(query)).scalars().all()
    return [
        {
            'table_id': r.table_id,
            'table_no': r.table_no,
            'table_name': r.table_name or '',
            'capacity': r.capacity,
            'table_status': r.table_status,
            'location': r.location or '',
        }
        for r in rows
    ]


# ---- 意图识别 ----


def _parse_intent(question: str) -> dict[str, Any]:
    text = question or ''
    if any(k in text for k in ['菜', '菜品', '菜单', '有什么', '吃什么', '推荐', '餐', '饭', '点菜']):
        keyword = None
        for k in ['红烧肉', '宫保鸡丁', '鱼香肉丝', '糖醋排骨', '麻婆豆腐', '水煮肉片',
                  '回锅肉', '干煸豆角', '地三鲜', '蛋炒饭', '扬州炒饭', '牛肉面',
                  '炸酱面', '葱油拌面', '番茄炒蛋', '番茄鸡蛋面', '紫菜蛋花汤',
                  '西红柿鸡蛋汤', '酸辣汤', '排骨玉米汤', '凉拌木耳', '凉拌黄瓜',
                  '口水鸡', '夫妻肺片', '皮蛋豆腐', '白米饭', '矿泉水', '可乐',
                  '雪碧', '酸梅汤', '橙汁', '冰红茶', '绿豆汤']:
            if k in text:
                keyword = k
                break
        return {'intent': 'menu', 'keyword': keyword}
    if any(k in text for k in ['订单', '我点的', '我的订单', '消费', '账单']):
        return {'intent': 'order'}
    if any(k in text for k in ['桌子', '餐桌', '座位', '订桌', '包厢', '有空']):
        return {'intent': 'table'}
    return {'intent': 'chat'}


# ---- 结构化回答 ----


STATUS_TEXT = {
    '0': '待支付',
    '1': '已支付',
    '2': '已完成',
    '3': '已取消',
}

MENU_TYPE_TEXT = {'0': '热菜', '1': '凉菜', '2': '主食', '3': '汤品', '4': '饮品'}
TABLE_STATUS_TEXT = {'0': '空闲', '1': '占用', '2': '预订'}


def _render_menu(items: list[dict[str, Any]], keyword: str | None) -> str:
    if not items:
        if keyword:
            return f'抱歉，没有找到与"{keyword}"相关的菜品。'
        return '目前没有在售菜品，请到现场确认。'
    lines = []
    if keyword:
        lines.append(f'为您推荐与"{keyword}"相关的菜品 👇')
    else:
        lines.append('以下是目前在售的菜品（前 30 条）：')
    for item in items:
        mt = MENU_TYPE_TEXT.get(str(item.get('menu_type') or ''), '其他')
        img = item.get('image_url', '')
        lines.append(
            f"- {item['menu_name']}（{mt}） ¥{float(item['price']):.2f}"
            + (f" — {item['description']}" if item.get('description') else '')
            + (f" — 图片: {img}" if img else '')
        )
    lines.append('> 提示：你可以说「来一份红烧肉」或询问「今天有什么汤」。')
    return '\n'.join(lines)


def _render_order(items: list[dict[str, Any]]) -> str:
    if not items:
        return '没有查询到订单记录。'
    lines = [f'共查询到 {len(items)} 条订单：']
    for o in items:
        status_txt = STATUS_TEXT.get(str(o.get('order_status') or ''), o.get('order_status') or '')
        lines.append(
            f"- {o['order_no']}（{status_txt}） 金额 ¥{float(o['total_amount']):.2f}  下单时间 {o['create_time']}"
        )
        for it in o['items']:
            lines.append(f"    · {it['menu_name']} × {it['quantity']}  小计 ¥{float(it['amount']):.2f}")
    return '\n'.join(lines)


def _render_table(items: list[dict[str, Any]]) -> str:
    if not items:
        return '没有查询到餐桌信息。'
    lines = [f'共查询到 {len(items)} 张餐桌：']
    for t in items:
        st = TABLE_STATUS_TEXT.get(str(t.get('table_status') or ''), t.get('table_status') or '')
        lines.append(
            f"- {t['table_no']}（{st}） 容量 {t['capacity']} 人"
            + (f" · {t['location']}" if t.get('location') else '')
        )
    return '\n'.join(lines)


# ---- 大模型：可选，有密钥才调用 ----


def _has_llm_key() -> bool:
    key = getattr(AppConfig, 'chat_model_key', None) or os.environ.get('CHAT_MODEL_KEY', '')
    return bool(key and str(key).strip())


async def _call_llm(question: str, context: str) -> str | None:
    """尝试使用 httpx 调用 OpenAI 兼容接口。失败或未配置时返回 None。"""
    try:
        import httpx  # noqa: F401
    except Exception:
        return None
    if not _has_llm_key():
        return None
    try:
        import httpx
        api_key = getattr(AppConfig, 'chat_model_key', None) or os.environ.get('CHAT_MODEL_KEY', '')
        base_url = getattr(AppConfig, 'chat_model_base', None) or os.environ.get(
            'CHAT_MODEL_BASE', 'https://api.deepseek.com'
        )
        model = getattr(AppConfig, 'chat_model_name', None) or os.environ.get(
            'CHAT_MODEL_NAME', 'deepseek-chat'
        )
        messages = [
            {
                'role': 'system',
                'content': (
                    '你是食堂的智能服务员，说话简洁、口语化、中文回答。\n'
                    '使用下面"上下文"中的真实数据回复用户，不要编造菜品、价格或订单信息。\n'
                    '如果数据中没有相关信息，直接告诉用户"暂时没有相关信息"。\n'
                    '【重要】每道菜品都有 "图片" 字段，格式为 /static/canteen-menu-images/菜名.png 或 .jpg。\n'
                    '【重要】在回复用户关于菜品的问题时，务必附上对应的图片URL，格式示例：\n'
                    '- 红烧肉 ¥38.00 - 图片: http://localhost:9099/static/canteen-menu-images/红烧肉.jpg\n'
                    '【重要】所有图片URL前缀都是 http://localhost:9099，图片URL格式类似 /static/canteen-menu-images/xxx.png。\n'
                ),
            },
            {'role': 'user', 'content': f'用户问题：{question}\n\n上下文：\n{context}'},
        ]
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
            r = await client.post(
                '/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'model': model, 'messages': messages, 'temperature': 0.3},
            )
            if r.status_code != 200:
                return None
            data = r.json()
            return data['choices'][0]['message']['content'].strip()
    except Exception:
        return None


# ---- 对外主入口 ----


async def chat(db: AsyncSession, question: str, user_id: int | None = None) -> str:
    intent = _parse_intent(question)
    structured: str
    structured_data: dict[str, Any] = {}
    if intent['intent'] == 'menu':
        items = await _fetch_menus(db, keyword=intent.get('keyword'))
        structured_data = {'kind': 'menu', 'items': items}
        structured = _render_menu(items, intent.get('keyword'))
    elif intent['intent'] == 'order':
        items = await _fetch_orders(db, user_id=user_id)
        structured_data = {'kind': 'order', 'items': items}
        structured = _render_order(items)
    elif intent['intent'] == 'table':
        items = await _fetch_tables(db)
        structured_data = {'kind': 'table', 'items': items}
        structured = _render_table(items)
    else:
        structured = (
            '你好，我是食堂智能服务员。你可以这样问我：\n'
            '- 「有什么菜」「推荐红烧肉」\n'
            '- 「我的订单」\n'
            '- 「有哪些空桌子」'
        )
        structured_data = {'kind': 'chat'}
    # 有密钥时尝试交给大模型润色
    llm_answer = await _call_llm(
        question,
        f"意图：{intent['intent']}\n结构化数据：{json.dumps(structured_data, ensure_ascii=False, default=str)}\n格式化回答：\n{structured}",
    )
    return llm_answer or structured

import asyncio
import json
from typing import Any, AsyncIterator, List, Optional

from agno.models.base import Model


class LocalCanteenModel(Model):
    def __init__(self, id: str, name: Optional[str] = None, **kwargs):
        super().__init__(id=id, name=name or '食堂助手', **kwargs)
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 2048)

    async def arun(self, messages: List[dict], **kwargs) -> str:
        last_message = messages[-1]['content'] if messages else ''
        response = self._generate_response(last_message)
        return response

    async def astream(self, messages: List[dict], **kwargs) -> AsyncIterator[str]:
        last_message = messages[-1]['content'] if messages else ''
        response = self._generate_response(last_message)
        chunk_size = 20
        for i in range(0, len(response), chunk_size):
            yield response[i:i + chunk_size]
            await asyncio.sleep(0.05)

    def _generate_response(self, query: str) -> str:
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ['你好', 'hi', 'hello', '您好']):
            return '您好！我是食堂智能助手，很高兴为您服务。请问您想了解什么菜品？'

        if any(keyword in query_lower for keyword in ['菜单', '菜品', '吃什么', '有什么']):
            return '食堂目前提供多种美味菜品，包括：\n\n🍛 热菜类：宫保鸡丁、红烧肉、鱼香肉丝、青椒肉丝\n🥗 凉菜类：凉拌黄瓜、凉拌木耳、拍黄瓜、凉拌鸡丝\n🍲 汤品类：西红柿鸡蛋汤、紫菜蛋花汤、冬瓜排骨汤、海带豆腐汤\n🍚 主食类：米饭、馒头、面条、水饺\n🥤 饮料类：可乐、雪碧、果汁、矿泉水\n\n请问您想了解哪个具体菜品？'

        if any(keyword in query_lower for keyword in ['宫保鸡丁']):
            return '宫保鸡丁是我们的招牌菜之一！\n\n🍗 菜品特点：鸡肉鲜嫩，花生米酥脆，微辣酸甜\n💰 价格：28元\n🌟 推荐指数：⭐⭐⭐⭐⭐\n\n需要帮您点这道菜吗？'

        if any(keyword in query_lower for keyword in ['红烧肉']):
            return '红烧肉是我们的经典菜品！\n\n🥩 菜品特点：肥而不腻，入口即化，色泽红亮\n💰 价格：38元\n🌟 推荐指数：⭐⭐⭐⭐⭐\n\n需要帮您点这道菜吗？'

        if any(keyword in query_lower for keyword in ['鱼香肉丝']):
            return '鱼香肉丝是一道非常受欢迎的川菜！\n\n🥢 菜品特点：肉丝滑嫩，配菜丰富，酸甜微辣\n💰 价格：26元\n🌟 推荐指数：⭐⭐⭐⭐\n\n需要帮您点这道菜吗？'

        if any(keyword in query_lower for keyword in ['青椒肉丝']):
            return '青椒肉丝是一道家常美味！\n\n🌶️ 菜品特点：青椒爽脆，肉丝鲜嫩，咸香可口\n💰 价格：24元\n🌟 推荐指数：⭐⭐⭐⭐\n\n需要帮您点这道菜吗？'

        if any(keyword in query_lower for keyword in ['米饭', '馒头', '面条', '水饺']):
            return '我们的主食区提供：\n\n🍚 米饭：3元/份\n🥠 馒头：2元/个\n🍜 面条：15元/碗（可选择牛肉面、鸡蛋面等）\n🥟 水饺：20元/份（约20个）\n\n需要帮您点主食吗？'

        if any(keyword in query_lower for keyword in ['汤', '汤品']):
            return '我们提供多种美味汤品：\n\n🍲 西红柿鸡蛋汤：8元\n🍲 紫菜蛋花汤：8元\n🍲 冬瓜排骨汤：15元\n🍲 海带豆腐汤：10元\n\n需要帮您点汤吗？'

        if any(keyword in query_lower for keyword in ['饮料', '喝']):
            return '我们的饮料区提供：\n\n🥤 可乐/雪碧：6元\n🥤 果汁（橙汁/苹果汁）：8元\n💧 矿泉水：3元\n☕ 热饮：咖啡12元，奶茶10元\n\n需要帮您点饮料吗？'

        if any(keyword in query_lower for keyword in ['价格', '多少钱']):
            return '我们的菜品价格实惠，热菜20-40元，凉菜8-15元，汤品8-15元，主食3-20元，饮料3-12元。具体价格可以在菜单中查看。'

        if any(keyword in query_lower for keyword in ['营业时间', '几点', '开门']):
            return '食堂营业时间：\n\n🌅 早餐：6:30 - 9:00\n🌞 午餐：11:00 - 13:30\n🌙 晚餐：17:00 - 19:30\n\n周末和节假日营业时间可能有所调整，请关注通知。'

        if any(keyword in query_lower for keyword in ['点餐', '点单', '下单']):
            return '您可以通过"线上点单"功能进行点餐，选择您喜欢的菜品和餐桌，提交后即可完成下单。如需帮助，请告诉我您想点什么菜！'

        if any(keyword in query_lower for keyword in ['谢谢', '感谢', 'bye', '再见']):
            return '不客气！祝您用餐愉快！如有其他问题，随时可以问我。'

        return f'我是食堂智能助手，很高兴为您服务。\n\n您问的是："{query}"\n\n关于食堂的常见问题，您可以问我：\n- 有哪些菜品？\n- 某个菜品的价格和特点\n- 营业时间\n- 如何点餐\n\n请问还有什么可以帮到您的？'
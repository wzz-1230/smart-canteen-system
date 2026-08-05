"""
食堂知识库服务
从数据库中提取食堂相关数据，生成知识库文本，供智能体使用
"""
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy import text, select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.log_util import logger


class CanteenKnowledgeService:
    """食堂知识库服务"""

    @classmethod
    async def get_menu_knowledge(cls, query_db: AsyncSession, include_all: bool = True) -> List[str]:
        """
        获取菜单/菜品知识库内容（实时从数据库读取）

        Args:
            query_db: 数据库会话
            include_all: 是否包含所有菜品（True=包含下架，False=仅上架）
        """
        knowledge = []

        try:
            # 获取所有菜品（包括图片URL，让智能体能够回复图片信息）
            # 列索引: 0=menu_name, 1=menu_type, 2=price, 3=description, 4=sort_order, 5=status, 6=image_url
            if include_all:
                result = await query_db.execute(
                    text("SELECT menu_name, menu_type, price, description, sort_order, status, image_url FROM canteen_menu ORDER BY sort_order, menu_id")
                )
            else:
                result = await query_db.execute(
                    text("SELECT menu_name, menu_type, price, description, sort_order, status, image_url FROM canteen_menu WHERE status = '0' ORDER BY sort_order, menu_id")
                )
            rows = result.fetchall()

            if rows:
                # 统计信息
                total_count = len(rows)
                available_count = sum(1 for r in rows if r[5] == '0')
                unavailable_count = total_count - available_count

                knowledge.append(f"【食堂菜单信息】共 {total_count} 道菜品（{available_count} 道上架，{unavailable_count} 道下架）")
                knowledge.append(f"【重要提示】每道菜品都有对应的图片 URL，格式为 /static/canteen-menu-images/菜名.png。图片可以通过后端服务访问，完整访问地址为 http://localhost:9099 + image_url 字段值。")

                # 分类统计
                type_map = {}
                for row in rows:
                    menu_type = str(row[1]) if row[1] is not None else '其他'
                    if menu_type not in type_map:
                        type_map[menu_type] = []
                    type_map[menu_type].append(row)

                # 按分类输出 - 使用实际的分类名称
                type_cn_map = {'0': '荤菜/热菜', '1': '凉菜/小吃', '2': '主食/米饭/面食', '3': '汤品', '4': '饮料/饮品', '5': '小吃'}

                for menu_type, items in type_map.items():
                    type_name = type_cn_map.get(menu_type, f'分类{menu_type}')
                    # 统计该分类的上架/下架数量
                    type_available = sum(1 for it in items if it[5] == '0')
                    type_unavailable = len(items) - type_available
                    knowledge.append(f"\n【{type_name}】共 {len(items)} 道（上架 {type_available} 道，下架 {type_unavailable} 道）：")

                    import os
                    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'canteen-menu-images')
                    
                    for item in items:
                        name = item[0]
                        price = item[2]
                        desc = item[3] or ''
                        status = item[5]
                        image_url = item[6] if len(item) > 6 and item[6] else ''
                        
                        # 如果数据库中没有图片URL，尝试在本地目录按菜名匹配
                        if not image_url and name:
                            # 尝试常见图片扩展名
                            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                                candidate = os.path.join(static_dir, name + ext)
                                if os.path.exists(candidate):
                                    image_url = f"/static/canteen-menu-images/{name}{ext}"
                                    break
                        
                        # 明确标注上下架状态
                        status_str = "✅ 上架" if status == '0' else "❌ 下架"
                        price_str = f"¥{float(price):.1f}" if price else "价格待定"
                        # 格式化菜品信息，让智能体更易理解
                        desc_str = f" - {desc[:80]}" if desc else ""
                        # 加入图片 URL 信息
                        image_str = f" [图片: {image_url}]" if image_url else " [图片: 暂无]"
                        knowledge.append(f"  • {name}（{price_str}）{status_str}{desc_str}{image_str}")

                # 图片信息说明（让智能体知道如何回复图片）
                knowledge.append(f"\n【菜品图片说明】所有菜品图片均存储在后端静态资源目录 /static/canteen-menu-images/ 下，可通过 http://localhost:9099{image_url}（image_url 为该菜品的图片路径）直接访问图片。请在回答用户关于菜品的问题时，在菜品名称后附上对应的图片 URL（使用 ![图片描述](http://localhost:9099/path/to/image.png) 格式展示）。")

                # 价格统计 - 基于上架菜品
                available_prices = [float(r[2]) for r in rows if r[5] == '0' and r[2]]
                if available_prices:
                    avg_price = sum(available_prices) / len(available_prices)
                    min_price = min(available_prices)
                    max_price = max(available_prices)
                    knowledge.append(f"\n【上架菜品价格统计】最低价 ¥{min_price:.1f}，最高价 ¥{max_price:.1f}，平均价格 ¥{avg_price:.1f}")

                # 价格区间分布
                price_ranges = {
                    '10元以下': 0,
                    '10-20元': 0,
                    '20-30元': 0,
                    '30元以上': 0
                }
                for r in rows:
                    if r[5] == '0' and r[2]:
                        price = float(r[2])
                        if price < 10:
                            price_ranges['10元以下'] += 1
                        elif price < 20:
                            price_ranges['10-20元'] += 1
                        elif price < 30:
                            price_ranges['20-30元'] += 1
                        else:
                            price_ranges['30元以上'] += 1

                knowledge.append(f"\n【价格区间分布】（上架菜品）")
                for pr, count in price_ranges.items():
                    if count > 0:
                        knowledge.append(f"  • {pr}: {count} 道")

                # 下架菜品列表（单独列出，让智能体能够回答）
                if unavailable_count > 0:
                    knowledge.append(f"\n【下架菜品提醒】以下菜品当前为下架状态，暂不提供：")
                    for row in rows:
                        if row[5] != '0':
                            name = row[0]
                            price = row[2]
                            price_str = f"¥{float(price):.1f}" if price else ""
                            knowledge.append(f"  • {name}{(' ' + price_str) if price_str else ''}（已下架）")

        except Exception as e:
            logger.error(f"获取菜单知识库失败: {e}")
            knowledge.append(f"菜单信息获取失败: {str(e)}")

        return knowledge

    @classmethod
    async def get_inventory_knowledge(cls, query_db: AsyncSession) -> List[str]:
        """获取库存知识库内容"""
        knowledge = []

        try:
            # 库存统计
            result = await query_db.execute(
                text("SELECT COUNT(*), SUM(total_value), AVG(remaining_quantity) FROM canteen_inventory WHERE status = '0'")
            )
            stat_row = result.fetchone()
            total_items = stat_row[0] if stat_row[0] else 0
            total_value = stat_row[1] if stat_row[1] else 0

            if total_items > 0:
                knowledge.append(f"【库存信息】共 {total_items} 条库存记录，总价值 {total_value:.2f} 元")

                # 分类统计
                result = await query_db.execute(
                    text("SELECT item_type, COUNT(*), SUM(total_value), SUM(remaining_quantity * unit_price) FROM canteen_inventory WHERE status = '0' GROUP BY item_type ORDER BY COUNT(*) DESC")
                )
                type_rows = result.fetchall()

                if type_rows:
                    knowledge.append("\n【库存分类】")
                    for t_row in type_rows:
                        item_type = t_row[0] or '其他'
                        count = t_row[1]
                        value = t_row[2] or 0
                        knowledge.append(f"  • {item_type}：{count} 项，价值 {value:.2f} 元")

                # 高价值物品
                result = await query_db.execute(
                    text("SELECT item_name, remaining_quantity, unit, unit_price, total_value FROM canteen_inventory WHERE status = '0' ORDER BY total_value DESC LIMIT 5")
                )
                top_rows = result.fetchall()
                if top_rows:
                    knowledge.append("\n【高价值物资TOP5】")
                    for r in top_rows:
                        knowledge.append(f"  • {r[0]}：剩余 {r[1]}{r[2]}，单价 {r[3]:.2f}元，价值 {r[4]:.2f}元")

                # 低库存预警
                result = await query_db.execute(
                    text("SELECT item_name, remaining_quantity, unit FROM canteen_inventory WHERE status = '0' AND remaining_quantity < 20 ORDER BY remaining_quantity ASC LIMIT 5")
                )
                low_rows = result.fetchall()
                if low_rows:
                    knowledge.append("\n【低库存预警】")
                    for r in low_rows:
                        knowledge.append(f"  ⚠️ {r[0]}：仅剩余 {r[1]}{r[2]}")

        except Exception as e:
            logger.error(f"获取库存知识库失败: {e}")
            knowledge.append(f"库存信息获取失败")

        return knowledge

    @classmethod
    async def get_finance_knowledge(cls, query_db: AsyncSession) -> List[str]:
        """获取财务/收支知识库内容"""
        knowledge = []

        try:
            # 收支统计
            result = await query_db.execute(
                text("SELECT COUNT(*) FROM canteen_revenue_expense WHERE status = '0'")
            )
            total_rows = result.fetchone()[0] or 0

            if total_rows > 0:
                knowledge.append(f"【收支信息】共 {total_rows} 条收支记录")

                # 收入统计
                result = await query_db.execute(
                    text("SELECT COUNT(*), SUM(amount) FROM canteen_revenue_expense WHERE record_type = '0' AND status = '0'")
                )
                income_row = result.fetchone()
                income_count = income_row[0] or 0
                income_total = income_row[1] or 0

                # 支出统计
                result = await query_db.execute(
                    text("SELECT COUNT(*), SUM(amount) FROM canteen_revenue_expense WHERE record_type = '1' AND status = '0'")
                )
                expense_row = result.fetchone()
                expense_count = expense_row[0] or 0
                expense_total = expense_row[1] or 0

                net_profit = income_total - expense_total

                knowledge.append(f"\n【总体财务】")
                knowledge.append(f"  • 收入：{income_count} 笔，共计 {income_total:.2f} 元")
                knowledge.append(f"  • 支出：{expense_count} 笔，共计 {expense_total:.2f} 元")
                knowledge.append(f"  • 净利润：{net_profit:.2f} 元（利润率 {net_profit/income_total*100:.1f}%）" if income_total > 0 else "  • 暂无收入数据")

                # 收入分类
                result = await query_db.execute(
                    text("SELECT category, SUM(amount) FROM canteen_revenue_expense WHERE record_type = '0' AND status = '0' GROUP BY category ORDER BY SUM(amount) DESC")
                )
                income_cats = result.fetchall()
                if income_cats:
                    knowledge.append(f"\n【收入来源】")
                    for cat in income_cats:
                        knowledge.append(f"  • {cat[0]}：{cat[1]:.2f} 元")

                # 支出分类
                result = await query_db.execute(
                    text("SELECT category, SUM(amount) FROM canteen_revenue_expense WHERE record_type = '1' AND status = '0' GROUP BY category ORDER BY SUM(amount) DESC")
                )
                expense_cats = result.fetchall()
                if expense_cats:
                    knowledge.append(f"\n【支出项目】")
                    for cat in expense_cats:
                        knowledge.append(f"  • {cat[0]}：{cat[1]:.2f} 元")

                # 最近的利润记录
                result = await query_db.execute(
                    text("SELECT period_name, revenue, cost, profit, profit_rate FROM canteen_profit ORDER BY start_date DESC LIMIT 3")
                )
                profit_rows = result.fetchall()
                if profit_rows:
                    knowledge.append(f"\n【近期利润】")
                    for r in profit_rows:
                        knowledge.append(f"  • {r[0]}：收入 {r[1]:.2f}元，成本 {r[2]:.2f}元，利润 {r[3]:.2f}元（利润率{r[4]:.1f}%）")

        except Exception as e:
            logger.error(f"获取财务知识库失败: {e}")
            knowledge.append(f"财务信息获取失败")

        return knowledge

    @classmethod
    async def get_order_knowledge(cls, query_db: AsyncSession) -> List[str]:
        """获取订单/销售知识库内容"""
        knowledge = []

        try:
            # 订单统计
            result = await query_db.execute(
                text("SELECT COUNT(*), SUM(total_amount), AVG(total_amount) FROM canteen_order WHERE order_status IN ('1', '2', '3')")
            )
            order_row = result.fetchone()
            total_orders = order_row[0] or 0
            total_sales = order_row[1] or 0
            avg_order = order_row[2] or 0

            if total_orders > 0:
                knowledge.append(f"【销售订单】共 {total_orders} 笔订单，总销售额 {total_sales:.2f} 元，平均客单价 {avg_order:.2f} 元")

                # 支付方式统计
                result = await query_db.execute(
                    text("SELECT pay_method, COUNT(*), SUM(total_amount) FROM canteen_order WHERE order_status IN ('1', '2', '3') GROUP BY pay_method ORDER BY SUM(total_amount) DESC")
                )
                pay_rows = result.fetchall()
                if pay_rows:
                    knowledge.append(f"\n【支付方式】")
                    for r in pay_rows:
                        method = r[0] or '其他'
                        knowledge.append(f"  • {method}：{r[1]} 笔，{r[2]:.2f} 元")

                # 热销菜品
                result = await query_db.execute(
                    text("SELECT menu_name, SUM(quantity), SUM(amount) FROM canteen_order_detail GROUP BY menu_name ORDER BY SUM(amount) DESC LIMIT 5")
                )
                hot_rows = result.fetchall()
                if hot_rows:
                    knowledge.append(f"\n【热销菜品TOP5】")
                    for r in hot_rows:
                        knowledge.append(f"  • {r[0]}：{r[1]} 份，{r[2]:.2f} 元")

        except Exception as e:
            logger.error(f"获取订单知识库失败: {e}")
            knowledge.append(f"订单信息获取失败")

        return knowledge

    @classmethod
    async def get_staff_knowledge(cls, query_db: AsyncSession) -> List[str]:
        """获取员工知识库内容"""
        knowledge = []

        try:
            result = await query_db.execute(
                text("SELECT staff_name, position, phone, hire_date FROM canteen_staff WHERE status = '0'")
            )
            rows = result.fetchall()

            if rows:
                knowledge.append(f"【员工信息】共 {len(rows)} 名员工")
                for r in rows:
                    knowledge.append(f"  • {r[0]}（{r[1]}）- 电话：{r[2]}，入职时间：{r[3]}")

        except Exception as e:
            logger.error(f"获取员工知识库失败: {e}")
            knowledge.append(f"员工信息获取失败")

        return knowledge

    @classmethod
    async def get_table_knowledge(cls, query_db: AsyncSession) -> List[str]:
        """获取餐桌知识库内容"""
        knowledge = []

        try:
            result = await query_db.execute(
                text("SELECT table_no, table_name, capacity, table_status, location FROM canteen_table")
            )
            rows = result.fetchall()

            if rows:
                total = len(rows)
                available = sum(1 for r in rows if r[3] == '0')
                occupied = total - available

                knowledge.append(f"【餐桌信息】共 {total} 张餐桌，{available} 张可用，{occupied} 张占用")

                locations = {}
                for r in rows:
                    loc = r[4] or '其他'
                    if loc not in locations:
                        locations[loc] = 0
                    locations[loc] += 1

                knowledge.append(f"\n【区域分布】")
                for loc, count in locations.items():
                    knowledge.append(f"  • {loc}：{count} 张桌")

                total_cap = sum(r[2] for r in rows)
                knowledge.append(f"\n【总容量】可同时容纳 {total_cap} 人就餐")

        except Exception as e:
            logger.error(f"获取餐桌知识库失败: {e}")
            knowledge.append(f"餐桌信息获取失败")

        return knowledge

    @classmethod
    async def get_recent_data_knowledge(cls, query_db: AsyncSession) -> List[str]:
        """获取最近数据摘要（用于实时问答）"""
        knowledge = []

        try:
            today = datetime.now().strftime('%Y-%m-%d')

            # 今日订单数
            result = await query_db.execute(
                text(f"SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM canteen_order WHERE DATE(create_time) = '{today}'")
            )
            today_row = result.fetchone()
            today_orders = today_row[0] or 0
            today_revenue = today_row[1] or 0

            # 本月数据
            result = await query_db.execute(
                text(f"SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM canteen_order WHERE YEAR(create_time) = YEAR(NOW()) AND MONTH(create_time) = MONTH(NOW())")
            )
            month_row = result.fetchone()
            month_orders = month_row[0] or 0
            month_revenue = month_row[1] or 0

            knowledge.append(f"\n【实时数据】（截至 {today}）")
            knowledge.append(f"  • 今日订单：{today_orders} 笔，收入 {today_revenue:.2f} 元")
            knowledge.append(f"  • 本月订单：{month_orders} 笔，收入 {month_revenue:.2f} 元")

            # 最近30天趋势
            result = await query_db.execute(
                text(f"SELECT DATE(create_time), COUNT(*), COALESCE(SUM(total_amount), 0) FROM canteen_order WHERE create_time >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY DATE(create_time) ORDER BY COUNT(*) DESC LIMIT 3")
            )
            top_days = result.fetchall()
            if top_days:
                knowledge.append(f"\n【近期销售高峰】")
                for day in top_days:
                    knowledge.append(f"  • {day[0]}：{day[1]} 笔订单，{day[2]:.2f} 元")

        except Exception as e:
            logger.error(f"获取实时数据知识库失败: {e}")

        return knowledge

    @classmethod
    async def generate_knowledge_base(
        cls,
        query_db: AsyncSession,
        query_type: str = 'all'
    ) -> List[str]:
        """
        生成完整的知识库内容

        Args:
            query_db: 数据库会话
            query_type: 查询类型 - all, menu, inventory, finance, order, staff, table

        Returns:
            知识库文本列表
        """
        knowledge = []

        # 标题
        knowledge.append("=" * 60)
        knowledge.append("【食堂智能助手知识库】")
        knowledge.append(f"数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        knowledge.append("=" * 60)

        # 根据查询类型调用不同的知识库生成
        type_map = {
            'menu': lambda: cls.get_menu_knowledge(query_db),
            'inventory': lambda: cls.get_inventory_knowledge(query_db),
            'finance': lambda: cls.get_finance_knowledge(query_db),
            'order': lambda: cls.get_order_knowledge(query_db),
            'staff': lambda: cls.get_staff_knowledge(query_db),
            'table': lambda: cls.get_table_knowledge(query_db),
            'all': None  # all 特殊处理
        }

        if query_type == 'all':
            # 获取所有知识库
            menu_data = await cls.get_menu_knowledge(query_db)
            knowledge.extend(menu_data)

            inv_data = await cls.get_inventory_knowledge(query_db)
            knowledge.extend(inv_data)

            finance_data = await cls.get_finance_knowledge(query_db)
            knowledge.extend(finance_data)

            order_data = await cls.get_order_knowledge(query_db)
            knowledge.extend(order_data)

            staff_data = await cls.get_staff_knowledge(query_db)
            knowledge.extend(staff_data)

            table_data = await cls.get_table_knowledge(query_db)
            knowledge.extend(table_data)

            recent_data = await cls.get_recent_data_knowledge(query_db)
            knowledge.extend(recent_data)
        elif query_type in type_map:
            func = type_map[query_type]
            if func:
                data = await func()
                knowledge.extend(data)

        # 添加提示
        knowledge.append("\n" + "=" * 60)
        knowledge.append("【说明】")
        knowledge.append("以上内容基于食堂数据库实时数据生成，仅供参考。")
        knowledge.append("如需更精确的查询，请在对应功能页面查看详细信息。")
        knowledge.append("=" * 60)

        return knowledge

    @classmethod
    async def analyze_query_and_get_knowledge(
        cls,
        query_db: AsyncSession,
        user_query: str
    ) -> List[str]:
        """
        智能分析用户查询，返回相关的知识库内容

        Args:
            query_db: 数据库会话
            user_query: 用户查询

        Returns:
            相关知识库内容
        """
        query_lower = user_query.lower()

        # 关键词映射
        keyword_map = {
            'menu': ['菜', '菜品', '菜单', '吃什么', '推荐', '价格', '菜系', '红烧肉', '宫保鸡丁', '鱼香肉丝'],
            'inventory': ['库存', '剩余', '缺货', '采购', '物资', '食材', '肉', '菜', '粮油'],
            'finance': ['收入', '支出', '利润', '成本', '多少', '财务', '盈利', '亏损', '营收', '支出'],
            'order': ['订单', '销售', '顾客', '点单', '销售', '客户', '支付', '支付宝', '微信'],
            'staff': ['员工', '厨师', '服务员', '人员', '员工', '管理', '电话'],
            'table': ['餐桌', '桌子', '位置', '座位', '大厅', '包厢']
        }

        # 检测查询类型
        query_types = []
        for qtype, keywords in keyword_map.items():
            for kw in keywords:
                if kw in user_query or kw.lower() in query_lower:
                    query_types.append(qtype)
                    break

        if not query_types:
            # 如果没有匹配特定类型，返回通用知识
            query_types = ['menu', 'inventory', 'finance', 'order']

        knowledge = []
        knowledge.append("【智能识别】根据您的查询，以下是相关信息：\n")

        for qtype in query_types:
            try:
                if qtype == 'menu':
                    data = await cls.get_menu_knowledge(query_db)
                elif qtype == 'inventory':
                    data = await cls.get_inventory_knowledge(query_db)
                elif qtype == 'finance':
                    data = await cls.get_finance_knowledge(query_db)
                elif qtype == 'order':
                    data = await cls.get_order_knowledge(query_db)
                elif qtype == 'staff':
                    data = await cls.get_staff_knowledge(query_db)
                elif qtype == 'table':
                    data = await cls.get_table_knowledge(query_db)
                else:
                    data = []

                if data:
                    knowledge.extend(data)
                    knowledge.append("")

            except Exception as e:
                logger.error(f"获取{qtype}知识库失败: {e}")

        # 添加实时数据
        try:
            recent = await cls.get_recent_data_knowledge(query_db)
            if recent:
                knowledge.extend(recent)
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")

        return knowledge

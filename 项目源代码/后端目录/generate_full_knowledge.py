import sys
import os

os.chdir(r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')
sys.path.insert(0, r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')

from sqlalchemy import text
from config.get_db import get_db
import asyncio

# 分类ID到文字的映射
category_map = {
    '0': '荤菜/热菜',
    '1': '凉菜/小吃',
    '2': '主食/米饭/面食',
    '3': '汤品',
    '4': '饮料/饮品'
}

async def get_all_knowledge():
    print("=" * 80)
    print("📋 正在生成完整的食堂知识库")
    print("=" * 80)
    
    async for db in get_db():
        output_lines = []
        
        # ============= 1. 菜单数据 =============
        print("\n[1/5] 读取菜单数据...", end="")
        result = await db.execute(text("SELECT * FROM canteen_menu ORDER BY menu_id"))
        menu_items = result.fetchall()
        
        output_lines.append("=" * 80)
        output_lines.append("【食堂系统知识库】")
        output_lines.append("=" * 80)
        output_lines.append("")
        output_lines.append("本知识库包含以下内容：")
        output_lines.append("  1. 菜品菜单（40道）")
        output_lines.append("  2. 库存信息")
        output_lines.append("  3. 订单数据")
        output_lines.append("  4. 收支和利润")
        output_lines.append("  5. 员工信息")
        output_lines.append("  6. 餐桌信息")
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("【一、菜品菜单】")
        output_lines.append("=" * 80)
        output_lines.append("")
        output_lines.append(f"当前共有 {len(menu_items)} 道菜品，分为 5 个分类：")
        output_lines.append("  荤菜/热菜: 15 道")
        output_lines.append("  凉菜/小吃: 5 道")
        output_lines.append("  主食/米饭/面食: 8 道")
        output_lines.append("  汤品: 5 道")
        output_lines.append("  饮料/饮品: 7 道")
        output_lines.append("")
        output_lines.append("-" * 80)
        
        # 按分类分组输出
        categories = {}
        for item in menu_items:
            menu_type = item[2] if item[2] else '0'
            cat_name = category_map.get(str(menu_type), str(menu_type))
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)
        
        # 按分类输出
        for cat_name, items in categories.items():
            output_lines.append("")
            output_lines.append(f"【{cat_name}】（共 {len(items)} 道）")
            output_lines.append("-" * 80)
            
            for idx, item in enumerate(items, 1):
                menu_id = item[0]
                menu_name = item[1] if item[1] else '未命名'
                price = item[3] if item[3] else 0
                description = item[5] if len(item) > 5 and item[5] else ''
                status = item[6] if len(item) > 6 and item[6] else '0'
                remark = item[12] if len(item) > 12 and item[12] else ''
                
                status_text = '✅ 上架' if str(status) == '0' else '❌ 下架'
                
                output_lines.append(f"  {idx}. {menu_name} - ¥{price}")
                output_lines.append(f"     状态: {status_text}")
                if description:
                    output_lines.append(f"     描述: {description}")
                if remark:
                    output_lines.append(f"     备注: {remark}")
                output_lines.append("")
        
        # 价格区间汇总
        prices = [item[3] for item in menu_items if item[3] is not None]
        if prices:
            output_lines.append("")
            output_lines.append("-" * 80)
            output_lines.append("【价格区间汇总】")
            output_lines.append(f"  最低价格: ¥{min(prices)}")
            output_lines.append(f"  最高价格: ¥{max(prices)}")
            output_lines.append(f"  平均价格: ¥{sum(prices)/len(prices):.1f}")
            output_lines.append("")
            
            # 价格区间统计
            price_ranges = [
                ("10元以下", 0, 10),
                ("10-20元", 10, 20),
                ("20-30元", 20, 30),
                ("30元以上", 30, 999999)
            ]
            for label, min_p, max_p in price_ranges:
                count = sum(1 for p in prices if min_p <= p < max_p)
                output_lines.append(f"  {label}: {count} 道")
            output_lines.append("")
        
        # ============= 2. 库存数据 =============
        print(f"\n✅ 菜单数据读取完成 ({len(menu_items)} 道菜)")
        print("[2/5] 读取库存数据...", end="")
        
        try:
            result = await db.execute(text("SELECT * FROM canteen_inventory ORDER BY id"))
            inventory_items = result.fetchall()
            
            output_lines.append("=" * 80)
            output_lines.append("【二、库存信息】")
            output_lines.append("=" * 80)
            output_lines.append("")
            
            if inventory_items:
                output_lines.append(f"当前共有 {len(inventory_items)} 条库存记录。")
                output_lines.append("")
                
                # 获取列名
                result_cols = await db.execute(text(
                    "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                    "WHERE TABLE_NAME = 'canteen_inventory' ORDER BY ORDINAL_POSITION"
                ))
                inv_columns = [row[0] for row in result_cols.fetchall()]
                
                for idx, item in enumerate(inventory_items, 1):
                    item_dict = {}
                    for i, col in enumerate(inv_columns):
                        item_dict[col] = item[i]
                    
                    output_lines.append(f"【记录 {idx}】")
                    
                    # 动态输出字段
                    for col in inv_columns:
                        if col in ['id', 'create_time', 'update_time', 'create_by', 'update_by']:
                            continue
                        
                        value = item_dict.get(col, '')
                        if value is None or value == '':
                            continue
                        
                        col_display = {
                            'item_name': '物品名称',
                            'item_type': '物品类型',
                            'quantity': '数量',
                            'unit': '单位',
                            'price': '单价',
                            'supplier': '供应商',
                            'stock_status': '库存状态',
                            'expiry_date': '有效期',
                            'remark': '备注',
                            'category': '分类',
                            'in_date': '入库日期',
                        }.get(col, col)
                        
                        output_lines.append(f"  {col_display}: {value}")
                    output_lines.append("")
            else:
                output_lines.append("暂无库存数据。")
                output_lines.append("")
        except Exception as e:
            output_lines.append(f"读取库存数据时出错: {e}")
            output_lines.append("")
        
        # ============= 3. 订单数据 =============
        print(f"\n✅ 库存数据读取完成")
        print("[3/5] 读取订单数据...", end="")
        
        try:
            result = await db.execute(text("SELECT * FROM canteen_order ORDER BY id"))
            order_items = result.fetchall()
            
            output_lines.append("=" * 80)
            output_lines.append("【三、订单数据】")
            output_lines.append("=" * 80)
            output_lines.append("")
            
            if order_items:
                output_lines.append(f"当前共有 {len(order_items)} 条订单记录。")
                output_lines.append("")
                
                # 获取列名
                result_cols = await db.execute(text(
                    "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                    "WHERE TABLE_NAME = 'canteen_order' ORDER BY ORDINAL_POSITION"
                ))
                order_columns = [row[0] for row in result_cols.fetchall()]
                
                # 订单统计
                total_amount = 0
                status_count = {}
                
                for item in order_items:
                    item_dict = {}
                    for i, col in enumerate(order_columns):
                        item_dict[col] = item[i]
                    
                    # 统计总金额
                    amount = item_dict.get('total_amount', item_dict.get('amount', 0))
                    if amount and isinstance(amount, (int, float)):
                        total_amount += amount
                    
                    # 统计状态
                    status = str(item_dict.get('status', '未知'))
                    status_count[status] = status_count.get(status, 0) + 1
                
                output_lines.append(f"订单总金额: ¥{total_amount:.2f}")
                output_lines.append(f"平均订单金额: ¥{total_amount/len(order_items):.2f}")
                output_lines.append("")
                output_lines.append("订单状态统计:")
                for status, count in status_count.items():
                    output_lines.append(f"  {status}: {count} 个")
                output_lines.append("")
                
                # 输出最近几个订单
                output_lines.append("最近订单列表（前 10 个）:")
                output_lines.append("-" * 80)
                
                for idx, item in enumerate(order_items[:10], 1):
                    item_dict = {}
                    for i, col in enumerate(order_columns):
                        item_dict[col] = item[i]
                    
                    order_no = item_dict.get('order_no', item_dict.get('order_id', f'订单{idx}'))
                    amount = item_dict.get('total_amount', item_dict.get('amount', 0))
                    status = item_dict.get('status', '未知')
                    order_time = item_dict.get('create_time', item_dict.get('order_time', ''))
                    
                    output_lines.append(f"  {idx}. {order_no} - 金额 ¥{amount} - 状态: {status}")
                    if order_time:
                        output_lines.append(f"     时间: {order_time}")
                    output_lines.append("")
            else:
                output_lines.append("暂无订单数据。")
                output_lines.append("")
        except Exception as e:
            output_lines.append(f"读取订单数据时出错: {e}")
            output_lines.append("")
        
        # ============= 4. 收支和利润 =============
        print(f"\n✅ 订单数据读取完成")
        print("[4/5] 读取收支利润数据...", end="")
        
        try:
            result = await db.execute(text("SELECT * FROM canteen_revenue_expense ORDER BY id"))
            revenue_items = result.fetchall()
            
            result2 = await db.execute(text("SELECT * FROM canteen_profit ORDER BY id"))
            profit_items = result2.fetchall()
            
            output_lines.append("=" * 80)
            output_lines.append("【四、收支与利润数据】")
            output_lines.append("=" * 80)
            output_lines.append("")
            
            if revenue_items:
                output_lines.append(f"当前共有 {len(revenue_items)} 条收支记录。")
                output_lines.append("")
                
                # 获取列名
                result_cols = await db.execute(text(
                    "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                    "WHERE TABLE_NAME = 'canteen_revenue_expense' ORDER BY ORDINAL_POSITION"
                ))
                rev_columns = [row[0] for row in result_cols.fetchall()]
                
                total_revenue = 0
                total_expense = 0
                
                for item in revenue_items:
                    item_dict = {}
                    for i, col in enumerate(rev_columns):
                        item_dict[col] = item[i]
                    
                    # 统计收入和支出
                    type_col = item_dict.get('type', '')
                    amount = item_dict.get('amount', 0)
                    
                    if isinstance(amount, (int, float)):
                        if '收' in str(type_col) or type_col in ['income', 'revenue', '1']:
                            total_revenue += amount
                        else:
                            total_expense += amount
                
                output_lines.append(f"📈 总收入: ¥{total_revenue:.2f}")
                output_lines.append(f"📉 总支出: ¥{total_expense:.2f}")
                output_lines.append(f"💰 净利润: ¥{(total_revenue - total_expense):.2f}")
                output_lines.append("")
                
                # 输出最近的收支记录
                output_lines.append("最近收支记录（前 5 条）:")
                output_lines.append("-" * 80)
                
                for idx, item in enumerate(revenue_items[:5], 1):
                    item_dict = {}
                    for i, col in enumerate(rev_columns):
                        item_dict[col] = item[i]
                    
                    desc = item_dict.get('description', item_dict.get('remark', ''))
                    amount = item_dict.get('amount', 0)
                    rec_type = item_dict.get('type', '')
                    
                    output_lines.append(f"  {idx}. [{rec_type}] {desc}")
                    output_lines.append(f"     金额: ¥{amount}")
                    output_lines.append("")
            
            if profit_items:
                output_lines.append(f"利润记录: {len(profit_items)} 条")
                output_lines.append("")
                
                for idx, item in enumerate(profit_items[:3], 1):
                    output_lines.append(f"  利润记录 {idx}: {item}")
                    output_lines.append("")
        except Exception as e:
            output_lines.append(f"读取收支数据时出错: {e}")
            output_lines.append("")
        
        # ============= 5. 员工和餐桌 =============
        print(f"\n✅ 收支数据读取完成")
        print("[5/5] 读取员工和餐桌数据...", end="")
        
        try:
            result = await db.execute(text("SELECT * FROM canteen_staff ORDER BY id"))
            staff_items = result.fetchall()
            
            result2 = await db.execute(text("SELECT * FROM canteen_table ORDER BY id"))
            table_items = result2.fetchall()
            
            output_lines.append("=" * 80)
            output_lines.append("【五、员工与餐桌】")
            output_lines.append("=" * 80)
            output_lines.append("")
            
            # 员工信息
            if staff_items:
                output_lines.append(f"员工人数: {len(staff_items)} 人")
                output_lines.append("")
                
                # 获取列名
                result_cols = await db.execute(text(
                    "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                    "WHERE TABLE_NAME = 'canteen_staff' ORDER BY ORDINAL_POSITION"
                ))
                staff_columns = [row[0] for row in result_cols.fetchall()]
                
                for idx, item in enumerate(staff_items, 1):
                    item_dict = {}
                    for i, col in enumerate(staff_columns):
                        item_dict[col] = item[i]
                    
                    name = item_dict.get('name', item_dict.get('staff_name', f'员工{idx}'))
                    position = item_dict.get('position', item_dict.get('role', ''))
                    phone = item_dict.get('phone', item_dict.get('contact', ''))
                    
                    output_lines.append(f"  {idx}. {name}")
                    if position:
                        output_lines.append(f"     职位: {position}")
                    if phone:
                        output_lines.append(f"     联系方式: {phone}")
                    output_lines.append("")
            
            # 餐桌信息
            if table_items:
                output_lines.append(f"餐桌数量: {len(table_items)} 张")
                output_lines.append("")
                
                # 获取列名
                result_cols = await db.execute(text(
                    "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                    "WHERE TABLE_NAME = 'canteen_table' ORDER BY ORDINAL_POSITION"
                ))
                table_columns = [row[0] for row in result_cols.fetchall()]
                
                for idx, item in enumerate(table_items, 1):
                    item_dict = {}
                    for i, col in enumerate(table_columns):
                        item_dict[col] = item[i]
                    
                    table_no = item_dict.get('table_no', item_dict.get('number', f'{idx}'))
                    capacity = item_dict.get('capacity', item_dict.get('seats', ''))
                    status = item_dict.get('status', '未知')
                    
                    output_lines.append(f"  {idx}. 餐桌 {table_no}")
                    if capacity:
                        output_lines.append(f"     座位数: {capacity}")
                    output_lines.append(f"     状态: {status}")
                    output_lines.append("")
        except Exception as e:
            output_lines.append(f"读取员工/餐桌数据时出错: {e}")
            output_lines.append("")
        
        # ============= 使用说明 =============
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("【知识库使用说明】")
        output_lines.append("=" * 80)
        output_lines.append("")
        output_lines.append("📌 本知识库包含了食堂系统的完整数据：")
        output_lines.append("")
        output_lines.append("1. 菜品菜单 - 40 道菜，包含价格、分类、描述、状态")
        output_lines.append("2. 库存信息 - 食材和物资的库存记录")
        output_lines.append("3. 订单数据 - 顾客订单记录及统计")
        output_lines.append("4. 收支利润 - 财务数据分析")
        output_lines.append("5. 员工餐桌 - 食堂基础运营信息")
        output_lines.append("")
        output_lines.append("📌 智能体回答规则:")
        output_lines.append("")
        output_lines.append("1. 只基于知识库中的信息回答，不要编造数据")
        output_lines.append("2. 价格信息要准确，使用人民币格式（¥价格）")
        output_lines.append("3. 菜品状态要明确标注（上架/下架）")
        output_lines.append("4. 如果知识库中没有相关信息，请诚实告知用户")
        output_lines.append("5. 用友好、简洁的语言回答")
        output_lines.append("6. 推荐菜品时可参考菜品描述和价格")
        output_lines.append("7. 统计数据要准确，根据实际记录回答")
        output_lines.append("")
        output_lines.append("📌 常见问题回答示例:")
        output_lines.append("")
        output_lines.append("Q: 有什么推荐的菜？")
        output_lines.append("A: 根据知识库中的菜品信息，推荐以下经典菜品：")
        output_lines.append("   - 红烧肉 ¥38（肥而不腻，入口即化）")
        output_lines.append("   - 宫保鸡丁 ¥28（酸甜微辣，鸡肉嫩爽）")
        output_lines.append("   - 牛肉面 ¥28（肉香浓郁，面条劲道）")
        output_lines.append("")
        output_lines.append("Q: 红烧肉多少钱？")
        output_lines.append("A: 根据知识库，红烧肉的价格是 ¥38。")
        output_lines.append("")
        output_lines.append("Q: 有什么素菜？")
        output_lines.append("A: 知识库中素菜主要在主食和热菜中。可推荐：")
        output_lines.append("   - 地三鲜 ¥22")
        output_lines.append("   - 干煸豆角 ¥20")
        output_lines.append("   - 麻婆豆腐 ¥18")
        output_lines.append("")
        output_lines.append("Q: 最贵的菜是什么？")
        output_lines.append("A: 根据知识库，目前最贵的菜品是红烧肉和夫妻肺片，均为 ¥38。")
        output_lines.append("")
        output_lines.append("Q: 最便宜的菜是什么？")
        output_lines.append("A: 根据知识库，最便宜的菜品是白米饭 ¥3 和矿泉水 ¥3。")
        output_lines.append("")
        output_lines.append("Q: 今天有什么特价？")
        output_lines.append("A: 知识库中暂未包含今日特价信息。目前菜品价格从 ¥3 到 ¥38 不等。")
        output_lines.append("")
        output_lines.append("Q: 糖醋排骨还有吗？")
        output_lines.append("A: 根据知识库，糖醋排骨目前为【下架】状态，暂不提供。")
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("【知识库生成时间】")
        output_lines.append("=" * 80)
        
        from datetime import datetime
        output_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"数据来源: 食堂系统数据库 (canteen_menu, inventory, order, profit, staff, table)")
        output_lines.append(f"总菜品数: {len(menu_items)} 道")
        output_lines.append("=" * 80)
        
        # 输出到控制台
        print(f"\n✅ 知识库生成完成！共 {len(output_lines)} 行")
        print("")
        print("=" * 80)
        output_content = "\n".join(output_lines)
        print(output_content)
        
        # 保存到文件
        output_file = r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\canteen_menu_knowledge_base.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n\n{'=' * 80}")
        print(f"✅ 完整知识库已保存到: {output_file}")
        print(f"   共 {len(output_lines)} 行文字，{len(output_content)} 个字符")
        print(f"{'=' * 80}")
        print("")
        print("📌 下一步操作:")
        print("")
        print("【方式一：在扣子平台添加知识库（推荐）】")
        print("  1. 打开文件: " + output_file)
        print("  2. 全选并复制所有内容")
        print("  3. 登录 https://www.coze.cn")
        print("  4. 进入你的智能体编辑页面")
        print("  5. 左侧导航找到 '知识库' 或 'Knowledge Base'")
        print("  6. 点击 '添加' 或 'Add'")
        print("  7. 选择文本粘贴方式，或上传txt文件")
        print("  8. 粘贴知识库内容，或上传生成的文件")
        print("  9. 保存后，智能体就能基于完整食堂信息回答问题了")
        print("")
        print("【方式二：通过系统后端API动态获取】")
        print("  注意：如果已正确配置 Bot ID，系统会自动将知识库内容")
        print("  通过 API 传递给智能体，无需手动添加知识库。")
        print("  但为了获得更好的效果，仍建议添加知识库。")
        print("")
        print(f"{'=' * 80}")
        
        break

asyncio.run(get_all_knowledge())

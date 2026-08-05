import sys
import os

os.chdir(r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')
sys.path.insert(0, r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')

from sqlalchemy import text
from config.get_db import get_db
import asyncio

async def get_menu_data():
    print("=" * 80)
    print("读取食堂菜单数据库 - 表结构")
    print("=" * 80)
    
    async for db in get_db():
        # 1. 检查表结构
        result = await db.execute(text("DESCRIBE canteen_menu"))
        columns = result.fetchall()
        print("\n【canteen_menu 表结构】")
        for col in columns:
            print(f"  {col[0]:<20} {col[1]:<20} {col[2]:<10} {col[3]:<10} {col[4] if col[4] else ''}")
        
        # 2. 读取所有菜品数据
        print("\n" + "=" * 80)
        print("读取所有菜品数据")
        print("=" * 80)
        
        result = await db.execute(text("SELECT * FROM canteen_menu ORDER BY id"))
        menu_items = result.fetchall()
        
        print(f"\n共找到 {len(menu_items)} 道菜")
        
        # 获取列名
        result = await db.execute(text("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = 'canteen_menu' ORDER BY ORDINAL_POSITION"))
        column_names = [row[0] for row in result.fetchall()]
        print(f"列名: {column_names}")
        
        # 3. 整理成知识库格式
        print("\n" + "=" * 80)
        print("📋 扣子知识库格式 - 食堂菜单")
        print("=" * 80)
        print("")
        
        output_lines = []
        
        output_lines.append("=" * 80)
        output_lines.append("【食堂菜单知识库】")
        output_lines.append("=" * 80)
        output_lines.append(f"")
        output_lines.append(f"当前共有 {len(menu_items)} 道菜，供智能问答使用。")
        output_lines.append(f"")
        output_lines.append("-" * 80)
        
        for idx, item in enumerate(menu_items, 1):
            # 将元组转换为字典
            item_dict = {}
            for i, col_name in enumerate(column_names):
                item_dict[col_name] = item[i]
            
            output_lines.append(f"")
            output_lines.append(f"【第 {idx} 道菜】")
            output_lines.append(f"菜名: {item_dict.get('name', item_dict.get('menu_name', '未知'))}")
            
            # 价格
            price = item_dict.get('price', item_dict.get('menu_price', None))
            if price:
                output_lines.append(f"价格: ¥{price}")
            
            # 分类
            category = item_dict.get('category', item_dict.get('menu_category', item_dict.get('type', '')))
            if category:
                output_lines.append(f"分类: {category}")
            
            # 描述
            description = item_dict.get('description', item_dict.get('menu_description', ''))
            if description:
                output_lines.append(f"描述: {description}")
            
            # 其他字段 - 动态输出
            for key, value in item_dict.items():
                if key not in ['id', 'name', 'menu_name', 'price', 'menu_price', 'category', 'menu_category', 
                               'type', 'description', 'menu_description', 'create_time', 'update_time', 
                               'created_at', 'updated_at', 'create_by', 'update_by', 'is_deleted', 'del_flag']:
                    if value is not None and value != '':
                        key_display = {
                            'status': '状态',
                            'stock': '库存',
                            'image': '图片',
                            'image_url': '图片地址',
                            'is_available': '是否上架',
                            'is_recommended': '是否推荐',
                            'spicy_level': '辣度',
                            'taste': '口味',
                            'ingredients': '食材',
                            'allergens': '过敏原',
                            'nutrition': '营养信息',
                            'calories': '卡路里',
                            'prep_time': '准备时间',
                            'serving_size': '份量',
                            'cooking_method': '烹饪方法',
                            'origin': '产地',
                            'tags': '标签',
                            'remark': '备注',
                            'comments': '说明',
                        }.get(key, key)
                        output_lines.append(f"{key_display}: {value}")
            
            output_lines.append(f"")
        
        # 添加总结信息
        output_lines.append("")
        output_lines.append("-" * 80)
        output_lines.append("【菜单分类统计】")
        
        # 统计分类
        categories = {}
        for item in menu_items:
            item_dict = {}
            for i, col_name in enumerate(column_names):
                item_dict[col_name] = item[i]
            cat = item_dict.get('category', item_dict.get('menu_category', 
                      item_dict.get('type', item_dict.get('menu_type', '未分类'))))
            if not cat:
                cat = '未分类'
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            output_lines.append(f"  {cat}: {count} 道")
        
        output_lines.append(f"")
        output_lines.append(f"总计: {len(menu_items)} 道菜")
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("【使用说明】")
        output_lines.append("=" * 80)
        output_lines.append("这是食堂系统的菜单知识库。")
        output_lines.append("当用户询问菜品信息时，请基于以上知识库内容回答。")
        output_lines.append("回答时请确保：")
        output_lines.append("1. 只提供知识库中有的菜品信息")
        output_lines.append("2. 价格信息准确")
        output_lines.append("3. 分类信息清晰")
        output_lines.append("4. 用友好的语言回答")
        output_lines.append("=" * 80)
        
        # 输出到文件
        output_content = "\n".join(output_lines)
        
        output_file = r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\canteen_menu_knowledge_base.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(output_content)
        print(f"\n\n✅ 知识库内容已保存到: {output_file}")
        print(f"   共 {len(output_lines)} 行文字")
        print(f"   请将此文件内容复制到扣子平台的知识库中")
        
        break

asyncio.run(get_menu_data())

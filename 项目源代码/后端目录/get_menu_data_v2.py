import sys
import os

os.chdir(r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')
sys.path.insert(0, r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')

from sqlalchemy import text
from config.get_db import get_db
import asyncio

async def get_menu_data():
    print("=" * 80)
    print("📋 食堂菜单知识库 - 正在读取数据库")
    print("=" * 80)
    
    async for db in get_db():
        # 读取所有菜品数据（使用正确的列名）
        result = await db.execute(text("SELECT * FROM canteen_menu ORDER BY menu_id"))
        menu_items = result.fetchall()
        
        print(f"\n✅ 共找到 {len(menu_items)} 道菜")
        
        # 整理成知识库格式
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("【食堂菜单知识库】")
        output_lines.append("=" * 80)
        output_lines.append("")
        output_lines.append(f"本菜单共收录 {len(menu_items)} 道菜品。")
        output_lines.append("包含菜品名称、价格、分类、描述等信息。")
        output_lines.append("")
        output_lines.append("=" * 80)
        
        # 分类统计
        category_stats = {}
        
        for idx, item in enumerate(menu_items, 1):
            menu_id = item[0]
            menu_name = item[1] if item[1] else '未命名'
            menu_type = item[2] if item[2] else '其他'
            price = item[3] if item[3] else 0
            image_url = item[4] if item[4] else ''
            description = item[5] if item[5] else ''
            status = item[6] if item[6] else '0'
            sort_order = item[7] if item[7] else 0
            remark = item[12] if len(item) > 12 and item[12] else ''
            
            # 统计分类
            category_stats[menu_type] = category_stats.get(menu_type, 0) + 1
            
            # 状态描述
            status_text = '上架' if status == '0' else '下架'
            
            output_lines.append("")
            output_lines.append(f"【第 {idx} 道】 {menu_name}")
            output_lines.append(f"  菜名: {menu_name}")
            output_lines.append(f"  价格: ¥{price}")
            output_lines.append(f"  分类: {menu_type}")
            
            if description:
                output_lines.append(f"  描述: {description}")
            
            if remark:
                output_lines.append(f"  备注: {remark}")
            
            output_lines.append(f"  状态: {status_text}")
            output_lines.append(f"  编号: {menu_id}")
        
        # 添加分类统计
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("【菜品分类统计】")
        output_lines.append("-" * 80)
        
        for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
            output_lines.append(f"  {cat}: {count} 道")
        
        output_lines.append(f"")
        output_lines.append(f"  总计: {len(menu_items)} 道")
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("【使用说明】")
        output_lines.append("=" * 80)
        output_lines.append("这是食堂系统的菜单知识库。")
        output_lines.append("当用户询问菜品信息时，请严格基于以上知识库内容回答。")
        output_lines.append("")
        output_lines.append("回答规则:")
        output_lines.append("1. 只提供知识库中有的菜品信息")
        output_lines.append("2. 价格信息要准确，使用人民币格式（¥价格）")
        output_lines.append("3. 分类信息要清晰")
        output_lines.append("4. 如果知识库中没有相关信息，请诚实告知")
        output_lines.append("5. 用友好、简洁的语言回答")
        output_lines.append("6. 推荐菜品时可参考菜品描述和备注")
        output_lines.append("7. 标注菜品的上下架状态")
        output_lines.append("")
        output_lines.append("常见问题回答模板:")
        output_lines.append("Q: 有什么菜推荐？")
        output_lines.append("A: 根据知识库中的菜品信息，推荐以下分类的菜品...")
        output_lines.append("")
        output_lines.append("Q: 红烧肉多少钱？")
        output_lines.append("A: 根据知识库，红烧肉的价格是...")
        output_lines.append("")
        output_lines.append("Q: 有什么素菜？")
        output_lines.append("A: 根据知识库中的分类信息...")
        output_lines.append("=" * 80)
        
        # 输出到控制台
        print("\n" + "=" * 80)
        print("📝 知识库内容")
        print("=" * 80)
        print("")
        output_content = "\n".join(output_lines)
        print(output_content)
        
        # 保存到文件
        output_file = r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\canteen_menu_knowledge_base.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n\n{'=' * 80}")
        print(f"✅ 知识库内容已保存到: {output_file}")
        print(f"   共 {len(output_lines)} 行文字")
        print(f"{'=' * 80}")
        print("")
        print("📌 使用方法:")
        print("   方式一（推荐）: 直接复制下面的内容到扣子平台的知识库")
        print("   方式二: 打开文件复制完整内容")
        print(f"   文件位置: {output_file}")
        print("")
        print("📌 在扣子平台添加知识库的步骤:")
        print("   1. 登录 https://www.coze.cn")
        print("   2. 进入你的智能体编辑页面")
        print("   3. 左侧导航找到 '知识库' 或 'Knowledge Base'")
        print("   4. 点击 '添加' 或 'Add'")
        print("   5. 选择文本粘贴方式，或上传txt文件")
        print("   6. 粘贴以下内容，或上传生成的文件")
        print("   7. 保存后，智能体就能基于菜单信息回答问题了")
        print(f"{'=' * 80}")
        
        break

asyncio.run(get_menu_data())

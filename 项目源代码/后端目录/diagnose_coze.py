"""
诊断脚本：检查配置读取和扣子API响应
"""
import sys
import os

os.chdir(r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')
sys.path.insert(0, r'E:\刘柏霆\RuoYi-Vue3-FastAPI-master\ruoyi-fastapi-backend')

import asyncio
import json
import httpx
from config.env import AppConfig


async def diagnose():
    print("=" * 80)
    print("🔍 扣子智能体诊断测试")
    print("=" * 80)

    # 1. 检查配置读取
    print("\n【1/3】检查配置读取...")
    api_key = AppConfig.coze_api_key
    bot_id = AppConfig.coze_canteen_bot_id

    print(f"   API Key 长度: {len(api_key)} 字符")
    if api_key:
        print(f"   ✅ API Key: {api_key[:20]}...")
    else:
        print(f"   ❌ API Key: 空")

    print(f"   Bot ID 值: '{bot_id}'")
    if bot_id:
        print(f"   ✅ Bot ID: {bot_id}")
    else:
        print(f"   ❌ Bot ID: 空")

    if not api_key or not bot_id:
        print("\n   ⚠️ 配置不完整，无法调用扣子API")
        return

    # 2. 测试API连接
    print("\n【2/3】测试扣子API连接和响应格式...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    test_payload = {
        "bot_id": bot_id,
        "user_id": "test_user_001",
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": "你好！请简单介绍一下你自己。",
                "content_type": "text",
            }
        ],
    }

    print(f"   请求URL: https://api.coze.cn/v3/chat")
    print(f"   Bot ID: {bot_id}")
    print(f"   正在发送请求...")

    try:
        timeout = httpx.Timeout(120.0, connect=30.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                "https://api.coze.cn/v3/chat",
                headers=headers,
                json=test_payload,
            ) as response:
                print(f"   ✅ HTTP状态码: {response.status_code}")

                if response.status_code != 200:
                    error_content = await response.aread()
                    print(f"   ❌ 错误内容: {error_content}")
                    return

                # 3. 分析响应格式
                print("\n【3/3】分析响应格式...")
                print("-" * 80)

                line_count = 0
                event_count = 0
                data_count = 0
                content_found = False
                full_response = ""
                raw_lines = []

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    line_count += 1
                    raw_lines.append(line)

                    # 记录前30行原始数据用于调试
                    if line_count <= 30:
                        preview = line[:120] + "..." if len(line) > 120 else line
                        print(f"   行{line_count:2d}: {preview}")

                    # 分析事件类型
                    if line.startswith("event:"):
                        event_count += 1
                        event_type = line[6:].strip()
                        print(f"   📢 事件: {event_type}")

                    # 分析数据
                    elif line.startswith("data:"):
                        data_count += 1
                        data_str = line[5:].strip()

                        try:
                            data = json.loads(data_str)
                            # 尝试提取内容
                            if isinstance(data, dict):
                                content = None
                                if "content" in data and isinstance(data["content"], str):
                                    content = data["content"]
                                elif "data" in data and isinstance(data["data"], dict) and "content" in data["data"]:
                                    content = data["data"]["content"]
                                elif "messages" in data and isinstance(data["messages"], list):
                                    for msg in data["messages"]:
                                        if isinstance(msg, dict) and msg.get("type") in ["answer", "text"] and msg.get("content"):
                                            content = msg["content"]
                                            break
                                elif "answer" in data:
                                    content = data["answer"]

                                if content:
                                    content_found = True
                                    full_response += content
                                    if len(full_response) < 300:
                                        print(f"   💬 内容: {content[:80]}")

                        except json.JSONDecodeError:
                            if len(data_str) > 2 and not data_str.startswith("{"):
                                content_found = True
                                full_response += data_str
                                if len(full_response) < 300:
                                    print(f"   💬 文本: {data_str[:80]}")

                print("-" * 80)
                print(f"\n📊 分析结果:")
                print(f"   总行数: {line_count}")
                print(f"   事件数: {event_count}")
                print(f"   数据块: {data_count}")
                print(f"   是否找到内容: {'✅ 是' if content_found else '❌ 否'}")
                print(f"   完整回答长度: {len(full_response)} 字符")

                if full_response:
                    print(f"\n📝 智能体回答预览:")
                    print("-" * 80)
                    print(full_response[:600])
                    if len(full_response) > 600:
                        print("...")
                    print("-" * 80)

                print("\n" + "=" * 80)
                print("🎉 API连接和响应分析完成！")
                print("=" * 80)

                if content_found:
                    print("\n✅ 结论: 扣子API工作正常，可以获取到智能体回答")
                    print("   现在需要修改后端服务的解析逻辑")
                else:
                    print("\n⚠️ 结论: API调用成功，但未能正确解析出回答内容")
                    print("   需要调整响应解析逻辑以匹配实际的响应格式")

                print(f"\n💡 原始响应行数: {len(raw_lines)} 行，已展示前30行")
                print("=" * 80)

    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(diagnose())

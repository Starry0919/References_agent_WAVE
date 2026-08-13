#!/usr/bin/env python3
"""POE API Key 测试脚本"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv(Path(__file__).resolve().parent / "poe-api.env")

API_KEY = os.environ.get("POE_API_KEY")
BASE_URL = "https://api.poe.com/v1"

if not API_KEY:
    print("❌ POE_API_KEY 未设置。请在 poe-api.env 中配置，或导出环境变量后重试。")
    sys.exit(1)

def test_models():
    """测试 1: 列出可用模型"""
    print("=" * 50)
    print("测试 1: 获取模型列表 (GET /v1/models)")
    print("=" * 50)
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        models = client.models.list()
        print(f"✅ 连接成功！共获取到 {len(models.data)} 个模型:\n")
        for m in models.data[:10]:
            print(f"  - {m.id}")
        if len(models.data) > 10:
            print(f"  ... 还有 {len(models.data)-10} 个模型")
        return True
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}: {e}")
        return False

def test_chat():
    """测试 2: 简单对话"""
    print("\n" + "=" * 50)
    print("测试 2: 对话补全 (POST /v1/chat/completions)")
    print("=" * 50)
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        response = client.chat.completions.create(
            model="GPT-4o-Mini",  # 使用一个常见且便宜的模型测试
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'POE API is working!' in English, nothing else."}
            ],
            max_tokens=50,
            temperature=0.0,
        )
        content = response.choices[0].message.content
        print(f"✅ 对话成功！模型返回:\n")
        print(f"   '{content}'")
        print(f"\n   用量统计:")
        print(f"   - prompt_tokens: {response.usage.prompt_tokens}")
        print(f"   - completion_tokens: {response.usage.completion_tokens}")
        print(f"   - total_tokens: {response.usage.total_tokens}")
        return True
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    ok1 = test_models()
    ok2 = test_chat()

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"  模型列表: {'✅ 通过' if ok1 else '❌ 失败'}")
    print(f"  对话测试: {'✅ 通过' if ok2 else '❌ 失败'}")
    sys.exit(0 if (ok1 and ok2) else 1)

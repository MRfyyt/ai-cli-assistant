"""
LLM API 5 大核心概念 —— 一次性跑通
=====================================
跑法: python src/01_llm_concepts_demo.py

这个文件不是项目代码，是你的"概念实验台"。
每段代码都独立可运行，一个个跑，跑完你就全懂了。
"""

import sys
import os

# 修复 Windows Git Bash 中文乱码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载 API Key

# ============================================================
# 概念 1: Token —— 文本怎么被"切碎"
# ============================================================
print("=" * 60)
print("概念 1: TOKEN —— 文本的计价单位")
print("=" * 60)

# 先直观感受: 用 tiktoken 看看一段文本有多少 Token
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")  # GPT-4/3.5 用的编码

texts = [
    "Hello, world!",
    "我喜欢吃苹果",
    "The quick brown fox jumps over the lazy dog",
]
for t in texts:
    tokens = enc.encode(t)
    print(f"  '{t}'")
    print(f"    → {len(tokens)} tokens: {tokens}")
    print()

# 你只需要记住: 中文约 1-2 字/token, 英文约 0.75 词/token
# API 按 input + output token 总量计费

print("\n▶ 概念 2: CONTEXT WINDOW"); print("-" * 40)

# ============================================================
# 概念 2: Context Window —— 模型一次能"看"多少
# ============================================================
print("\n" + "=" * 60)
print("概念 2: CONTEXT WINDOW —— 模型的'工作记忆'上限")
print("=" * 60)

# 不同的模型有不同的上下文窗口
models_info = {
    "GPT-4o": 128_000,
    "GPT-4o-mini": 128_000,
    "Claude 3.5 Sonnet": 200_000,
    "GPT-3.5-turbo": 16_385,
}

for model, window in models_info.items():
    pages = window / 750  # 约 750 tokens/页英文
    print(f"  {model:<22s}: {window:>8,} tokens  (约 {pages:.0f} 页英文)")

print()
print("  ⚠ 对话越长 → 历史消息占的 context 越多 → 留给回复的空间越少")
print("  ⚠ 超出 context window → API 报错，或模型'失忆'")

print("\n▶ 概念 3: TEMPERATURE / TOP-P"); print("-" * 40)

# ============================================================
# 概念 3: Temperature / Top-P —— 控制输出的"随机程度"
# ============================================================
print("\n" + "=" * 60)
print("概念 3: TEMPERATURE / TOP-P —— 确定性 vs 创造性")
print("=" * 60)

print("""
  Temperature 指南:
    0.0 ~ 0.2  →  代码生成 / 数学 / 需要精确答案
    0.3 ~ 0.7  →  日常问答 / 文案 / 翻译
    0.8 ~ 1.5  →  创意写作 / 头脑风暴 / 希望每次不同

  Top-P 通常设 0.9~1.0，和 Temperature 二选一调就行。
  新手建议: 只调 Temperature，Top-P 保持默认。
""")

# 用伪代码演示效果 (不实际调 API, 省 token)
import random

prompt = "用一句话形容夕阳"

print(f"  Prompt: '{prompt}'")
print()
print("  如果 Temperature = 0.1 (几乎确定):")
for _ in range(3):
    print(f"    → 夕阳西下，天空被染成了橙红色。")  # 几乎每次一样
print()
print("  如果 Temperature = 1.2 (很有创意):")
creative = [
    "    → 太阳把自己灌醉，跌进了地平线的酒杯里。",
    "    → 天空在做最后的燃烧，像一个不愿谢幕的演员。",
    "    → 黄昏把整个世界调成了暖色滤镜。",
]
for c in creative:
    print(c)

print("\n▶ 概念 4: SYSTEM PROMPT"); print("-" * 40)

# ============================================================
# 概念 4: System Prompt —— 设定模型的"人设"
# ============================================================
print("\n" + "=" * 60)
print("概念 4: SYSTEM PROMPT —— 看不见的导演")
print("=" * 60)

print("""
  消息结构 (从模型视角):
  ┌──────────────────────────────────┐
  │ System:  "你是苏格拉底。"         │ ← 只发一次, 设定角色和规则
  │                                    │    用户看不到这层
  ├──────────────────────────────────┤
  │ User:    "什么是幸福？"            │ ← 用户每次输入
  ├──────────────────────────────────┤
  │ Assistant: "孩子，让我用提问来..." │ ← 模型回复
  └──────────────────────────────────┘

  好的 System Prompt 示例 (对比):
""")

bad_prompt = "你是一个助手"
good_prompt = """你是一个 Python 代码审查专家。你的回答必须:
1. 先指出最严重的问题
2. 给出修改后的代码
3. 解释为什么这样改
用中文回答。"""

print(f"  ❌ 差的: '{bad_prompt}'")
print(f"  ✅ 好的: '''{good_prompt}'''")
print()
print("  💡 System Prompt 是 Prompt Engineer 最重要的技能之一")

print("\n▶ 概念 5: FUNCTION CALLING / TOOL USE"); print("-" * 40)

# ============================================================
# 概念 5: Function Calling / Tool Use —— LLM 的"手"
# ============================================================
print("\n" + "=" * 60)
print("概念 5: FUNCTION CALLING —— 让模型能'做事'")
print("=" * 60)

print("""
  没有 Tool Use:  LLM 只能"说"
  有了 Tool Use:  LLM 可以"做" —— 查天气、搜网页、调 API、运行代码

  执行流程:
    用户: "北京今天几度？"
      → LLM: 我有个 get_weather 工具可以用
      → LLM 返回: { "function": "get_weather", "arguments": {"city": "北京"} }
      → 你的代码: 真的去查天气 API  (← 你写这步)
      → 把结果 "北京 22°C 晴" 发回 LLM
      → LLM: "北京今天 22°C，晴天，适合出行~"
""")

# 演示: 用 Pydantic 定义一个工具 schema (Week 3 重度用)
from pydantic import BaseModel, Field


class GetWeatherArgs(BaseModel):
    """这个 Model 就是告诉 LLM '我的工具长这样'"""
    city: str = Field(description="城市名，如 '北京'")
    unit: str = Field(default="celsius", description="温度单位: celsius 或 fahrenheit")


print("  工具定义示例 (Pydantic Model):")
print(f"  {GetWeatherArgs.model_json_schema()}")
print()
print("  💡 Week 3 的 Agent 项目就是在这个基础上扩展的")
print("  💡 这是 AI 应用工程师和普通 API 调用者的分水岭")

print("\n▶ 实战: 调用 DeepSeek API"); print("-" * 40)

# ============================================================
# 实战: 用 DeepSeek 做一次真实的 API 调用
# ============================================================
import json
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY", "")
if api_key and api_key != "sk-your-deepseek-key-here":
    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    print(f"\n  模型: {model}")
    print(f"  Base URL: {os.getenv('DEEPSEEK_BASE_URL')}")
    print()
    print("  > 发送请求: 用一句话介绍深度学习 (streaming 模式)")
    print()

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个简洁的AI科普助手，回答不超过3句话。"},
            {"role": "user", "content": "用一句话介绍深度学习"},
        ],
        temperature=0.5,
        max_tokens=200,
        stream=True,  # ← 流式输出, 打字机效果
    )

    print("  🗨️  回复: ", end="", flush=True)
    total_tokens = 0
    for chunk in stream:
        if chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            print(text, end="", flush=True)
            total_tokens += len(text)
    print()
    print(f"\n  📊 输出约 {total_tokens} 字符")

    # 非流式调用 + token 统计
    print("\n  > 对比: 同一条消息, 非流式调用 (一次性返回)")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个简洁的AI科普助手，回答不超过3句话。"},
            {"role": "user", "content": "用一句话介绍深度学习"},
        ],
        temperature=0.5,
        max_tokens=200,
        stream=False,
    )
    print(f"  🗨️  回复: {response.choices[0].message.content}")
    print(f"  📊 Token 用量: input={response.usage.prompt_tokens}, output={response.usage.completion_tokens}, total={response.usage.total_tokens}")

    print("\n" + "=" * 60)
    print("🎉 所有概念过完 + 第一次真实 API 调用成功！")
    print("=" * 60)
else:
    print("\n  ⚠️  未检测到 DeepSeek API Key")
    print("  请在 .env 文件中填写 DEEPSEEK_API_KEY= 后面换成你的真实 Key")
    print("  然后重新运行: python src/01_llm_concepts_demo.py")
    print()
    print("  .env 文件位置: C:\\Users\\23307\\Projects\\ai-cli-assistant\\.env")

print()
print("下一步: 用这些概念写项目 1 —— 命令行 AI 助手")

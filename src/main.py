# ============================================================
# main.py — CLI 交互主入口
# ============================================================
# 职责: 命令行交互循环——读用户输入 → 调 chat.py → 打印回复。
# 依赖: config.py（配置）、chat.py（对话会话）、utils.py（TokenCounter）
# 项目架构: main.py → chat.py → config.py + utils.py（顶层 → 底层）
# ============================================================

from config import load_config
from chat import ChatSession
from utils import TokenCounter

# ---- 初始化 ----
config = load_config()

session = ChatSession(config)
session.set_system_prompt("你是一个友好的AI助手,用中文回答,回答简洁。")

print("=" * 40)
print("🤖 AI CLI Assistant — 输入 /help 查看命令，/quit 退出")
print("=" * 40)

# ---- 主循环: 等用户输入 → 处理命令/对话 → 打印回复 ----
while True:
    user_input = input("\n你> ").strip()

    # 空输入（直接按回车）→ 跳过
    if not user_input:
        continue

    # /quit → 退出循环，程序结束
    if user_input == "/quit":
        print("👋 再见！")
        break

    # /clear → 清空对话历史，只保留 System Prompt（messages[0]）
    if user_input == "/clear":
        session.messages = session.messages[:1]  # 只保留 System Prompt（第 0 条）
        print("🧹 对话已清空")
        continue

    # /token → 估算 Token 用量（DeepSeek 流式模式不返回 usage 时用字符数 × 1.5 估算）
    if user_input == "/token":
        total_chars = sum(len(m["content"]) for m in session.messages)
        est_tokens = int(total_chars * 1.5)  # 粗略估算：1个中文字 ≈ 1.5 token
        print(f"📊 消息数: {len(session.messages)} | 估算 Token: ~{est_tokens} | 上下文占用: ~{est_tokens/128000*100:.1f}%")
        continue

    # /save → 保存对话历史到 JSON 文件
    if user_input == "/save":
        import json
        from datetime import datetime

        filename = datetime.now().strftime("history_%Y%m%d_%H%M%S.json")
        data = {
            "saved_at": datetime.now().isoformat(),
            "messages": session.messages,
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到 {filename}")
        continue


    # /help → 显示命令列表
    if user_input == "/help":
        print("""
命令列表:
  /help   - 显示帮助
  /clear  - 清空对话
  /token  - Token 用量统计
  /save   - 保存对话
  /quit   - 退出
""")
        continue

    # ---- 不是命令 → 当作对话发给 AI ----
    print("/AI> ",end = "")
    session.send_streaming(user_input)      # 流式输出，打字机效果

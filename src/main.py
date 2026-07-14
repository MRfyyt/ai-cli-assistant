from config import load_config
from chat import ChatSession
from utils import TokenCounter

config = load_config()

session = ChatSession(config)
session.set_system_prompt("你是一个友好的AI助手,用中文回答,回答简洁。")

print("=" * 40)
print("🤖 AI CLI Assistant — 输入 /help 查看命令，/quit 退出")
print("=" * 40)

while True:
    user_input = input("\n你> ").strip()

    if not user_input:
        continue

    if user_input == "/quit":
        print("👋 再见！")
        break

    if user_input == "/clear":
        session.messages = session.messages[:1]  # 只保留 System Prompt（第 0 条）
        print("🧹 对话已清空")
        continue

    if user_input == "/token":
        total_chars = sum(len(m["content"]) for m in session.messages)
        est_tokens = int(total_chars * 1.5)  # 粗略估算：1个中文字 ≈ 1.5 token
        print(f"📊 消息数: {len(session.messages)} | 估算 Token: ~{est_tokens} | 上下文占用: ~{est_tokens/128000*100:.1f}%")
        continue

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

    print("/AI> ",end = "")
    session.send_streaming(user_input)

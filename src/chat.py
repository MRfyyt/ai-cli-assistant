# ============================================================
# chat.py — 对话核心模块
# ============================================================
# 职责: 封装 DeepSeek API 调用，管理多轮对话的消息历史。
# 依赖: config.py（配置）、utils.py（@retry 装饰器）
# 工程技能: OpenAI SDK 流式/非流式调用、消息历史管理、@retry 实际应用
# ============================================================

from openai import OpenAI
from config import load_config
from utils import retry

# 模块加载时即读取配置（全局单例）
config = load_config()

class ChatSession:
    """管理一次完整的对话会话。
    - 维护 messages 列表（System Prompt + 用户/助手消息）
    - 提供 send()（一次性返回）和 send_streaming()（打字机效果）"""

    def __init__(self,config):
        self.config = config
        # 创建 OpenAI 客户端——虽然叫 OpenAI，但 base_url 指向 DeepSeek
        self.client = OpenAI(
            api_key = config.api_key,
            base_url = config.base_url,
        )
        self.messages = []          # 对话历史，每个元素是 {"role": ..., "content": ...}

    def set_system_prompt(self,prompt:str):
        """设置 System Prompt（对话开始时调用一次）。
        System Prompt 放在 messages 最前面，role="system" 告诉模型'你是谁、怎么回答'。"""
        self.messages = [{"role":"system","content":prompt}]

    # ---- 非流式: 一次性获取完整回复 ----
    @retry(max_attempts = 3,delay = 1.0)   # API 调用失败自动重试
    def send(self,user_input: str) -> str:
        """发送消息，等待完整回复后返回。"""

        # 1. 追加用户消息
        self.messages.append({"role":"user","content":user_input})

        # 2. 调用 API（非流式）
        response = self.client.chat.completions.create(
            model = self.config.model,
            messages = self.messages,       # 把整个对话历史发过去
            temperature = self.config.temperature,
            max_tokens = self.config.max_tokens,
            stream = False,                 # ← 关键: False = 等完整回复
        )

        # 3. 取回复文本
        reply = response.choices[0].message.content

        # 4. 追加助手消息（下一轮对话 LLM 能看到"我上次回答了什么"）
        self.messages.append({"role":"assistant","content":reply})

        return reply

    # ---- 流式: 打字机效果逐字打印 ----
    @retry(max_attempts = 3,delay = 1.0)
    def send_streaming(self,user_input : str) ->str:
        """发送消息，逐 chunk 打印回复（打字机效果）。"""

        # 1. 追加用户消息
        self.messages.append({"role":"user","content":user_input})

        # 2. 调用 API（流式）
        stream = self.client.chat.completions.create(
            model = self.config.model,
            messages = self.messages,
            temperature = self.config.temperature,
            max_tokens = self.config.max_tokens,
            stream = True,                  # ← 关键: True = 一段一段返回
        )

        # 3. 逐 chunk 接收并打印
        full_reply = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:          # 有的 chunk 不含内容（元数据）
                text = chunk.choices[0].delta.content   # 取这一小段的文字
                full_reply += text                      # 拼到完整回复里
                print(text,end = "",flush = True)       # 打印不换行，立刻显示
        print()                          # 流式结束补一个换行

        # 4. 追加完整助手消息
        self.messages.append({"role":"assistant","content":full_reply})
        return full_reply


# ---- 自检: 流式对话测试 ----
if __name__ == "__main__":
    session = ChatSession(config)
    session.set_system_prompt("你是一个友好的助手，用中文回答。")
    reply = session.send_streaming("你好，用一句话介绍你自己")
    print("AI:", reply)

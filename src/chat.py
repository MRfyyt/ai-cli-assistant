from openai import OpenAI
from config import load_config
from utils import retry

config = load_config()

class ChatSession:
    def __init__(self,config):
        self.config = config
        self.client = OpenAI(
            api_key = config.api_key,
            base_url = config.base_url,
        )
        self.messages = []

    def set_system_prompt(self,prompt:str):
        self.messages = [{"role":"system","content":prompt}]

    @retry(max_attempts = 3,delay = 1.0)
    def send(self,user_input: str) -> str:
        self.messages.append({"role":"user","content":user_input})

        response = self.client.chat.completions.create(
            model = self.config.model,
            messages = self.messages,
            temperature = self.config.temperature,
            max_tokens = self.config.max_tokens,
            stream = False,
        )

        reply = response.choices[0].message.content

        self.messages.append({"role":"assistant","content":reply})

        return reply
    
    @retry(max_attempts = 3,delay = 1.0)
    def send_streaming(self,user_input : str) ->str:
        self.messages.append({"role":"user","content":user_input})

        stream = self.client.chat.completions.create(
            model = self.config.model,
            messages = self.messages,
            temperature = self.config.temperature,
            max_tokens = self.config.max_tokens,
            stream = True,
        )

        full_reply = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_reply += text
                print(text,end = "",flush = True)
        print()

        self.messages.append({"role":"assistant","content":full_reply})
        return full_reply


if __name__ == "__main__":
    session = ChatSession(config)
    session.set_system_prompt("你是一个友好的助手，用中文回答。")
    reply = session.send_streaming("你好，用一句话介绍你自己")
    print("AI:", reply)

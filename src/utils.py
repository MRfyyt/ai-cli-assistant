import time
import functools
import random

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args,**kwargs)
                except Exception as e:
                    attempts +=1
                    if attempts < max_attempts:
                        time.sleep(delay * (2 ** (attempts - 1)))
                    else:
                        raise e
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1.0)
def call_api():
        if random.random() < 0.7:
            raise ConnectionError("网络超时")
        return "调用成功！"

class TokenCounter:
    def __init__(self,label:str = ""):
        self.label = label
        self.start_time = 0.0
        self.input_tokens =0
        self.output_tokens = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self

    def record_token(self,input_tokens : int ,output_tokens : int):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
    def __exit__(self,exc_type,exc_val,exc_tb):
        elapsed = time.time() - self.start_time
        total_token = self.input_tokens + self.output_tokens
        prefix = f"[{self.label}] " if self.label else ""
        print(f"  📊 {prefix}Token: in={self.input_tokens} out={self.output_tokens} total_tokens={total_token} | 耗时 {elapsed:.1f}s")


if __name__ == "__main__":
    @retry(max_attempts=3, delay=1.0)
    def call_api():
        if random.random() < 0.7:
            raise ConnectionError("网络超时")
        return "调用成功！"

    print(call_api())

    with TokenCounter("测试") as tc:
        time.sleep(2)
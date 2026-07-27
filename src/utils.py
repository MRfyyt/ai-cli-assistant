# ============================================================
# utils.py — 工具函数集
# ============================================================
# 职责: 提供可复用的工程工具——装饰器、上下文管理器。
# 依赖: 不依赖任何本项目的其他文件（最底层模块）。
# 工程技能: 装饰器（带参数的三层结构）、上下文管理器（__enter__/__exit__）
# ============================================================

import time
import functools
import random

# ============================================================
# 1. @retry 装饰器 —— API 调用失败自动重试
# ============================================================
# 三层结构（带参数的装饰器）:
#   retry(max_attempts, delay)  →  返回 decorator
#   decorator(func)             →  返回 wrapper
#   wrapper(*args, **kwargs)    →  真正执行 + 重试逻辑
#
# 指数退避: 第1次等 delay 秒 → 第2次等 delay*2 秒 → 第3次等 delay*4 秒

def retry(max_attempts=3, delay=1.0):
    """装饰器工厂: 返回一个装饰器，被装饰的函数抛异常时自动重试。
    用法: @retry(max_attempts=3, delay=1.0)"""

    # ---- 第2层: 接收被装饰的函数 ----
    def decorator(func):
        @functools.wraps(func)  # 保留原函数的 __name__ 和 __doc__
        # ---- 第3层: 真正干活的 wrapper ----
        def wrapper(*args,**kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args,**kwargs)        # 尝试执行原函数
                except Exception as e:
                    attempts +=1
                    if attempts < max_attempts:
                        # 指数退避: 1s → 2s → 4s → ...
                        time.sleep(delay * (2 ** (attempts - 1)))
                    else:
                        raise e                      # 最后一次也失败 → 抛出
        return wrapper
    return decorator

# ---- 测试: 模拟一个 70% 概率失败的 API 调用 ----
@retry(max_attempts=3, delay=1.0)
def call_api():
        if random.random() < 0.7:
            raise ConnectionError("网络超时")
        return "调用成功！"

# ============================================================
# 2. TokenCounter 上下文管理器 —— 自动统计 Token 用量
# ============================================================
# 用法:
#   with TokenCounter("流式") as tc:
#       tc.record_token(in_tokens, out_tokens)
#   # 退出 with 块时自动打印用量和耗时

class TokenCounter:
    """进入 with 块时开始计时，退出时打印 Token 用量和耗时。"""

    def __init__(self,label:str = ""):
        self.label = label
        self.start_time = 0.0
        self.input_tokens =0
        self.output_tokens = 0

    def __enter__(self):
        """进入 with 块: 记录开始时间，返回自身供 as 绑定。"""
        self.start_time = time.time()
        return self

    def record_token(self,input_tokens : int ,output_tokens : int):
        """累计 Token 用量（可在 with 块内多次调用）。"""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def __exit__(self,exc_type,exc_val,exc_tb):
        """退出 with 块: 自动计算耗时并打印统计。
        无论 with 块内是否抛异常，该方法都会执行。
        返回 None（或 False）= 不抑制异常，让它继续传播。"""
        elapsed = time.time() - self.start_time
        total_token = self.input_tokens + self.output_tokens
        prefix = f"[{self.label}] " if self.label else ""
        print(f"  📊 {prefix}Token: in={self.input_tokens} out={self.output_tokens} total_tokens={total_token} | 耗时 {elapsed:.1f}s")


# ---- 自检 ----
if __name__ == "__main__":
    @retry(max_attempts=3, delay=1.0)
    def call_api():
        if random.random() < 0.7:
            raise ConnectionError("网络超时")
        return "调用成功！"

    print(call_api())

    with TokenCounter("测试") as tc:
        time.sleep(2)

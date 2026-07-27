# ============================================================
# config.py — 配置管理模块
# ============================================================
# 职责: 从 .env 文件读取 DeepSeek API 配置，用 Pydantic 校验。
# 依赖: 被 chat.py 和 main.py import，不依赖任何本项目的其他文件。
# 工程技能: Pydantic BaseModel + field_validator（类型校验 + 自定义验证）
# ============================================================

import os
from pydantic import BaseModel,field_validator
from dotenv import load_dotenv

# 把 .env 里的变量注入到 os.environ（DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL 等）
load_dotenv()  # 把 .env 里的变量注入到 os.environ

class LLMConfig(BaseModel):
    """LLM 连接配置。
    Pydantic BaseModel 会在创建实例时自动校验每个字段的类型。
    如果 .env 里填了字符串给 max_tokens，Pydantic 会尝试转 int——转不了就报错。"""

    # ---- 必填字段（没有默认值，不传就报错） ----
    api_key : str         # DeepSeek API Key，形如 sk-d56769...
    base_url : str        # API 地址，默认 https://api.deepseek.com

    # ---- 可选字段（有默认值） ----
    model : str = "deepseek-chat"       # 模型名
    max_tokens : int = 2048             # 单次回复最大 token 数
    temperature : float = 0.7           # 随机性 0~2，越低越确定

    # ---------- 自定义校验 ----------

    @field_validator("api_key")
    @classmethod
    def check_api_key(cls,v:str) -> str :
        """确保 API Key 不是空值或占位符。"""
        if not v or not v.strip():
            raise ValueError("API Key不能为空")
        lower = v.strip().lower()
        if "your-key-here" in lower or "your-api-key" in lower or "sk-your-" in lower :
            raise ValueError("API Key是占位符,请填入真实密钥")
        return v.strip()

    @field_validator("max_tokens")
    @classmethod
    def check_max_tokens(cls, v: int) -> int:
        """确保 max_tokens 是正数。"""
        if v <= 0:
            raise ValueError(f"max_tokens 必须 > 0,当前值: {v}")
        return v

def load_config() -> LLMConfig:
    """从环境变量读取配置，构造并返回一个校验过的 LLMConfig 对象。
    这是本模块的唯一对外接口——外部只需调 load_config() 就能拿到配置。"""

    api_key = os.getenv("DEEPSEEK_API_KEY","").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL","").strip()

    # 提前检查必填项，比 Pydantic 校验给出更友好的中文错误提示
    if not api_key :
        raise ValueError("坏境变量DEEPSEEK_API_KEY未设置,请在.env中配置")
    if not base_url :
        raise ValueError("坏境变量DEEPSEEK_BASE_URL未设置,请在.env中配置")

    return LLMConfig(
        api_key = api_key,
        base_url = base_url,
        model = os.getenv("DEEPSEEK_MODEL","deep-chat"),
        max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS","2048")),
        temperature = float(os.getenv("DEEPSEEK_TEMPERATURE","0.7"))
    )

# ---- 自检：直接运行 config.py 验证配置能否正常加载 ----
if __name__ == "__main__":
    try:
        cfg = load_config()
        print("配置加载成功")
        print(cfg.model_dump())
    except ValueError as e:
        print(f"配置错误：{e}")

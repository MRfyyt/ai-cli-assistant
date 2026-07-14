import os
from pydantic import BaseModel,field_validator
from dotenv import load_dotenv

load_dotenv()  # 把 .env 里的变量注入到 os.environ
class LLMConfig(BaseModel):
    api_key : str
    base_url : str
    model : str = "deepseek-chat"
    max_tokens : int = 2048
    temperature : float = 0.7

    @field_validator("api_key")
    @classmethod
    def check_api_key(cls,v:str) -> str :
        if not v or not v.strip():
            raise ValueError("API Key不能为空")
        lower = v.strip().lower()
        if "your-key-here" in lower or "your-api-key" in lower or "sk-your-" in lower :
            raise ValueError("API Key是占位符,请填入真实密钥")
        return v.strip()
    
    @field_validator("max_tokens")
    @classmethod
    def check_max_tokens(cls, v: int) -> int:
        if v <= 0:
            raise ValueError(f"max_tokens 必须 > 0,当前值: {v}")
        return v

def load_config() -> LLMConfig:
    api_key = os.getenv("DEEPSEEK_API_KEY","").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL","").strip()

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

if __name__ == "__main__":
    try:
        cfg = load_config()
        print("配置加载成功")
        print(cfg.model_dump())
    except ValueError as e:
        print(f"配置错误：{e}")
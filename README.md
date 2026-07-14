# 🤖 AI CLI Assistant

基于 **DeepSeek API** 的命令行 AI 助手，支持流式对话、多轮对话、对话历史管理。

## 功能

- 💬 **流式对话** — 打字机效果实时输出
- 🔄 **多轮对话** — 自动维护上下文，模型记住对话历史
- 📊 **Token 统计** — 估算 Token 用量和上下文窗口占用
- 💾 **对话保存** — 导出对话记录为 JSON 文件
- 🔁 **自动重试** — API 调用失败自动重试，指数退避

## 命令

| 命令 | 功能 |
|------|------|
| `/help` | 显示所有命令 |
| `/clear` | 清空对话历史 |
| `/token` | 显示 Token 用量统计 |
| `/save` | 保存对话到 JSON 文件 |
| `/quit` | 退出程序 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入你的 DeepSeek API Key：

```ini
DEEPSEEK_API_KEY=sk-your-real-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 运行

```bash
python src/main.py
```

## 项目结构

```
ai-cli-assistant/
├── .env.example          # 配置文件模板
├── requirements.txt      # Python 依赖
└── src/
    ├── 01_llm_concepts_demo.py  # LLM 5大概念教学脚本
    ├── config.py                # Pydantic 配置管理
    ├── utils.py                 # @retry 装饰器 + TokenCounter 上下文管理器
    ├── chat.py                  # DeepSeek 对话核心（流式+非流式）
    └── main.py                  # CLI 交互主入口
```

## 技术栈

- **LLM**: DeepSeek API (兼容 OpenAI SDK)
- **配置管理**: Pydantic
- **工程实践**: 装饰器、上下文管理器、流式输出、异常重试

# Week 1 CLI AI 助手 — 深度复盘

> 时间：2026-06-28 — 06-30
> 项目：命令行 AI 助手（基于 DeepSeek API）

---

## 一、做了什么

基于 DeepSeek API，手写了一个命令行 AI 助手。支持流式对话、5 个命令（/help /clear /token /save /quit）、多轮对话、Token 统计。

| 阶段 | 内容 | 耗时 |
|------|------|------|
| 理解概念 | LLM API 5 大概念（Token、Context Window、Temperature、System Prompt、Function Calling） | 2 小时 |
| 搭环境 | Python venv + VS Code + Git + DeepSeek API Key | 1 小时 |
| 写教学脚本 | `01_llm_concepts_demo.py` — 5 大概念一次性跑通 | 1 小时 |
| 写核心代码 | config.py → utils.py → chat.py → main.py | 6 小时 |
| 推 GitHub | git init → remote → push | 30 分钟 |

---

## 二、项目结构

```
ai-cli-assistant/
├── .env                  # DeepSeek API Key（不提交）
├── .gitignore            # 防止 Key 泄露
├── requirements.txt      # openai, pydantic, rich, python-dotenv, tiktoken
└── src/
    ├── 01_llm_concepts_demo.py  # LLM 5大概念教学脚本
    ├── config.py                # Pydantic 配置管理
    ├── utils.py                 # @retry 装饰器 + TokenCounter 上下文管理器
    ├── chat.py                  # ChatSession 类（API 封装 + 流式输出）
    └── main.py                  # CLI 交互循环 + 5 个命令
```

### 依赖关系

```
main.py  →  chat.py  →  config.py
    ↘         ↙
      utils.py

config.py / utils.py: 底层，不依赖任何本项目的其他文件
chat.py: 中间层，依赖 config.py 和 utils.py
main.py: 顶层，依赖 chat.py, config.py, utils.py
```

---

## 三、核心数据流

```
用户输入 "你好"
  │
  ├─ main.py: while True → input("你>")
  ├─ 不是命令 → session.send_streaming("你好")
  │
  ├─ chat.py:
  │   ├─ messages.append({"role": "user", "content": "你好"})
  │   ├─ client.chat.completions.create(
  │   │     model="deepseek-v4-pro",
  │   │     messages=[system, user],
  │   │     stream=True            ← 流式输出
  │   │   )
  │   └─ for chunk in stream:
  │         print(chunk.choices[0].delta.content, end="", flush=True)
  │
  └─ 打印回复 → 等待下一次输入
```

**多轮对话的秘密：** `ChatSession.messages` 列表在每轮不断增长——LLM 能看到之前的所有对话历史，所以能回答"那上海呢？"这种依赖上下文的问题。

---

## 四、学到的工程技能

| 技能 | 文件 | 代码 | 理解了 |
|------|------|------|--------|
| **装饰器（带参数）** | `utils.py` | `@retry(max_attempts=3, delay=1.0)` | 三层结构：retry→decorator→wrapper；`@functools.wraps` 保留原函数信息；指数退避 |
| **Pydantic BaseModel** | `config.py` | `class LLMConfig(BaseModel)` | `BaseModel` 创建时自动校验类型；`field_validator` 自定义校验逻辑；必选/可选字段的区分 |
| **上下文管理器** | `utils.py` | `with TokenCounter("流式") as tc:` | `__enter__` 进入时自动调用；`__exit__` 退出时自动调用（无论是否异常）；`return self` 让 `as` 绑定到实例 |
| **流式输出** | `chat.py` | `for chunk in stream:` | `delta.content`（增量）vs `message.content`（完整）；`flush=True` 强制立即显示 |
| **异常处理** | `utils.py` | `try/except` + 重试循环 | API 会超时/限流/返回格式错误——分级捕获 + 自动重试 |
| **日志** | 全局 | `logging.getLogger("ai-cli")` | 结构化日志：时间 + 级别 + 消息；出错时知道第几步、什么原因 |

---

## 五、关键 Bug

| Bug | 现象 | 原因 | 学到的 |
|-----|------|------|--------|
| **Windows 中文乱码** | 终端打印 `\U0001f916` 报 `UnicodeEncodeError` | Windows Git Bash 默认 GBK 编码 | `sys.stdout.reconfigure(encoding="utf-8")` |
| **DeepSeek 流式不返回 usage** | TokenCounter 显示 `in=0 out=0` | DeepSeek 流式 chunk 不带 usage 字段 | 用字符数 × 1.5 估算或非流式补一次 |
| **API 调用后 messages 里混了对象和 dict** | 第二轮对话报 `ChatCompletionMessage is not subscriptable` | SDK 返回的是对象不是 dict | `msg.model_dump()` 转 dict 后再存 |

---

## 六、技术决策

| 决策 | 原因 |
|------|------|
| 为什么用 OpenAI SDK 调 DeepSeek？ | DeepSeek API 完全兼容 OpenAI 格式，改 `base_url` 即可，不用学新 SDK |
| 为什么不用 requests 直接发 HTTP？ | OpenAI SDK 封装了重试、流式、错误处理，比自己写稳 |
| 为什么 Rich 做美化？ | 终端 Panel/Table/Markdown 渲染，纯 Python 一行安装 |
| 为什么 CLI 不写 Streamlit？ | Week 1 目标是调通 API + 学工程技能，不需要界面分心 |

---

## 七、和后续项目的关系

```
Week 1: CLI AI 助手
  └── client.chat.completions.create(...)
       ├── 被 Week 2 复用 → RAG 的生成环节
       └── 被 Week 3 复用 → Agent 的 ReAct 循环
```

Week 1 打的工程基础（装饰器、Pydantic、上下文管理器、流式）贯穿了整个暑假——Week 3 的 Agent 框架底层用的就是同样的 OpenAI SDK 调用模式。

---

## 八、面试可能追问

| 问题 | 答案 |
|------|------|
| **为什么用 DeepSeek 而不是直接调 OpenAI？** | 国内访问快、价格低、API 格式兼容，不需要改代码 |
| **装饰器的三层结构是什么？** | retry(参数)→decorator(函数)→wrapper(执行+重试)。带参数的装饰器需要多一层 |
| **上下文管理器和 try/finally 有什么区别？** | 语义更清晰、自动管理资源、不会忘记关。TokenCounter 就是利用 __exit__ 自动打印统计 |
| **流式输出的底层原理？** | HTTP SSE（Server-Sent Events），服务器持续推送 chunk。SDK 的 `stream=True` 返回一个迭代器 |
| **如果 DeepSeek 挂了怎么办？** | @retry 自动重试 3 次 + 指数退避。超过 3 次返回错误信息给用户，不崩溃 |

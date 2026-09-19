# Chat API · 带鉴权与多轮对话的流式问答后端

基于 **FastAPI** 的大模型问答后端：**JWT 登录鉴权 + 多轮对话（SQLite 持久化）+ SSE 流式输出**，
并配有**访问日志**与**限流**中间件，以及 pytest 接口测试。

## ✨ 功能

| 功能 | 说明 |
|---|---|
| 🔐 **登录鉴权** | `POST /token` 签发 JWT；`POST /chat` 通过 `Depends(get_current_user)` 校验 `Authorization: Bearer <token>` |
| 💬 **多轮对话** | 服务端按 `conversation_id` 维护历史（默认只取最近 20 条）；**客户端只发本次这一句** |
| ⚡ **流式输出（SSE）** | 模型边生成边推送，实测首字节约 2.3s 可见（非流式需等完整生成） |
| 🗂 **持久化** | SQLite 存对话（`chat_history.db`，已在 `.gitignore` 中） |
| 🧾 **访问日志中间件** | 记录 `方法 路径 状态码 耗时`，并回写 `X-Process-Time` 响应头 |
| 🚦 **限流中间件** | 滑动窗口：每 IP 60 秒最多 5 次，超限返回 **429** |
| ✅ **接口测试** | pytest 5 个用例（含"状态隔离" fixture） |

## 🧰 技术栈

Python 3.12 · FastAPI · Pydantic v2 · SQLite · python-jose（JWT）· passlib + bcrypt · OpenAI SDK（DeepSeek）· pytest

## 📮 接口

| 方法 | 路径 | 鉴权 | 请求格式 | 说明 |
|---|---|---|---|---|
| GET | `/health` | 否 | — | 健康检查 |
| POST | `/token` | 否 | **表单** | 登录，返回 `access_token` |
| POST | `/chat` | ✅ Bearer | **JSON** | 多轮问答，**流式**返回正文 |

### 1) 登录拿 token
```bash
curl -X POST http://127.0.0.1:8000/token \
  -d "username=zhangsan&password=123456"
# -> {"access_token":"eyJhbGciOi...","token_type":"bearer"}
```

### 2) 流式问答
```bash
curl -N -X POST http://127.0.0.1:8000/chat \
  -H "Authorization: Bearer <你的token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"用一句话介绍你自己"}'
```
- 响应头 `Content-Type: text/event-stream`
- 响应头 **`X-Conversation-Id`**：本次会话 id（下次带上它就能"接上"上一轮）
- 响应体：**纯文本流**（一段段返回，不是 JSON）

```python
# Python 侧：第二轮接上第一轮
import requests

token = requests.post("http://127.0.0.1:8000/token",
                      data={"username": "zhangsan", "password": "123456"}
                      ).json()["access_token"]
H = {"Authorization": f"Bearer {token}"}

r = requests.post("http://127.0.0.1:8000/chat", json={"message": "我叫张三"}, headers=H)
cid = r.headers["X-Conversation-Id"]

r2 = requests.post("http://127.0.0.1:8000/chat",
                   json={"conversation_id": cid, "message": "我叫什么？"}, headers=H)
print(r2.text)          # -> 你叫张三。
```

## 🚀 快速开始

```bash
# 1) 安装依赖（本机开发：含测试依赖）
pip install -r requirements-dev.txt

# 2) 配置密钥（.env 不会提交到 git）
#    内容示例：
#    DEEPSEEK_API_KEY=sk-xxxxxx
#    DEEPSEEK_MODEL=deepseek-chat
#    SECRET_KEY=<用 python -c "import secrets;print(secrets.token_urlsafe(48))" 生成>
#    NO_PROXY=api.deepseek.com,127.0.0.1,localhost

# 3) 启动服务
uvicorn app.main:app --reload

# 4) 打开交互式文档
#    http://127.0.0.1:8000/docs

# 5) 跑测试
pytest -v
```

## 📁 项目结构

```
app/
├── main.py              # 组装：include_router + 注册中间件（CORS 最外层）
├── config.py            # 只读配置（.env → 常量）
├── dependencies.py      # get_current_user：验 token
├── middleware/
│   ├── access_log.py    # 访问日志 + X-Process-Time
│   └── rate_limit.py    # 滑动窗口限流（429）
├── models/chat.py       # Pydantic 请求/响应模型
├── routers/
│   ├── auth.py          # POST /token
│   └── chat.py          # POST /chat（流式）
└── services/
    ├── llm.py           # 与大模型通信（含流式版）
    ├── storage.py       # SQLite 存取（save_message / get_history）
    ├── token.py         # JWT 签发
    └── user.py          # 用户校验 + 密码哈希
tests/test_api.py        # pytest 接口测试
```

## 🧠 设计要点（面试可讲）

1. **分层铁律**：`routers` 只接线、`services` 不碰 FastAPI、`config` 只读配置；
   service 用**返回值**表达业务结论，router 用**状态码**表达 HTTP 结论。
2. **流式是"三层接力"**：模型 `yield` 片段 → 生成器转发 → `StreamingResponse` 边取边写网络；
   **任何一层"攒完再交"，流式就断在那一层**。
3. **会话 id 走响应头**：流式响应体被占用了，元信息只能放 header（`X-Conversation-Id`）。
4. **落库时机**：写在**生成器内部、循环之后** —— 路由在 `return` 那刻已结束，且只有流结束才有完整答案。
5. **中间件顺序**：`CORS` 注册在最后 = 最外层 → 连 **429 也带 CORS 头**（否则浏览器会把 429 显示成 CORS 错误）。
6. **测试要隔离状态**：限流的 `_hits` 是模块级全局变量 → 用 `fixture(autouse=True)` 在每个测试前后清空。
7. **上下文控制**：只取最近 N 条（注入 `limit`）+ 按时间正序（SQL 用 `DESC` 取、再 `reverse()`）——因为模型**只"接着最后一条"写**。

## ⚠️ 已知边界（后续改进）

- **限流是单机内存版** → 多进程/多实例部署时需换成 **Redis** 做共享计数；
- **pytest 里 `/chat` 会真调模型** → 生产级测试应 mock 掉 `ask_llm_stream`；
- **SQLite 在部分云平台上不持久** → 部署时需挂持久化磁盘，或换 PostgreSQL。

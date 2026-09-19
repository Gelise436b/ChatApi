"""Chat API 的接口测试（4.3a）

运行方式（在 chatapi 目录下执行）：
    C:\\Users\\27703\\.conda\\envs\\ai_agent\\python.exe -m pytest -v
    加 -s 可以看到 print / 日志的实时输出（pytest 默认会把 stdout 抓走）

三个约定：
  · 名字以 `test_` 开头的函数 = 一个测试用例
  · `assert 条件` 不成立 → 这个用例 FAIL
  · fixture = 每个测试自动执行的"准备/收尾"动作
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.rate_limit import _hits

client = TestClient(app)
# ============ fixture：每个测试前把限流计数清空 ============
# 为什么需要：rate_limit 的 _hits 是【模块级全局变量】，测试之间不会自动清空；
#             累计超过 5 次（60 秒内）就会返回 429，把后面的用例"污染"挂掉。
# autouse=True → 不用手工引用，pytest 会在每个测试前后自动跑它。
@pytest.fixture(autouse=True)
def reset_rate_limit():
    _hits.clear()
    yield
    _hits.clear()

# 1.健康检查
def test_health():
    r = client.get("/health")
    assert r.status_code==200
    assert r.json() == {"status":"OK"}

#2.登陆成功->拿到票
def test_token_ok():
    r = client.post("/token",data = {"username":"zhangsan","password":"123456"})
    assert r.status_code == 200
    assert "access_token" in r.json()

#3. 密码错误->401
def test_token_wrong_password():
    r = client.post("/token",data={"username": "zhangsan", "password": "wrong-password"})
    assert r.status_code == 401

#4. 不带token调chat->401门禁生效
def test_chat_without_token():
    r = client.post("/chat",json = {"message":"你好"})
    assert r.status_code == 401

# 5. 带token调chat ->200+正文费控
def test_chat_with_token():
    token_r = client.post("/token",data={"username": "zhangsan", "password": "123456"})
    token = token_r.json()["access_token"]

    r = client.post(
        "/chat",
        json = {"message":"说一句你好"},
        headers = {"Authorization":f"Bearer {token}"},   # ⚠️❌ 【少了空格】：必须写 f"Bearer {token}" —— 少空格服务器就解析不出票 → 实测这一条 401（其他 4 条全过）
    )

    assert r.status_code == 200
    assert len(r.text)>0
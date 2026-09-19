# 部署清单（4.4 · 国内云服务器）

> **用法**：从上往下做，**每步都有验收标准**，跑通了才进下一步。
> **原则**：**先把 8000 端口跑通，再考虑 Nginx + 80 + 域名** —— 不要一次全上。
> **两个最容易卡住的大坑**：第 6 步的 `--host 0.0.0.0`、第 7 步的**安全组**。

---

## 第 0 步：买服务器（10 分钟）

- **买什么**：阿里云「轻量应用服务器」或 腾讯云「轻量应用服务器」
- **配置**：**2 核 2G 起**；系统选 **Ubuntu 22.04 LTS**
- **省钱**：搜「阿里云 学生认证」/「腾讯云 学生机」—— 通常一年几十块
- **买完你会拿到三样**：**公网 IP**、**用户名**（Ubuntu 镜像一般是 `root` 或 `ubuntu`）、**密码**（或密钥文件）

✅ **验收**：云控制台里能看到实例「运行中」

---

## 第 0.5 步：🔐 服务器安全（没学过网络安全也必做，共 20 分钟）

> **心法**：租服务器不是“进入危险世界”，而是“进入一个 **24 小时被扫描**的世界”。
> 你不需要学网络安全，**只需买上这几把锁**。

### 真实威胁（按概率排，不是按吓人程度）
| # | 威胁 | 真实情况 |
|---|---|---|
| **1** | **SSH 暴力破解** | 扫描器全天扫全网 22 端口试密码，**弱密码几小时内就被攻破** |
| **2** | **被当挖矿肉鸡** | 攻破后装挖矿程序，CPU 跑满 + 你付流量费 |
| **3** | **API key 被刷爆** | `/chat` 被脚本刷 → DeepSeek 账单起飞（真金白银） |
| 4 | 配置泄露 | `.env`（API key / SECRET_KEY）放在哪、权限对不对 |

### 5 个动作（按性价比排）
| 优先 | 动作 | 时间 | 挡什么 |
|---|---|---|---|
| **1** | **DeepSeek 后台设「月度额度上限」** | 2 min | **API key 被刷爆**（止损最关键） |
| **2** | 服务器上的 `SECRET_KEY` **用新生成的**（见第 5 步） | 1 min | token 被伪造 |
| **3** | **SSH 改密钥登录，然后关闭密码登录** | 10 min | **暴力破解（几乎 100% 挡住）** |
| 4 | **安全组只开必要端口**（SSH + 8000） | 2 min | 减少暴露面 |
| 5 | （可选）改 SSH 端口 22→其他 / 装 `fail2ban` | 5 min | 降低扫描噪音 |

#### ⭐ 第 3 步详细做法（**顺序不能错，否则会把自己锁在外面**）

本地电脑（Windows）生成密钥：
```bash
ssh-keygen -t ed25519 -C "myserver"
# 一路回车；公钥在  C:\Users\你\.ssh\id_ed25519.pub
```
把**公钥内容**贴到服务器（最省事的方式）：
```bash
# 在服务器上执行，然后用编辑器粘贴公钥那一整行
mkdir -p ~/.ssh && nano ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```
**先测一次**（新开一个本地 cmd 窗口）：
```bash
ssh root@你的公网IP        # 能免密码登入 = 成功
```
✅ **确认密钥登录成功之后**，再去关闭密码登录：
```bash
nano /etc/ssh/sshd_config
# 改成：
#   PasswordAuthentication no
#   PermitRootLogin prohibit-password
systemctl restart ssh
```
> ⚠️ **不要提前关**——否则密钥没配好时你就进不去了（新手最惨的翻车）。

### 止损三道锁（比“防”更现实）
```
① 额度锁：DeepSeek 后台设月度上限 → 万一被刷，损失封顶
② 数据锁：服务器上别放敏感数据（本项目的 SQLite 里是假数据）
③ 备份锁：代码在 GitHub（别只放服务器）
```

### 面试可讲（安全 ≠ “我没学过”）
> “部署时我做了三件事：**SSH 用密钥登录并关闭密码登录、安全组只开必要端口、给大模型 API 设了月度额度上限**；
> 应用层有 JWT 鉴权和限流，`.env` 不入库。”

---

## 第 1 步：连上服务器

- **最省事**：实例详情页 →「**远程连接**」→ **免密直接进**
  （走的是**阿里云账号身份 + 内部通道**，**不需要服务器密码**；需要 SSH 才去左侧菜单「密钥对」绑私钥）
- 或者本地 cmd（Windows 10+ 自带 ssh）：
  ```bash
  ssh admin@你的公网IP
  ```

> ⚠️ **本项目实际环境（已确认）**：
> - 用户名是 **`admin`**（**不是 root**）→ 后面的 `apt install` / 写系统文件都要加 **`sudo`**
> - 部署目录用**家目录** `~/chatapi`（= `/home/admin/chatapi`），避开 sudo 写权限的麻烦

✅ **验收**：看到 `admin@实例ID:~$` 提示符

---

## 第 2 步：装基础环境（5 分钟）

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
python3 --version          # 期望 3.10 以上
```

✅ **验收**：`python3 --version` 有输出

---

## 第 3 步：把代码拉上去（用 git，最省事）

```bash
cd ~
git clone https://github.com/Gelise436b/ChatApi.git chatapi
cd chatapi
```

> ⚠️ 如果仓库是**私有**的 → 要么改成公开，要么用 token 克隆。**建议先改成公开**（面试官也要看得到）。

✅ **验收**：`ls` 能看到 `app/`、`requirements.txt`、`README.md`

---

## 第 4 步：建虚拟环境 + 装依赖（3–5 分钟）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> 💡 服务器上**不用 conda** —— Python 自带的 `venv` 更轻、更标准。

✅ **验收**：`pip list` 里能看到 `fastapi` / `uvicorn` / `openai`

---

## 第 5 步：写 `.env`（**必须，否则一启动就报错**）

```bash
nano .env
```

内容（4 行）：
```
DEEPSEEK_API_KEY=你的key
DEEPSEEK_MODEL=deepseek-chat
SECRET_KEY=在服务器上新生成的随机串
NO_PROXY=api.deepseek.com,127.0.0.1,localhost
```

生成新密钥（**别复用本地那个**）：
```bash
python3 -c "import secrets;print(secrets.token_urlsafe(48))"
```

✅ **验收**：`cat .env` 能看到 4 行

---

## 第 6 步：先手动试跑一遍 ⚠️ **大坑 1**

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> ⚠️ **`--host 0.0.0.0` 必须写！**
> uvicorn 默认只监听 `127.0.0.1`（只接受本机访问）→ **外网点不开**。这是新手第一个大坑。

✅ **验收**：屏幕上出现 `Uvicorn running on http://0.0.0.0:8000`

---

## 第 7 步：开放端口 ⚠️ **大坑 2（最常见的卡点）**

要在**云控制台**里放行（**不是**在 Linux 里改）：

| 平台 | 位置 | 要加什么 |
|---|---|---|
| 阿里云 | **安全组** → 入方向 → 手动添加 | 协议 TCP，端口 **8000**，授权对象 `0.0.0.0/0` |
| 腾讯云 | **防火墙** → 添加规则 | 端口 **8000**，来源 `0.0.0.0/0` |

> 💡 Ubuntu 自带的 `ufw` 默认是**关闭**的，一般不用管；如果你手动开过，才需要 `ufw allow 8000`。

✅ **验收**：浏览器打开 `http://你的公网IP:8000/docs` —— **能看到 Swagger 文档** 🎉

---

## 第 8 步：验收三个核心接口

在 `/docs` 页面：
1. 展开 `POST /token` → **Try it out** → 填 `zhangsan` / `123456` → Execute → 拿到 `access_token`
2. 点右上角 **Authorize** → 填 token → 点 `POST /chat` → Try it out → `{"message":"说一句你好"}` → Execute
3. 看到**一段段冒出来的流式响应** ✅

✅ **验收**：能问答 = 鉴权 + 流式 + SQLite 全部正常

---

## 第 9 步：让它长期运行（systemd）—— 否则 Ctrl+C / 关掉终端就没了

```bash
nano /etc/systemd/system/chatapi.service
```
```ini
[Unit]
Description=Chat API
After=network.target

[Service]
WorkingDirectory=/home/admin/chatapi
ExecStart=/home/admin/chatapi/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
User=admin

[Install]
WantedBy=multi-user.target
```
```bash
systemctl daemon-reload
systemctl enable chatapi      # 开机自启
systemctl start chatapi
systemctl status chatapi      # 看 active (running)
```

> ⚠️ **`WorkingDirectory` 必须写！** 因为 `chat_history.db` 是**相对路径** —— 不写它，数据库会被建到别的地方（这是个真实的坑）。
> 💡 **面试可讲点**：`Restart=always` = 进程崩了自动重启；`enable` = 开机自启 —— 这就是"让服务可靠运行"的标准做法。

✅ **验收**：`systemctl status` 显示 running；**断开 SSH 再打开** `http://IP:8000/docs` 仍然能访问

---

## 第 10 步（可选，后面再做）：Nginx + 80 端口 + 域名

先别急。等前面全通了，再考虑：
- Nginx 反向代理（把 80 转到 8000）→ 浏览器用 `http://IP/` 直接打开
- 域名 + HTTPS（证书）
- ⚠️ **Nginx 反代流式接口时必须加**：`proxy_buffering off;`（否则流式会被 Nginx 缓存成一次性返回）

---

## 📋 出问题时先查这三样

| 现象 | 大概率原因 |
|---|---|
| 浏览器打不开 | ① 安全组没放行 8000 ② uvicorn 没写 `--host 0.0.0.0` ③ 服务没在跑 |
| 启动就报错 | `.env` 没建 / 缺 `SECRET_KEY` / 依赖没装完 |
| 能打开但一问答就 500 | `DEEPSEEK_API_KEY` 错了；或 SQLite 目录不可写（查 `WorkingDirectory`） |

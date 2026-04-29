# 念念 Eterna — AI 思念亲人平台

> **用 AI 技术保存和延续亲人的记忆与声音**
>
> 让思念不再只是回忆，而是可以触碰的温暖

---

## 快速开始

### 方式一：本地启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 填入 API Key

# 3. 一键启动
chmod +x start.sh
./start.sh
```

打开 http://localhost:8102

### 方式二：Docker 启动

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 方式三：手动启动

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8102 --reload
```

---

## 功能模块

### 核心功能 (已实现)

| 功能 | 说明 | API 端点 |
|------|------|----------|
| 用户注册/登录 | 邮箱+密码认证 | `/api/auth/*` |
| 亲人档案 | 创建/管理亲人信息 | `/api/loved-ones/*` |
| 媒体上传 | 语音/照片/视频/3D模型 | `/api/loved-ones/{id}/voice` |
| AI 对话 | 基于人格的温暖对话 | `/api/chat` |
| 记忆系统 | 存储和检索共同记忆 | `/api/memories/*` |
| 数字人格 | AI人格训练和管理 | `/api/loved-ones/{id}/digital-human` |
| 主动关怀 | 定时推送/节日问候 | `/api/proactive/*` |
| 语音电话 | Twilio语音通话 | `/api/bridge/twilio/*` |

### 纪念服务 (已实现)

| 功能 | 说明 | API 端点 |
|------|------|----------|
| 虚拟蜡烛 | 点燃蜡烛寄托思念 | `/api/candles/{id}` |
| 虚拟献花 | 献上鲜花表达敬意 | `/api/flowers/{id}` |
| 虚拟祈福 | 发送祝福和祈祷 | `/api/prayers/{id}` |
| AI 信件 | 生成写给亲人的信 | `/api/letters/{id}` |
| AI 故事 | 生成亲人的生平故事 | `/api/stories/{id}` |
| 家族树 | 构建家族谱系 | `/api/family-tree/{id}` |
| 纪念墙 | 统计和展示纪念数据 | `/api/memorial-wall/{id}` |
| 哀伤辅导 | 提供心理支持资源 | `/api/grief-resources` |
| 社交分享 | 分享纪念页到社交平台 | `/api/share/{id}` |

### 语音克隆 (已实现)

| 功能 | 说明 | API 端点 |
|------|------|----------|
| 创建语音模型 | 上传语音样本训练 | `/api/voice-clone/create` |
| 语音合成 | 用克隆语音说话 | `/api/voice-clone/synthesize` |
| 语音列表 | 查看所有语音模型 | `/api/voice-clone/list` |

### 订阅计费 (已实现)

| 套餐 | 价格 | 功能 |
|------|------|------|
| 免费版 | ¥0 | 基础纪念页 |
| 基础版 | ¥29/月 | 文字对话 |
| 高级版 | ¥99/月 | 语音对话 |
| 旗舰版 | ¥299/月 | 视频+3D |

---

## 技术架构

```
frontend/
├── index.html          # 主页面 (1120行)
├── css/main.css        # 样式 (3363行)
├── js/app.js           # 应用逻辑 (5009行)
├── js/memorial.js      # 纪念交互组件 (250行)
└── assets/             # 静态资源

api/
├── main.py             # 应用入口
├── app_helpers.py      # 核心函数/模型/DB
├── enhanced_chat.py    # 增强AI对话引擎
├── voice_clone.py      # 语音克隆模块
└── routers/
    ├── auth.py         # 认证路由
    ├── admin.py        # 管理后台
    ├── lovedones.py    # 亲人管理
    ├── media.py        # 媒体上传
    ├── chat.py         # AI对话
    ├── memorial.py     # 纪念服务
    ├── billing.py      # 订阅支付
    ├── proactive.py    # 主动关怀
    ├── memorial_services.py  # 蜡烛/献花/祈福
    └── voice_clone.py  # 语音克隆

data/                   # 配置数据
├── candle-types.json   # 蜡烛类型
├── flower-types.json   # 鲜花类型
├── grief-resources.json # 哀伤资源
└── ...
```

---

## 配置说明

### 必需配置

```bash
# .env
PORT=8102
```

### AI 对话 (推荐)

```bash
# MIMO API 或 OpenAI 兼容 API
MIMO_API_KEY=your-api-key
MIMO_API_BASE=https://api.mimo.ai/v1
```

### 语音克隆 (可选)

```bash
# ElevenLabs API
ELEVENLABS_API_KEY=your-elevenlabs-key
```

### 支付 (可选)

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

---

## 用户流程

```
1. 访问首页 → 注册/登录
2. 创建亲人档案 → 填写基本信息
3. 上传记忆素材 → 语音/照片/文字
4. 训练数字人格 → AI学习亲人的性格
5. 开始对话 → 与数字亲人聊天
6. 纪念服务 → 点蜡烛/献花/祈福
7. 分享纪念页 → 邀请家人一起纪念
```

---

## 开发指南

### 运行测试

```bash
python -m pytest tests/ -v
```

### 添加新的 API 路由

1. 在 `api/routers/` 创建新文件
2. 定义 `router = APIRouter(tags=["xxx"])`
3. 在 `api/main.py` 导入并注册: `app.include_router(xxx.router)`

### 添加新的数据库表

在 `api/app_helpers.py` 的 `init_db()` 函数中添加 CREATE TABLE 语句。

---

## 部署

### Render

1. 连接 GitHub 仓库
2. 选择 Docker 环境
3. 设置环境变量
4. 部署

### Railway

```bash
railway login
railway init
railway up
```

### 自有服务器

```bash
# 使用 Docker Compose
git clone <repo>
cd cloud-memorial
cp .env.example .env
# 编辑 .env
docker-compose up -d
```

---

## 项目统计

- API 路由: 106 个
- 后端模块: 20 个 Python 文件
- 前端文件: 4 个 (HTML/CSS/JS)
- 测试用例: 12 个 (100% 通过)
- 代码总量: ~15,000 行

---

## 许可证

MIT License

---

## 联系方式

- 项目主页: https://github.com/MoKangMedical/cloud-memorial
- 问题反馈: https://github.com/MoKangMedical/cloud-memorial/issues

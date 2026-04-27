# 🌸 云思园 — AI 思念亲人平台

> **用 AI 技术保存和延续亲人的记忆与声音**
>
> _让思念不再只是回忆，而是可以触碰的温暖_

---

## 📖 项目简介

**云思园（Cloud Memorial）** 是一个基于 AI 技术的数字纪念平台。通过上传照片、语音、文字和视频等记忆素材，训练出具有亲人性格特征的数字人格，让思念有处安放，让爱延续不止。

我们相信：**念念不忘，必有回响。**

---

## ✨ 核心功能

| # | 功能 | 说明 |
|---|------|------|
| 1 | 📸 **记忆上传** | 支持上传照片、语音、文字、视频等多模态记忆素材 |
| 2 | 🧠 **AI 人格训练** | 基于上传内容训练数字人格，还原亲人的性格与记忆 |
| 3 | 🎙️ **语音通话** | 与数字亲人进行实时语音对话，聆听熟悉的声音 |
| 4 | 💬 **文字聊天** | 模拟亲人的说话风格，进行自然语言文字对话 |
| 5 | 🕯️ **虚拟纪念** | 在线纪念堂、虚拟祭扫、节日追思 |
| 6 | 🌳 **家族树** | 构建家族族谱，记录家族历史与传承 |

---

## 🎯 使用场景

- 🌿 **清明节** — 远程祭扫，线上追思，跨越时空的缅怀
- 📅 **忌日纪念** — 在特殊日子与亲人"重逢"，重温温暖记忆
- 💭 **日常思念** — 随时随地与数字亲人聊天，分享生活点滴
- 👨‍👩‍👧‍👦 **家族传承** — 记录家族故事，让后代了解祖辈的智慧与爱

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户终端 (Web/App)                      │
├─────────────┬─────────────┬──────────────┬──────────────┤
│  记忆上传模块  │  对话交互模块  │   纪念空间模块  │   家族树模块   │
├─────────────┴─────────────┴──────────────┴──────────────┤
│                      API Gateway                         │
├─────────────────────────────────────────────────────────┤
│                     核心 AI 引擎                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 人格训练  │ │ 语音克隆  │ │ 对话引擎  │ │ 情感分析  │   │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│                    数据与基础设施                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 对象存储  │ │ 向量数据库 │ │ 关系数据库 │ │ 消息队列  │   │
│  │   (OSS)  │ │(Milvus)  │ │ (MySQL)  │ │ (Redis)  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

**技术栈：**

- **前端**：React / Next.js + TailwindCSS
- **后端**：Python (FastAPI) + Node.js
- **AI 引擎**：LLM Fine-tuning + TTS 语音合成 + ASR 语音识别
- **数据库**：MySQL + Redis + Milvus (向量检索)
- **存储**：腾讯云 COS / AWS S3
- **部署**：Docker + Kubernetes + Vercel

---

## 🔒 隐私与安全

我们深知记忆数据的敏感性，云思园采用多层安全防护：

- 🔐 **端到端加密** — 所有上传数据 AES-256 加密存储
- 🛡️ **访问控制** — 基于角色的权限管理（RBAC），数据仅授权用户可访问
- 🗑️ **数据可删除** — 用户可随时永久删除所有数据
- 📋 **合规认证** — 符合 GDPR / 个人信息保护法要求
- 🔍 **审计日志** — 完整的数据访问审计追踪

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- Docker (可选)

### 本地部署

```bash
# 克隆仓库
git clone https://github.com/MoKangMedical/cloud-memorial.git
cd cloud-memorial

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 启动后端
python api/app.py

# 启动前端 (新终端)
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
docker-compose up -d
```

访问 `http://localhost:3000` 即可体验。

---

## 📁 项目结构

```
cloud-memorial/
├── api/                    # 后端 API 服务
│   ├── app.py              # 主应用入口
│   ├── personality_system.py    # 人格系统
│   ├── emotion_analysis.py      # 情感分析
│   ├── memory_system.py         # 记忆系统
│   ├── dialogue_naturalness.py  # 对话自然度
│   ├── emotional_expression.py  # 情感表达
│   └── proactive_care_system.py # 主动关怀
├── frontend/               # 前端界面
│   ├── index.html          # 主页
│   └── assets/             # 静态资源
├── docs/                   # 项目文档
├── scripts/                # 工具脚本
├── data/                   # 示例数据
├── templates/              # 页面模板
├── deploy/                 # 部署配置
└── creative/               # 创意素材
```

---

## 📊 商业模式

| 版本 | 价格 | 功能 |
|------|------|------|
| 🆓 **基础版** | 免费 | 1 个数字人格、文字聊天、基础纪念堂 |
| ⭐ **高级版** | ¥29.9/月 | 5 个数字人格、语音通话、高级纪念堂、家族树 |
| 💎 **尊享版** | ¥99.9/月 | 无限人格、高清语音、专属客服、数据永存 |

详见 [商业模式文档](docs/business-model.md)

---

## 🤝 贡献指南

我们欢迎社区贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

---

## 🔗 相关项目

| 项目 | 定位 |
|------|------|
| [OPC Platform](https://github.com/MoKangMedical/opcplatform) | 一人公司全链路学习平台 |
| [Digital Sage](https://github.com/MoKangMedical/digital-sage) | 与100位智者对话 |
| [Cloud Memorial](https://github.com/MoKangMedical/cloud-memorial) | AI思念亲人平台 |
| [天眼 Tianyan](https://github.com/MoKangMedical/tianyan) | 市场预测平台 |
| [MediChat-RD](https://github.com/MoKangMedical/medichat-rd) | 罕病诊断平台 |
| [MedRoundTable](https://github.com/MoKangMedical/medroundtable) | 临床科研圆桌会 |
| [DrugMind](https://github.com/MoKangMedical/drugmind) | 药物研发数字孪生 |
| [MediPharma](https://github.com/MoKangMedical/medi-pharma) | AI药物发现平台 |
| [Minder](https://github.com/MoKangMedical/minder) | AI知识管理平台 |
| [Biostats](https://github.com/MoKangMedical/Biostats) | 生物统计分析平台 |

## 📄 许可证

本项目采用 MIT 许可证 — 详见 [LICENSE](LICENSE)

---

## 📬 联系我们

- 📧 **邮箱**：contact@cloud-memorial.com
- 🐛 **问题反馈**：[GitHub Issues](https://github.com/MoKangMedical/cloud-memorial/issues)
- 💬 **讨论交流**：[GitHub Discussions](https://github.com/MoKangMedical/cloud-memorial/discussions)

---

<p align="center">
  🌸 <i>每一份思念，都值得被温柔以待</i> 🌸
</p>

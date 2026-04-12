# 正式部署清单

目标域名：`eterna-niannian.cloud`

目标服务器：`43.134.3.158`

## 目录建议

```bash
mkdir -p /opt/eterna-niannian
cd /opt/eterna-niannian
```

把当前项目同步到 `/opt/eterna-niannian`，并在该目录创建 `.env.local`。

数据目录不要放在发布目录里，建议单独放到：

```bash
mkdir -p /var/lib/eterna-niannian
```

## 环境变量

参考项目根目录的 `.env.example`，至少补齐：

```bash
APP_BASE_URL=https://eterna-niannian.cloud
PUBLIC_BASE_URL=https://eterna-niannian.cloud
DATA_DIR=/var/lib/eterna-niannian
MIMO_API_KEY=你的小米 Mimo Key
MIMO_TTS_VOICE=default_zh
OUTBOUND_CALL_WEBHOOK_URL=你的电话桥接服务 URL
OUTBOUND_CALL_WEBHOOK_TOKEN=你的电话桥接服务 Token
TWILIO_ACCOUNT_SID=你的 Twilio Account SID
TWILIO_AUTH_TOKEN=你的 Twilio Auth Token
TWILIO_FROM_NUMBER=你的 Twilio 外呼号码
TWILIO_STATUS_CALLBACK_BASE_URL=https://eterna-niannian.cloud
PHONE_CALL_MAX_TURNS=3
DEFAULT_TIMEZONE=Asia/Shanghai
PROACTIVE_POLL_SECONDS=60
STRIPE_SECRET_KEY=你的 Stripe Secret Key
STRIPE_WEBHOOK_SECRET=你的 Stripe Webhook Secret
STRIPE_PRICE_SEED=price_xxx
STRIPE_PRICE_TREE=price_xxx
STRIPE_PRICE_GARDEN=price_xxx
STRIPE_PRICE_FAMILY=price_xxx
```

## 启动应用

```bash
cd /opt/eterna-niannian
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp deploy/eterna.service /etc/systemd/system/eterna.service
systemctl daemon-reload
systemctl enable eterna.service
systemctl restart eterna.service
systemctl status eterna.service
```

## Nginx 反向代理

```bash
cp deploy/nginx-eterna-niannian.cloud.conf /etc/nginx/conf.d/eterna-niannian.cloud.conf
nginx -t
systemctl reload nginx
```

## HTTPS

```bash
dnf install -y certbot python3-certbot-nginx
certbot --nginx -d eterna-niannian.cloud
```

## 健康检查

```bash
curl -fsS http://127.0.0.1:8102/health
curl -I https://eterna-niannian.cloud
```

## Stripe Webhook

上线后，把 Stripe webhook 指到：

```text
https://eterna-niannian.cloud/api/billing/webhook
```

监听事件至少包括：

- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## 主动电话说明

主动联系功能现在支持三条路径：

- 站内主动问候：系统按节奏生成文字和语音，在产品内主动出现
- Twilio 内建外呼：如果配置了 `TWILIO_ACCOUNT_SID`、`TWILIO_AUTH_TOKEN` 和 `TWILIO_FROM_NUMBER`，系统会直接通过 Twilio 拨打电话，并用数字人模型继续语音对话
- 自定义电话桥接：如果配置了 `OUTBOUND_CALL_WEBHOOK_URL`，系统会把外呼请求推送到你的电话服务商或语音桥接服务

如果还没有配置任何电话桥接，产品依然会生成主动联系内容和语音，但会停留在站内，不会真正拨打电话。

## Twilio 语音会话回调

如果走内建 Twilio 外呼，服务会自动使用这几个回调地址，不需要再手工配置：

- `https://eterna-niannian.cloud/api/bridge/twilio/connect/{event_id}`
- `https://eterna-niannian.cloud/api/bridge/twilio/respond/{event_id}`
- `https://eterna-niannian.cloud/api/bridge/twilio/status/{event_id}`

这些地址会直接使用数字人模型生成主动开场、接收用户语音输入，并继续返回下一轮电话回复。

# MCP 集成说明

本项目真实使用麦当劳中国 MCP Server（`mcd-mcp`）的能力，把营销活动、收藏品上新、优惠券与积分权益转化为可订阅的 ICS 日历 + PC 端 AI 助手。

## 使用的 MCP Server

| 项 | 值 |
|---|---|
| 名称 | 麦当劳中国 MCP Server（`mcd-mcp`） |
| 接入地址 | `https://mcp.mcd.cn` |
| 传输协议 | Streamable HTTP |
| 认证方式 | `Authorization: Bearer <MCP Token>` |
| Token 申请 | https://open.mcd.cn/mcp（手机号登录 → 控制台 → 激活） |
| 工具总数 | 35 个（`tools/list` 实测） |

## 使用的 Tool 及业务价值

### 公共数据（对所有订阅者开放）

| Tool | 用途 | 产物 |
|---|---|---|
| `campaign-calendar` | 查询当月营销活动日历（进行中/往期/未来，含图片、领券深链） | `data/campaigns.json` → `calendar.ics` |
| `mall-points-products` | 查询积分商城可兑换商品（收藏品/周边/派对等 50 件） | `data/products.json` → 收藏/权益日历 |
| `mall-product-detail` | 查询单个商品 SPU 详情（含 SKU） | 商品详情 |
| `query-nearby-stores` | 查询附近门店 | 落地页地图 |
| `available-coupons` | 查询可领取优惠券列表（公共） | `data/coupons.json` |
| `now-time-info` | 获取当前时间 | 校准日期口径 |

### 个人数据（需用户本人授权，不进入公共订阅源）

| Tool | 用途 | 说明 |
|---|---|---|
| `auto-bind-coupons` | 一键领取全部可用券 | 账户操作，需授权 |
| `query-my-coupons` | 查询卡包券资产 | 个人数据 |
| `query-my-account` | 查询积分账户详情（余额/到期） | 个人数据 |
| `query-lottery-info` | 查询积分抽奖活动 | 个人数据 |
| `query-my-prizes` | 查询我的抽奖奖品 | 个人数据 |
| `draw-lottery` | 执行抽奖（消耗积分） | 需用户明确确认 |
| `query-party-city` / `query-party-store` / `query-party-store-date` / `query-party-store-session` | 主题活动城市/门店/日期/场次查询 | 派对/体验营/品鉴会 |

## 调用流程

```
用户说「更新麦当劳日历」
        │
        ▼
┌─────────────────────────────┐
│ 1. scripts/collect_data.py   │  调用 campaign-calendar / mall-points-products /
│    （内部走 mcp_call.py）      │  available-coupons 等，结构化落盘 data/*.json
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 2. scripts/gen_calendars.py  │  JSON → RFC 5545 ICS（含 VALARM 提前一天提醒）
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 3. 生成 3 个 ICS             │  calendar.ics / calendar-collectibles.ics /
│                              │  calendar-benefits.ics
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 4. scripts/sync_summary.py   │  生成前端 summary.json（仅公共数据）
└─────────────────────────────┘
        │
        ▼
  用户手机日历订阅远程 URL → 提前一天提醒 → 点链接领券/查看

用户说「帮我领券」（个人授权后）
        │
        ▼
┌─────────────────────────────┐
│ 调用 auto-bind-coupons       │  自动领取全部可用券
└─────────────────────────────┘

用户说「我有多少积分」（个人授权后）
        │
        ▼
┌─────────────────────────────┐
│ 调用 query-my-account        │  返回积分余额 / 到期积分
└─────────────────────────────┘
```

## 关键实现点

- **领券链接进日历 `URL` 字段**：ICS 的 `URL` 属性让手机日历在活动提醒里带可点击链接。App 深链（`mcdapp://`）不能放 ICS，统一用官方推文页（`/news/...`，已验证可达）。
- **提前一天提醒**：`VALARM` + `TRIGGER;VALUE=DATE-TIME`（发售/截止前一天 09:00 本地时间），仅对未来事件触发，已发生不补发。
- **长期活动标首尾**：跨度 > 5 天的活动只在「上线」「截止」两天各放一条（`UID` 加 `-start`/`-end` 后缀）。
- **个人数据隔离**：`my_account.json` / `my_coupons.json` / `lottery.json` 已加入 `.gitignore`，`summary.json` 只含公共数据，个人 Token 和权益不泄露到公共订阅源。
- **脱敏配置**：`mcp-config.example.json` 仅使用 `${MCD_MCP_TOKEN}` 环境变量占位符，不包含真实 Token。

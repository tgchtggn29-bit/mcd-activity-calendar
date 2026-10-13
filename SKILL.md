---
name: mcd-activity-calendar
description: 麦麦权益与收藏日历（McCalendar）。基于麦当劳 MCP 能力，把营销活动、收藏品上新、积分兑换与优惠券做成可订阅的 ICS 日历，PC 端 WorkBuddy 里用自然语言查询/领券/查积分，手机端通过远程日历 URL 订阅并提前一天提醒。当用户说「麦当劳活动」「麦麦活动」「订阅麦当劳日历」「麦当劳收藏品」「帮我领券」「查我的积分」「积分抽奖」「麦当劳主题活动」「附近麦当劳」时使用。
agent_created: true
---

# 麦麦权益与收藏日历（McCalendar）

把麦当劳的**营销活动、收藏品上新、优惠券、积分权益**变成一个可持续更新的日历订阅服务：

- **手机端**：订阅一个远程日历 URL，活动上线、收藏品发售、积分到期前**提前一天提醒**
- **PC 端**：在 WorkBuddy 里用自然语言查活动、领券、查积分、查收藏品、生成日历订阅链接

核心思路复用「湾区 AI 日历」的 ICS 订阅链路，数据源是麦当劳 MCP（35 个真实工具）。

## 一、能力与 MCP 工具映射

| 模块 | 麦当劳 MCP 工具 | 产物 |
|---|---|---|
| 活动日历 | `campaign-calendar` | `data/campaigns.json` → `assets/calendar.ics` |
| 收藏日历 | `mall-points-products` / `mall-product-detail` | `data/products.json` → `assets/calendar-collectibles.ics` |
| 优惠券 | `available-coupons` / `auto-bind-coupons` / `query-my-coupons` | `data/coupons.json`（个人授权） |
| 积分权益 | `query-my-account` / `mall-points-products` | `data/my_account.json`（个人授权） |
| 积分抽奖 | `query-lottery-info` / `query-my-prizes` / `draw-lottery` | `data/lottery.json`（个人授权） |
| 主题活动 | `query-party-city` / `query-party-store` / `query-party-store-date` / `query-party-store-session` | 派对/体验营/品鉴会场次 |
| 附近门店 | `query-nearby-stores` | 落地页地图 |
| 时间校准 | `now-time-info` | 校准日期口径 |

## 二、工作流

### 1. 采集全部数据（核心脚本）

用户说「**更新麦当劳日历**」「**刷新麦麦数据**」时：

```bash
python3 scripts/collect_data.py        # 采集活动/收藏品/优惠券/积分/抽奖 → data/*.json
python3 scripts/gen_calendars.py       # 生成三个 ICS → assets/*.ics
python3 scripts/sync_summary.py        # 生成前端 summary.json（仅公共数据）
```

> 采集脚本内部调用 `mcp_call.py` 连麦当劳 MCP，Token 从环境变量 `MCD_MCP_TOKEN` 或脚本默认值读取。

### 2. 帮用户领券（个人授权）

用户说「**帮我领券**」「**一键领券**」时：

1. 确认这是用户本人授权的账户操作（PRD 要求：领券等账户操作必须经用户授权）
2. 调用 `auto-bind-coupons` 自动领取全部可用券
3. 也可先 `available-coupons` 列出可领券，让用户选择

### 3. 查积分 / 卡包 / 抽奖（个人授权）

- 「**我有多少积分**」→ `query-my-account`
- 「**我有什么券**」→ `query-my-coupons`
- 「**抽奖有什么奖品**」→ `query-lottery-info`（`draw-lottery` 需用户明确确认后才调用，避免误扣积分）

### 4. 收藏品 / 主题活动查询

- 「**有哪些收藏品上新**」→ `mall-points-products`（`catRuleIds` 筛选玩具/周边等）
- 「**深圳有哪些主题派对**」→ `query-party-city` → `query-party-store` → `query-party-store-date` → `query-party-store-session`

### 5. 生成订阅链接

- 「**生成苹果日历订阅链接**」→ 返回 `assets/calendar.ics` 的 URL（`webcal://` 前缀）
- 三个日历：活动 `calendar.ics`、收藏 `calendar-collectibles.ics`、权益 `calendar-benefits.ics`

## 三、订阅口径（重要）

与「湾区 AI 日历」一致，避免日历被长期活动铺满：

- 跨度 ≤ 5 天：整段显示
- 跨度 > 5 天：只在**开始日**（「上线」）和**结束日**（「截止」）各放一条
- `rolling: true` 的长期滚动活动：排除
- **收藏品/权益**：发售前一天、截止前一天各通过 `VALARM` 提醒（未来事件才触发，已发生不补发）

## 四、数据模型

### 活动 `data/campaigns.json`

```json
{
  "id": "camp_xxx", "title": "活动名",
  "start_date": "2026-10-08", "end_date": "2026-10-21",
  "type": "营销活动", "category": "活动", "region": "全国",
  "coupon_link": "https://www.mcdonalds.com.cn/news/...",
  "app_jump_url": "mcdapp://...", "image": "https://...",
  "button_text": "立即领券", "highlights": "...", "description": "...",
  "rolling": false
}
```

### 收藏品/积分商品 `data/products.json`

```json
{
  "id": "prod_1830", "spu_id": 1830, "name": "麦当劳亲子读书会",
  "image": "https://...", "point": "0", "price": "45",
  "category": "读书会", "selling": "...",
  "up_time": "2023-03-29 00:00:00", "down_time": "2026-12-30 23:59:59", "status": 2
}
```

## 五、隐私与合规（PRD 硬性要求）

- **个人数据（积分余额、卡包券、奖品、领券操作）绝不进公共订阅源**：`data/summary.json` 只含 `campaigns` / `products` / `coupons`（可领券列表是公共的），不含 `my_account` / `my_coupons` / `lottery`。
- 领券、抽奖、查积分等账户操作，必须在用户明确授权（配置本人 MCP Token）后执行。
- 订阅 URL 不包含账号 Token、手机号、个人券码等敏感资料。
- 失败的数据查询不得当作「无活动/无库存」；不将演示数据当真实官方数据。

## 六、目录结构

```
mcd-activity-calendar/
├── SKILL.md                    # 本文件
├── README.md                   # 项目介绍（含订阅教程）
├── CONTEST_DECLARATION.md      # 官方参赛声明（不可改动）
├── MCP_INTEGRATION.md          # MCP 集成说明
├── mcp-config.example.json     # 脱敏配置示例
├── workbuddy.md                # WorkBuddy 对话上下文
├── scripts/
│   ├── mcp_call.py             # MCP 调用客户端
│   ├── collect_data.py         # 采集全部数据
│   ├── gen_calendars.py        # 多类别 ICS 生成器（含提前一天 VALARM）
│   ├── gen_calendar_ics.py     # 旧版活动日历生成器（兼容）
│   └── sync_summary.py         # 生成前端 summary.json
├── data/
│   ├── campaigns.json          # 活动
│   ├── products.json           # 收藏品/积分商品
│   ├── coupons.json            # 可领券（公共）
│   ├── my_account.json         # 积分（个人，不入 summary）
│   ├── my_coupons.json         # 卡包券（个人，不入 summary）
│   ├── lottery.json            # 抽奖（个人，不入 summary）
│   └── summary.json            # 前端公共数据汇总
├── assets/
│   ├── calendar.ics            # 活动日历
│   ├── calendar-collectibles.ics  # 收藏日历
│   └── calendar-benefits.ics   # 权益日历
├── index.html                  # 订阅落地页（多 Tab）
└── dashboard.html              # 订阅统计面板
```

# 麦麦权益与收藏日历 · McCalendar

> 麦当劳程序员创意开发大赛参赛作品

把麦当劳的**营销活动、收藏品上新、优惠券、积分权益**变成一个可持续更新的日历订阅服务：
手机日历订阅一个远程 URL，活动上线、收藏品发售、积分到期前**提前一天自动提醒**；
PC 端 WorkBuddy 里用自然语言查活动、领券、查积分、查收藏品。

## 它解决了什么问题

麦当劳的优惠活动、联名周边、限定玩具都藏在 App 深处，用户往往「错过才知道」。本项目把官方数据（麦当劳 MCP）转成标准 ICS 日历订阅 + PC 端 AI 助手：

- 📅 **活动日历**：营销活动上线/截止自动提醒
- 🧸 **收藏日历**：玩具、IP 联名、限量周边、积分实物发售前一天提醒
- 🎟️ **优惠券助手**：可领券查询、本人授权后一键领券、卡包券管理
- ⭐ **积分权益**：积分余额、到期提醒、积分商城兑换
- 🎰 **积分抽奖**：抽奖活动、我的奖品
- 📍 **附近门店**：地图标出附近麦当劳，缩短「领券 → 到店」路径
- 📊 **订阅统计**：公开后台看板展示转化漏斗

## 功能特性

| 能力 | 说明 |
|---|---|
| 双订阅系统 | 手机 ICS 日历 + PC WorkBuddy Skill，二选一或同时使用 |
| 合集日历 | 活动/收藏/权益合并成一个 ICS，一个订阅全搞定 |
| 多类别日历 | 活动日历 / 收藏日历 / 权益日历，可独立订阅 |
| 提前一天提醒 | 发售/截止前一天 09:00 通过 VALARM 提醒 |
| 一键领券 | 本人授权后自动领取全部可用券 |
| 收藏品订阅 | 五大类收藏品独立筛选 |
| 个人数据隔离 | 积分/卡包/奖品不进入公共订阅源 |

## 安装方法

### 前置条件

1. 申请麦当劳 MCP Token：https://open.mcd.cn/mcp（手机号登录 → 控制台 → 激活）
2. 将 Token 配置到支持 MCP 的客户端（推荐 [WorkBuddy](https://www.workbuddy.cn)）

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": { "Authorization": "Bearer 你的_TOKEN" }
    }
  }
}
```

### 使用步骤

1. 在 WorkBuddy 中导入本 Skill（`SKILL.md`）
2. 对话中说「**更新麦当劳日历**」→ 自动采集数据并生成合集 + 分三类共 4 个 ICS
3. 说「**订阅麦当劳活动**」→ 获得订阅地址
4. 把订阅地址添加到手机/电脑日历：

| 平台 | 步骤 |
|---|---|
| iPhone | 设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历 → 粘贴 URL |
| Android（小米/华为等） | 日历 App → 订阅管理 / 添加日历 → 通过 URL 订阅 |
| Google Calendar | 其他日历 → 通过 URL 添加 |
| 电脑 | Outlook / 系统日历 → 从 Internet 添加日历 |

## 在线体验（已上线）

| 资源 | 地址 |
|---|---|
| 订阅落地页 | https://mcd-activity-calendar.app.workbuddy.host/ |
| **⭐ 合集日历 ICS（推荐）** | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar-all.ics |
| 活动日历 ICS | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar.ics |
| 收藏日历 ICS | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar-collectibles.ics |
| 权益日历 ICS | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar-benefits.ics |
| 订阅统计后台 | https://mcd-activity-calendar.app.workbuddy.host/dashboard.html |

> 订阅方式：手机日历 → 通过 URL 添加日历 → 粘贴 ICS 订阅地址。
> **合集日历**把活动、收藏品、积分权益合并成一个订阅，一个地址全搞定；
> 也可按需只订阅某一类。活动上线、收藏品发售前一天自动提醒，点提醒里的链接直达官方详情。

## 使用示例

```
用户：更新麦当劳日历
助手：已采集 15 条活动、50 件积分商品、7 张可领券，生成 3 个日历。
     活动日历：https://.../calendar.ics
     收藏日历：https://.../calendar-collectibles.ics
     权益日历：https://.../calendar-benefits.ics

用户：帮我领券
助手：（调用 auto-bind-coupons）已为你领取全部 7 张可用优惠券。

用户：我有多少积分？
助手：（调用 query-my-account）你当前可用积分 201.4，本月到期 36.5。

用户：有哪些收藏品上新？
助手：（调用 mall-points-products）当前积分商城有 Nike 联名鞋、罗技键鼠套装等收藏品。

用户：深圳有哪些主题派对？
助手：（调用 query-party-city / query-party-store）深圳可预约的门店有...
```

## 参赛提交（GitHub）

1. 将本目录推送到你的 GitHub 公开仓库（Public）
2. 确认仓库包含以下必备文件（文件名不可改动）：
   - `README.md`、`CONTEST_DECLARATION.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`
   - 源代码、`workbuddy.md`（WorkBuddy 专项奖励）
3. 在活动仓库 [M-China/mcd-developer-innovation-challenge](https://github.com/M-China/mcd-developer-innovation-challenge) 发 Issue 报名：

```
【参赛申请】
项目名称：麦麦权益与收藏日历（McCalendar）
项目地址：https://github.com/<你的用户名>/<仓库名>
项目简介：基于麦当劳 MCP，把营销活动、收藏品上新、优惠券与积分权益做成可订阅日历，PC Skill 与 ICS 双渠道，发售提前一天提醒
```

> ⚠️ 报名 Issue 的标题与正文之间、各字段与内容之间不要用换行符；项目地址不要用 Markdown 链接格式。

## 目标用户

- **麦门信徒 / 麦当劳爱好者**：不想错过联名周边、限定玩具、限时优惠
- **收藏党**：关注玩具、手办、IP 联名、盲盒上新
- **省钱包用户**：把「领券」变成日历自动提醒
- **开发者**：想了解「MCP 能力 + 日历订阅」玩法的技术人

## 隐私与合规

- 个人积分、卡包券、抽奖奖品等**个人权益数据绝不进入公共订阅源**（`data/summary.json` 只含公共活动/商品/可领券列表）
- 领券、抽奖、查积分等账户操作需用户本人授权
- 订阅 URL 不含账号 Token、手机号、个人券码
- 个人数据文件（`my_account.json` / `my_coupons.json` / `lottery.json`）已加入 `.gitignore`，不提交公开仓库

## 项目结构

```
mcd-activity-calendar/
├── SKILL.md                  # WorkBuddy Skill 入口
├── README.md                 # 本文件
├── CONTEST_DECLARATION.md    # 官方参赛声明
├── MCP_INTEGRATION.md        # MCP 集成说明
├── mcp-config.example.json   # 脱敏配置示例
├── workbuddy.md              # WorkBuddy 对话上下文
├── scripts/
│   ├── mcp_call.py           # MCP 调用客户端
│   ├── collect_data.py       # 采集全部数据
│   ├── gen_calendars.py      # 多类别 ICS 生成器
│   └── sync_summary.py       # 生成前端公共数据
├── data/                     # 活动/商品/券数据库（JSON）
├── assets/                   # 4 个订阅 ICS（合集 + 活动/收藏/权益）
├── index.html                # 订阅落地页（多 Tab）
└── dashboard.html            # 订阅统计面板
```

## 声明

本项目为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。
项目输出仅供参考；餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。

**开发者邮箱**：931225409@qq.com

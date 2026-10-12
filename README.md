# 麦当劳活动推荐助手 · 麦麦活动日历

> 麦当劳程序员创意开发大赛参赛作品

把麦当劳的营销活动日历变成**你手机日历里的主动推送**：订阅一个远程日历 URL，
活动上线、即将截止时自动提醒，点开提醒里的链接直接跳转领券，落地页还帮你找到附近门店。

## 它解决了什么问题

麦当劳的优惠活动藏在 App 深处，用户往往「错过活动才知道」。本项目把官方活动日历
（`campaign-calendar`）转成标准 ICS 日历订阅：

- 📅 **主动推送**：活动上线当天、即将截止当天，手机日历自动提醒，不再错过限时优惠
- 🎟️ **一键领券**：日历提醒里自带活动链接，点开直接跳转领券
- 📍 **附近门店**：落地页用地图标出附近麦当劳，缩短「领券 → 到店」路径
- 📊 **订阅统计**：公开后台看板展示领订阅码、点击领券、跳转 App 的转化漏斗

## 功能特性

| 能力 | 说明 |
|---|---|
| 活动日历订阅 | 麦当劳营销活动 → ICS 日历 → 远程 URL 订阅 |
| 上线/截止提醒 | 长期活动标「上线」「截止」两个节点，关键时间各提醒一次 |
| 领券跳转 | 日历 `URL` 字段直连活动领券链接 |
| 附近门店地图 | 腾讯地图标记附近麦当劳门店 |
| 订阅统计后台 | 云数据库埋点 + 公开转化漏斗看板 |

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
2. 对话中说「**更新麦当劳活动日历**」→ 自动拉取活动并生成 `assets/calendar.ics`
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
| **ICS 订阅地址** | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar.ics |
| 订阅统计后台 | https://mcd-activity-calendar.app.workbuddy.host/dashboard.html |

> 订阅方式：手机日历 → 通过 URL 添加日历 → 粘贴 ICS 订阅地址。
> 活动上线、即将截止时，日历会自动提醒，点提醒里的链接直达领券。

## 使用示例

```
用户：更新麦当劳活动日历
助手：已拉取 7 条营销活动，生成 13 条日程。订阅地址：
     https://mcd-activity-calendar.app.workbuddy.host/assets/calendar.ics

用户：附近有哪些麦当劳？
助手：（调用 query-nearby-stores）已找到 4 家附近门店，见落地页地图。
```

## 参赛提交（GitHub）

1. 将本目录推送到你的 GitHub 公开仓库（Public）
2. 确认仓库包含以下必备文件（文件名不可改动）：
   - `README.md`、`CONTEST_DECLARATION.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`
   - 源代码、`workbuddy.md`（WorkBuddy 专项奖励）
3. 在活动仓库 [M-China/mcd-developer-innovation-challenge](https://github.com/M-China/mcd-developer-innovation-challenge) 发 Issue 报名：

```
【参赛申请】
项目名称：麦当劳活动推荐助手（麦麦活动日历）
项目地址：https://github.com/<你的用户名>/<仓库名>
项目简介：把麦当劳营销活动转成可订阅的 ICS 日历，活动上线/截止自动推送、点链接直达领券、附附近门店地图与订阅统计后台
```

> ⚠️ 报名 Issue 的标题与正文之间、各字段与内容之间不要用换行符；项目地址不要用 Markdown 链接格式。

## 目标用户

- **麦当劳爱好者 / 麦门信徒**：不想错过任何限时优惠的普通消费者
- **省钱包用户**：把「领券」变成日历自动提醒的省钱党
- **开发者**：想了解「MCP 能力 + 日历订阅」玩法的技术人

## 项目结构

```
mcd-activity-calendar/
├── SKILL.md                  # WorkBuddy Skill 入口
├── README.md                 # 本文件
├── CONTEST_DECLARATION.md    # 官方参赛声明
├── MCP_INTEGRATION.md        # MCP 集成说明
├── mcp-config.example.json   # 脱敏配置示例
├── workbuddy.md              # WorkBuddy 对话上下文
├── scripts/gen_calendar_ics.py   # 活动 → ICS 生成器
├── data/                     # 活动/门店数据库（JSON）
├── assets/calendar.ics       # 订阅文件
├── index.html                # 订阅落地页
└── dashboard.html            # 订阅统计面板
```

## 声明

本项目为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。
项目输出仅供参考；餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。

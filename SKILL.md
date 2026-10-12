---
name: mcd-activity-calendar
description: 麦当劳活动推荐助手。基于麦当劳 MCP 能力，把麦当劳营销活动日历与优惠券写入 ICS 日历，用户通过远程日历 URL 在手机日历里订阅，即可收到活动上线/截止推送，点开活动链接直接跳转领券，并推荐附近麦当劳门店地图。当用户说「麦当劳活动」「麦麦活动日历」「订阅麦当劳活动」「麦当劳优惠券日历」「更新麦当劳活动」「附近麦当劳门店」「麦当劳活动推送」时使用。
---

# 麦当劳活动推荐助手

把麦当劳的营销活动日历变成一个**可订阅的 ICS 日历**：用户在手机/电脑日历里订阅一个 URL，
活动上线、即将截止时自动收到提醒，点开提醒里的链接直接跳转领取优惠券，落地页还附带附近门店地图。

核心思路复用「湾区 AI 日历」的订阅链路，但数据源换成麦当劳 MCP 的营销活动日历。

## 一、能力概览

| 能力 | 依赖的麦当劳 MCP 工具 | 产物 |
|---|---|---|
| 拉取活动日历 | `campaign-calendar`（营销活动日历查询） | `data/campaigns.json` |
| 生成订阅日历 | 本地脚本 | `assets/calendar.ics` |
| 领券跳转 | 活动自带领券链接 | 日历 VEVENT 的 `URL` 字段 |
| 附近门店推荐 | `query-nearby-stores`（附近门店查询） | `data/stores.json` + 落地页地图 |
| 订阅统计后台 | `available-coupons` / 落地页埋点 | 云数据库统计面板 |

## 二、工作流（在 WorkBuddy 里怎么用）

### 1. 更新活动日历（核心流程）

用户说「**更新麦当劳活动日历**」时，按顺序执行：

1. **调用 MCP 工具** `campaign-calendar` 拉取当月营销活动（进行中 + 未来活动）
2. **结构化落盘**：把返回的活动映射成 `data/campaigns.json`，每条活动字段见下方「数据模型」
3. **生成 ICS**：运行
   ```bash
   python3 scripts/gen_calendar_ics.py data/campaigns.json assets/calendar.ics --cal-name "麦麦活动日历"
   ```
4. **发布**：把 `assets/calendar.ics` 上传到订阅地址（GitHub Pages / 托管静态目录），
   让用户订阅的远程 URL 拿到最新内容

> 映射规则：MCP 返回的活动字段与本项目 `data/campaigns.json` 字段名可能不同，
> 调用后用 `now-time-info` 校准当前日期，把活动名→`title`、开始→`start_date`、
> 结束→`end_date`、领券链接→`coupon_link`、类型→`type`，其余信息塞进 `description`。

### 2. 帮用户订阅

用户说「**订阅麦当劳活动**」时：
- 给出订阅地址（远程日历 URL），并附 iOS / Android / 电脑日历的添加步骤
- 订阅链接示例：`https://<你的托管域名>/assets/calendar.ics`（可用 `webcal://` 前缀）

### 3. 推荐附近门店

用户说「**附近有哪些麦当劳**」或给出地址时：
- 调用 MCP 工具 `query-nearby-stores` 查询该地址附近的麦当劳门店
- 把门店列表（名称/地址/经纬度/距离）写入 `data/stores.json`
- 落地页 `index.html` 会用腾讯地图标出门店位置

### 4. 订阅统计

落地页已埋点：领订阅码、点击领券、跳转 App/小程序都会写入云数据库，
统计面板（`dashboard.html`）公开展示转化漏斗。

## 三、相关 MCP 工具速查

| 工具 | 用途 | 本 skill 用法 |
|---|---|---|
| `campaign-calendar` | 查询当月营销活动日历 | 拉活动、生成 ICS 的数据源 |
| `query-nearby-stores` | 查附近门店 | 门店地图推荐 |
| `available-coupons` | 麦麦省可领券列表 | 补充领券链接 |
| `auto-bind-coupons` | 麦麦省一键领券 | 领券场景 |
| `now-time-info` | 获取当前时间 | 校准活动日期口径 |

## 四、数据模型

### 活动 `data/campaigns.json`

```json
{
  "id": "camp_202610_xxx",        // 稳定唯一 id（活动不变则 id 不变，避免日历重复）
  "title": "活动名称",
  "start_date": "2026-10-10",     // 开始日期
  "end_date": "2026-10-20",       // 结束日期（可选，缺省单日）
  "type": "优惠券活动",            // 活动类型
  "category": "限时优惠",          // 分类标签
  "region": "全国",               // 适用地区
  "coupon_link": "https://...",    // 领券链接（进日历 URL 字段，点开跳转领券）
  "description": "活动说明",
  "rolling": false                // true = 长期滚动开放，会从日历排除
}
```

### 门店 `data/stores.json`

```json
{
  "id": "store_001",
  "name": "麦当劳（中关村店）",
  "address": "北京市海淀区中关村大街 27 号",
  "lat": 39.984104,
  "lng": 116.307503,
  "distance": "距你 0.8 km",
  "open_hours": "07:00-22:00"
}
```

## 五、订阅口径（重要）

与「湾区 AI 日历」一致，避免日历被长期活动铺满：

- 跨度 ≤ 5 天的活动：整段显示
- 跨度 > 5 天的活动：只在**开始日**（「活动上线」）和**结束日**（「即将截止」）各放一条日程，
  让用户在活动上线当天和即将结束当天各收到一次提醒——这对领券活动尤其关键
- `rolling: true` 的长期滚动活动：排除，不占日历

## 六、目录结构

```
mcd-activity-calendar/
├── SKILL.md                  # 本文件
├── README.md                 # 项目介绍
├── CONTEST_DECLARATION.md    # 官方参赛声明（不可改动）
├── MCP_INTEGRATION.md        # MCP 集成说明
├── mcp-config.example.json   # 脱敏配置示例
├── workbuddy.md              # WorkBuddy 对话上下文
├── scripts/
│   └── gen_calendar_ics.py   # JSON → ICS 生成器
├── data/
│   ├── campaigns.json        # 活动数据库
│   └── stores.json           # 门店数据库
├── assets/
│   └── calendar.ics          # 订阅文件（静态托管）
├── index.html                # 订阅落地页（订阅 + 活动 + 门店地图）
└── dashboard.html            # 订阅统计面板
```

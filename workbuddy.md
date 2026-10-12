# WorkBuddy 对话上下文（参赛联动凭证）

本项目使用 **WorkBuddy** 完成构思、开发与调试，以下记录关键对话上下文，用于核验
WorkBuddy 专项奖励（前 100 名提交本文件可获 3000 积分）。

## 项目缘起

- 目标：基于麦当劳 MCP 能力，开发「麦麦权益与收藏日历（McCalendar）」Skill。
- 核心思路：复用「湾区 AI 日历」的 ICS 订阅链路，把麦当劳营销活动、收藏品上新、
  优惠券与积分权益转成可订阅的 ICS 日历，PC Skill 与 ICS 双渠道触达，发售提前一天提醒。

## 开发过程（关键节点）

1. **调研**：熟读大赛规则（README / activityGuidelines / CONTEST_DECLARATION），
   确认参赛必备文件与报名 Issue 格式约束。
2. **摸清 MCP 能力**：`tools/list` 实测麦当劳 MCP Server 共 35 个工具，锁定
   `campaign-calendar`（活动）、`mall-points-products`（收藏品/积分商品）、
   `available-coupons` / `auto-bind-coupons`（领券）、`query-my-account`（积分）、
   `query-lottery-info`（抽奖）、`query-party-*`（主题活动）为核心数据源。
3. **产品升级**：根据《McCalendar PRD V1.0》把项目从「活动日历」升级为
   「权益与收藏日历」，覆盖活动/收藏/优惠券/积分/抽奖/主题活动十大模块。
4. **复用沉淀**：复用「湾区 AI 日历」的 ICS 生成逻辑（RFC 5545 转义、折行、CRLF、
   DTEND 排他 +1、UID 稳定、REFRESH-INTERVAL），并扩展多类别日历 + VALARM 提前一天提醒。
5. **数据采集层**：`scripts/mcp_call.py`（MCP 客户端）+ `collect_data.py`（批量采集
   落盘）+ `gen_calendars.py`（多类别 ICS）+ `sync_summary.py`（前端公共数据）。
6. **落地页**：多 Tab 站点（首页/活动/收藏/优惠券/积分/抽奖/门店），腾讯地图合规代理模式。
7. **隐私合规**：个人积分/卡包/奖品不进公共订阅源，`.gitignore` 排除个人数据文件。
8. **订阅统计后台**：WorkBuddy 云服务数据库埋点（领订阅码/点击领券/跳转 App），公开看板。
9. **定时刷新**：配置每日自动化，自动拉最新数据并重生成 ICS。

## 用到的 WorkBuddy 能力

- 麦当劳 MCP 连接器（Streamable HTTP，Bearer Token 认证）
- 云服务（数据库埋点 + 公开统计）
- 静态站点发布（订阅 URL 托管）
- 定时自动化（数据每日刷新）

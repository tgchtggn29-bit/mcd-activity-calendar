# 安装说明 · 麦麦权益与收藏日历（McCalendar）

本文档说明如何在 WorkBuddy 中安装并使用本 Skill。

- **Skill 名称**：`mcd-activity-calendar`（麦麦权益与收藏日历 / McCalendar）
- **运行环境**：WorkBuddy 桌面端（macOS / Windows）
- **必备依赖**：麦当劳 MCP Token（免费申请）
- **GitHub 仓库**：https://github.com/tgchtggn29-bit/mcd-activity-calendar

---

## 一、前置条件

### 1. 安装 WorkBuddy

从 https://www.workbuddy.cn 下载并安装桌面端，登录账号。

### 2. 申请麦当劳 MCP Token（必须）

1. 打开 https://open.mcd.cn/mcp
2. 用手机号登录 → 进入控制台
3. 点击「激活」生成你的 MCP Token（形如 `1CUpPvRg2...`）
4. 复制保存，后面配置要用

> Token 是访问麦当劳官方 MCP 能力的凭证，**只保存在你本机**，不会上传到本项目服务器。

---

## 二、安装 Skill（三种方式，任选一种）

### 方式 A：从 GitHub 导入（推荐）

1. 打开 WorkBuddy → 左侧「技能」→ 右上角「导入技能 / 从 GitHub 导入」
2. 填入仓库地址：
   ```
   https://github.com/tgchtggn29-bit/mcd-activity-calendar
   ```
3. 确认导入，等待完成

### 方式 B：本地目录安装（手动）

macOS / Linux：

```bash
git clone https://github.com/tgchtggn29-bit/mcd-activity-calendar.git \
  ~/.workbuddy/skills/mcd-activity-calendar
```

Windows（PowerShell）：

```powershell
git clone https://github.com/tgchtggn29-bit/mcd-activity-calendar.git `
  "$env:USERPROFILE\.workbuddy\skills\mcd-activity-calendar"
```

> 关键：Skill 目录下必须**直接**有 `SKILL.md`（即 `~/.workbuddy/skills/mcd-activity-calendar/SKILL.md`），
> 不要再套一层子目录，否则 WorkBuddy 扫不到。

### 方式 C：技能包（zip）

1. 获取 zip：在 GitHub 仓库页点 **Code → Download ZIP**，或使用随项目提供的
   `mcd-activity-calendar-skill.zip`
2. 解压后把整个 `mcd-activity-calendar` 文件夹放入：
   - macOS / Linux：`~/.workbuddy/skills/`
   - Windows：`%USERPROFILE%\.workbuddy\skills\`
3. 确认路径为 `~/.workbuddy/skills/mcd-activity-calendar/SKILL.md`

---

## 三、配置麦当劳 MCP Token（关键步骤）

Skill 依赖麦当劳 MCP Server 取数，必须先配置 Token。

### 方式一：写进 WorkBuddy 的 MCP 配置（推荐）

编辑 `~/.workbuddy/mcp.json`（不存在则新建），添加：

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": {
        "Authorization": "Bearer 你的_TOKEN"
      }
    }
  }
}
```

保存后在 WorkBuddy 连接器管理页点「信任」启用该 MCP Server。

### 方式二：用环境变量（跑脚本时用）

```bash
export MCD_MCP_TOKEN="你的_TOKEN"
python3 scripts/collect_data.py
```

> 项目里的 `scripts/mcp_call.py` **只从环境变量读取 Token，不硬编码**，可安全开源。

---

## 四、验证安装是否成功

### 1. 检查文件

```bash
ls ~/.workbuddy/skills/mcd-activity-calendar/SKILL.md
```

### 2. 在 WorkBuddy 里试一句

对 WorkBuddy 说：

```
更新麦当劳日历
```

预期结果：调用麦当劳 MCP 采集活动/商品/优惠券数据，生成 4 个 ICS 文件，
并返回订阅地址（`assets/calendar-all.ics` 等）。

### 3. 检查 MCP 连接

```bash
# 应返回工具列表（35 个工具）
python3 scripts/mcp_call.py campaign-calendar | head -20
```

---

## 五、首次使用引导

安装后建议按下面几步完成配置（对应 PRD 4.1 引导流程）：

1. **配置 MCP Token** —— 见上文第三节
2. **选择订阅类别** —— 活动 / 收藏品 / 优惠券 / 积分权益 / 抽奖 / 主题活动
3. **设置关注城市** —— 用于门店与主题活动查询
4. **确认提醒时间** —— 默认「提前一天 09:00 提醒」
5. **是否开启定时检查** —— 授权后可创建自动化任务定期刷新
6. **获取 ICS 订阅链接** —— 添加到手机 / 电脑日历

也可以直接订阅线上已部署的日历（无需安装）：

| 日历 | 订阅地址 |
|---|---|
| ⭐ 合集（推荐） | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar-all.ics |
| 活动 | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar.ics |
| 收藏 | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar-collectibles.ics |
| 权益 | https://mcd-activity-calendar.app.workbuddy.host/assets/calendar-benefits.ics |

---

## 六、常用指令

安装后可以直接用自然语言：

| 说什么 | 会发生什么 |
|---|---|
| 更新麦当劳日历 | 采集最新数据并重新生成 ICS |
| 订阅麦当劳活动 | 给出订阅地址 + 添加步骤 |
| 帮我领券 | 调用 `auto-bind-coupons` 领取全部可用券（需授权） |
| 我有多少积分 | 调用 `query-my-account` 查询积分余额与到期 |
| 我有什么券 | 调用 `query-my-coupons` 查卡包 |
| 有哪些收藏品上新 | 调用 `mall-points-products` 列出收藏品 |
| 积分抽奖有什么奖品 | 调用 `query-lottery-info` 查看奖品（不自动抽） |
| 深圳有哪些主题派对 | 调用 `query-party-city` / `query-party-store` 查场次 |
| 附近有哪些麦当劳 | 调用 `query-nearby-stores` 查门店 |

---

## 七、卸载

```bash
rm -rf ~/.workbuddy/skills/mcd-activity-calendar
```

同时删除 `~/.workbuddy/mcp.json` 中的 `mcd-mcp` 配置段即可。

---

## 八、常见问题

**Q：WorkBuddy 里看不到这个技能？**
检查 `SKILL.md` 是否在 `skills/mcd-activity-calendar/` 的第一层（不要多套目录），
并且文件开头的 front matter（`---` 之间的 `name` / `description`）完整。

**Q：提示连接麦当劳 MCP 失败？**
先确认 Token 已激活且未过期；再确认 `mcp.json` 已启用（点「信任」）。

**Q：日历里没有内容 / 数据是旧的？**
说「更新麦当劳日历」重新采集；订阅客户端有刷新间隔（本日历声明 `REFRESH-INTERVAL:PT12H`，
即每 12 小时拉一次），iPhone 可在「日历 → 账户 → 已订阅的日历」里手动刷新。

**Q：个人积分/卡包数据会不会被别人看到？**
不会。个人数据只在你本机通过你自己的 Token 查询，
`data/summary.json`（对外页面用的数据）只含公共活动/商品/券列表。

---

## 声明

本项目为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。
项目输出仅供参考；餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。

**开发者邮箱**：931225409@qq.com

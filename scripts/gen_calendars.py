# -*- coding: utf-8 -*-
"""麦麦权益与收藏日历 —— 多类别 ICS 生成器。

把 data/ 下的活动与收藏品数据生成多个可独立订阅的 ICS 日历：
    assets/calendar.ics            活动日历（营销活动）
    assets/calendar-collectibles.ics  收藏日历（五大类收藏品/周边/玩具/积分实物）
    assets/calendar-benefits.ics   权益日历（积分兑换商品，按截止日提醒）

支持「提前一天提醒」：发售/截止前一天 09:00 通过 VALARM 提醒。

用法：
    python3 gen_calendars.py
"""
import json, os, re, datetime, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
ASSETS = os.path.join(HERE, '..', 'assets')
os.makedirs(ASSETS, exist_ok=True)

MAX_SPAN = 5

# 收藏品五大类映射（PRD 3.1）—— 从 mall-points-products 的 catName 归类
COLLECTIBLE_CATS = {
    '玩具': '开心乐园餐玩具',
    '鞋袜': 'IP 联名与限量周边',
    '周边': 'IP 联名与限量周边',
}

def load(name, default=None):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding='utf-8'))

def _still_active(down_time):
    """商品是否仍在售/未结束（down_time 为空或晚于今天）"""
    if not down_time:
        return True
    try:
        d = datetime.date.fromisoformat(str(down_time)[:10])
        return d >= datetime.date.today()
    except Exception:
        return True

def esc(s):
    s = '' if s is None else str(s)
    return s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\r\n', '\\n').replace('\n', '\\n')

def fold(line):
    if len(line.encode('utf-8')) <= 74:
        return line
    out, cur, n = [], '', 0
    for ch in line:
        cb = len(ch.encode('utf-8'))
        if n + cb > 73:
            out.append(cur)
            cur, n = ' ', 1
        n += cb
        cur += ch
    out.append(cur)
    return '\r\n'.join(out)

def ymd(s):
    return str(s)[:10].replace('-', '')

def plusday(s):
    return (datetime.date.fromisoformat(str(s)[:10]) + datetime.timedelta(days=1)).strftime('%Y%m%d')

def minusday_ts(s, hour='090000'):
    """提前一天提醒的触发时刻：日期前一天的 09:00:00（本地时间）"""
    d = datetime.date.fromisoformat(str(s)[:10]) - datetime.timedelta(days=1)
    return d.strftime('%Y%m%d') + 'T' + hour

def _date(a):
    return a.get('start_date') or a.get('date') or ''

def _end(a):
    return a.get('end_date') or a.get('endDate') or _date(a)

def span_days(a):
    try:
        s = datetime.date.fromisoformat(str(_date(a))[:10])
        e = datetime.date.fromisoformat(str(_end(a))[:10])
        return (e - s).days + 1
    except Exception:
        return 1

def segments(a):
    if span_days(a) <= MAX_SPAN:
        return [{'s': _date(a), 'e': _end(a), 'tag': ''}]
    out = [{'s': _date(a), 'e': _date(a), 'tag': '开始'}]
    if _end(a) and _end(a) != _date(a):
        out.append({'s': _end(a), 'e': _end(a), 'tag': '截止'})
    return out

def normalize_url(u):
    if not u:
        return 'https://www.mcdonalds.com.cn/'
    u = str(u).strip()
    if not u.startswith(('http://', 'https://')):
        return 'https://www.mcdonalds.com.cn/'
    if '://mcdonalds.com.cn' in u and '://www.mcdonalds.com.cn' not in u:
        u = u.replace('://mcdonalds.com.cn', '://www.mcdonalds.com.cn')
    return u

def valarm(date_str, summary):
    """提前一天 09:00 提醒（仅对未来的、有明确日期的发售/截止）"""
    try:
        d = datetime.date.fromisoformat(str(date_str)[:10])
        today = datetime.date.today()
        if d <= today:  # 已发生不补发
            return ''
        trigger = minusday_ts(date_str)
        return ('BEGIN:VALARM\r\n'
                'ACTION:DISPLAY\r\n'
                'DESCRIPTION:' + esc('提醒：' + summary) + '\r\n'
                'TRIGGER;VALUE=DATE-TIME:' + trigger + '\r\n'
                'END:VALARM\r\n')
    except Exception:
        return ''

def build_calendar(name, desc, events):
    """events: list of dict，每条含 uid/summary/desc/location/categories/url/date(s,e)/alarm_date/alarm_summary"""
    stamp = datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0',
         'PRODID:-//McCalendar//McD CN Benefits & Collectibles//CN',
         'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
         'X-WR-CALNAME:' + esc(name),
         'X-WR-TIMEZONE:Asia/Shanghai',
         'X-WR-CALDESC:' + esc(desc),
         'REFRESH-INTERVAL;VALUE=DURATION:PT12H',
         'X-PUBLISHED-TTL:PT12H']
    for ev in events:
        L.append('BEGIN:VEVENT')
        L.append('UID:' + esc(ev['uid']) + '@mccalendar')
        L.append('DTSTAMP:' + stamp)
        L.append('DTSTART;VALUE=DATE:' + ymd(ev['s']))
        L.append('DTEND;VALUE=DATE:' + plusday(ev['e']))
        L.append('SUMMARY:' + esc(ev['summary']))
        if ev.get('location'):
            L.append('LOCATION:' + esc(ev['location']))
        L.append('DESCRIPTION:' + esc(ev['desc']))
        if ev.get('categories'):
            L.append('CATEGORIES:' + esc(ev['categories']))
        if ev.get('url'):
            L.append('URL:' + ev['url'])
        if ev.get('alarm_date') and ev.get('alarm_summary'):
            L.append(valarm(ev['alarm_date'], ev['alarm_summary']))
        L.append('END:VEVENT')
    L.append('END:VCALENDAR')
    return '\r\n'.join(fold(x) for x in L) + '\r\n'

# ---------------- 活动日历 ----------------
def build_campaign_calendar():
    campaigns = load('campaigns.json', [])
    events = []
    for a in campaigns:
        if a.get('rolling'):
            continue
        for seg in segments(a):
            if seg['tag'] == '开始':
                title = a['title'] + ' · 活动上线'
            elif seg['tag'] == '截止':
                title = a['title'] + ' · 即将截止'
            else:
                title = a['title']
            link = normalize_url(a.get('coupon_link'))
            d = ['【' + (a.get('type') or '营销活动') + '】' + a['title']]
            d.append('时间：' + str(a.get('start_date', '')) + ((' 至 ' + str(a.get('end_date'))) if a.get('end_date') and a.get('end_date') != a.get('start_date') else ''))
            if a.get('highlights'):
                d.append('亮点：' + a['highlights'])
            if a.get('description'):
                d += ['', a['description']]
            if a.get('image'):
                d += ['', '图片：' + a['image']]
            d += ['', '领取优惠券/查看：' + link, '', '来源：麦当劳 MCP · 活动日历']
            events.append({
                'uid': 'camp-' + a['id'] + ('-start' if seg['tag'] == '开始' else '-end' if seg['tag'] == '截止' else ''),
                's': seg['s'], 'e': seg['e'],
                'summary': title,
                'location': a.get('region') or '全国',
                'desc': '\n'.join(d),
                'categories': (a.get('category') or '活动') + ',' + (a.get('region') or '全国'),
                'url': link,
                'alarm_date': seg['s'], 'alarm_summary': title,
            })
    ics = build_calendar('麦麦活动日历', '麦当劳营销活动 · 上线/截止提前一天提醒，点开即领券', events)
    return ics, len(campaigns), len(events)

# ---------------- 收藏日历（五大类） ----------------
def build_collectibles_calendar():
    products = load('products.json', [])
    # 收藏品 = 玩具/鞋袜/周边/实物（非派对、非读书会、非到店餐品券、非品鉴会）
    collectible_cats = {'玩具', '鞋袜'}
    def is_collectible(p):
        c = p.get('category', '')
        if c in collectible_cats:
            return True
        return False
    items = [p for p in products if is_collectible(p) and _still_active(p.get('down_time', ''))]
    events = []
    for p in items:
        name = p.get('name', '')
        up = p.get('up_time', '')[:10]
        down = p.get('down_time', '')[:10]
        if not up:
            continue
        # 仅保留未来发售/尚在发售期的
        cat = COLLECTIBLE_CATS.get(p.get('category', ''), p.get('category', '收藏品'))
        d = ['【' + cat + '】' + name]
        d.append('发售：' + up + ((' 至 ' + down) if down and down != up else ''))
        if p.get('point') and p.get('point') != '0':
            d.append('积分要求：' + str(p['point']))
        if p.get('price'):
            d.append('价格：' + str(p['price']) + ' 元')
        if p.get('selling'):
            d.append('说明：' + p['selling'])
        if p.get('image'):
            d.append('图片：' + p['image'])
        d += ['', '来源：麦当劳 MCP · 积分商城']
        link = 'https://www.mcdonalds.com.cn/news/news_list'
        events.append({
            'uid': 'coll-' + p['id'],
            's': up, 'e': down or up,
            'summary': name + ' · 上新',
            'desc': '\n'.join(d),
            'categories': cat,
            'url': link,
            'alarm_date': up, 'alarm_summary': name + ' 发售提醒',
        })
    ics = build_calendar('麦麦收藏日历', '麦当劳收藏品/联名周边/玩具上新 · 发售前一天提醒', events)
    return ics, len(items), len(events)

# ---------------- 权益日历（积分兑换到期提醒） ----------------
def build_benefits_calendar():
    products = load('products.json', [])
    # 权益 = 积分可兑换商品（point>0 且非派对/读书会）
    def is_benefit(p):
        pt = p.get('point', '0')
        try:
            return float(pt) > 0 and p.get('category', '') not in ('生日类派对', '主题类派对', '读书会', '品鉴会')
        except Exception:
            return False
    items = [p for p in products if is_benefit(p) and _still_active(p.get('down_time', ''))]
    events = []
    for p in items:
        name = p.get('name', '')
        down = p.get('down_time', '')[:10]
        up = p.get('up_time', '')[:10]
        if not down:
            continue
        # 以截止日为提醒锚点（积分兑换/权益到期）
        d = ['【积分兑换】' + name]
        d.append('可兑换：' + up + ((' 至 ' + down) if down and down != up else ''))
        d.append('所需积分：' + str(p.get('point', '0')))
        if p.get('price'):
            d.append('价格：' + str(p['price']) + ' 元')
        if p.get('selling'):
            d.append('说明：' + p['selling'])
        if p.get('image'):
            d.append('图片：' + p['image'])
        d += ['', '来源：麦当劳 MCP · 积分商城']
        link = 'https://www.mcdonalds.com.cn/news/news_list'
        events.append({
            'uid': 'benefit-' + p['id'],
            's': up or down, 'e': down,
            'summary': name + ' · 兑换截止',
            'desc': '\n'.join(d),
            'categories': '积分权益',
            'url': link,
            'alarm_date': down, 'alarm_summary': name + ' 即将截止兑换',
        })
    ics = build_calendar('麦麦权益日历', '麦当劳积分兑换/权益到期 · 截止前一天提醒', events)
    return ics, len(items), len(events)

def main():
    out = {}
    ics, nc, ne = build_campaign_calendar()
    open(os.path.join(ASSETS, 'calendar.ics'), 'w', encoding='utf-8', newline='').write(ics)
    print('活动日历 calendar.ics：活动 %d，日程 %d，%d 字节' % (nc, ne, len(ics.encode())))

    ics2, nc2, ne2 = build_collectibles_calendar()
    open(os.path.join(ASSETS, 'calendar-collectibles.ics'), 'w', encoding='utf-8', newline='').write(ics2)
    print('收藏日历 calendar-collectibles.ics：收藏品 %d，日程 %d，%d 字节' % (nc2, ne2, len(ics2.encode())))

    ics3, nc3, ne3 = build_benefits_calendar()
    open(os.path.join(ASSETS, 'calendar-benefits.ics'), 'w', encoding='utf-8', newline='').write(ics3)
    print('权益日历 calendar-benefits.ics：权益 %d，日程 %d，%d 字节' % (nc3, ne3, len(ics3.encode())))

if __name__ == '__main__':
    main()

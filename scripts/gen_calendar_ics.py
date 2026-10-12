# -*- coding: utf-8 -*-
"""把麦当劳活动数据（data/campaigns.json）生成 assets/calendar.ics。

用法：
    python3 gen_calendar_ics.py <campaigns.json> <输出 calendar.ics> [--cal-name "麦麦活动日历"]

数据字段（data/campaigns.json 里每一条活动）：
    id          稳定唯一标识（用作 UID，活动变化时保持稳定，避免日历里重复）
    title       活动名称
    start_date  开始日期 YYYY-MM-DD
    end_date    结束日期 YYYY-MM-DD（可选，缺省视为单日）
    type        活动类型（优惠券活动 / 会员活动 / 新品上市 / 主题活动 / 积分活动 ...）
    category    分类标签
    region      适用地区（全国 / 城市名）
    coupon_link 领券链接（写进 VEVENT 的 URL 字段，手机日历点开即可跳转领券）
    description 活动说明
    rolling     长期滚动开放的活动（无明确截止）设为 true，会被排除，不占满日历

订阅口径（麦当劳活动场景，与湾区 AI 日历同一套思路）：
    - 跨度 <= MAX_SPAN 天：整段显示（如限时买一送一）
    - 跨度 >  MAX_SPAN 天：只标「开始」和「截止」两天各一条，让用户
      在活动上线当天和即将结束当天各收到一次提醒（对领券活动尤其有用）
"""
import json, sys, argparse, datetime, os

ap = argparse.ArgumentParser()
ap.add_argument('src', help='campaigns.json 路径')
ap.add_argument('out', nargs='?', default='assets/calendar.ics', help='输出 calendar.ics 路径')
ap.add_argument('--cal-name', default='麦麦活动日历')
ap.add_argument('--cal-desc', default='麦当劳营销活动与优惠券 · 活动上线/截止自动提醒，点开即领券')
args = ap.parse_args()

D = json.load(open(args.src, encoding='utf-8'))
MAX_SPAN = 5

def _date(a):
    return a.get('start_date') or a.get('date') or ''

def _end(a):
    return a.get('end_date') or a.get('endDate') or _date(a)

def span(a):
    s = datetime.date.fromisoformat(str(_date(a))[:10])
    e = datetime.date.fromisoformat(str(_end(a))[:10])
    return (e - s).days + 1

def eligible(a):
    if not _date(a):
        return False
    if a.get('rolling'):
        return False
    return True

def segments(a):
    if span(a) <= MAX_SPAN:
        return [{'s': _date(a), 'e': _end(a), 'tag': ''}]
    out = [{'s': _date(a), 'e': _date(a), 'tag': '开始'}]
    if _end(a) and _end(a) != _date(a):
        out.append({'s': _end(a), 'e': _end(a), 'tag': '截止'})
    return out

def esc(s):
    s = '' if s is None else str(s)
    return s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\r\n', '\\n').replace('\n', '\\n')

# 麦当劳官网只有带 www 的域名有 DNS/HTTPS 服务；裸域名 mcdonalds.com.cn 无法解析会「无法打开网址」。
# 这里统一纠正领券链接，避免日历里出现打不开的裸域名地址。
# /news/... 推文页是真实活动页，保留；其他无意义子路径统一回首页。
MCD_HOME = 'https://www.mcdonalds.com.cn/'
MCD_NEWS_LIST = 'https://www.mcdonalds.com.cn/news/news_list'
def normalize_coupon_url(u):
    if not u:
        return MCD_HOME
    u = str(u).strip()
    if not u.startswith(('http://', 'https://')):
        u = 'https://' + u
    # 裸域名 / 无 www 前缀 → 纠正为 www 官方可达域名
    if '://mcdonalds.com.cn' in u and '://www.mcdonalds.com.cn' not in u:
        u = u.replace('://mcdonalds.com.cn', '://www.mcdonalds.com.cn')
    if '://www.mcdonalds.com.cn' not in u:
        return MCD_HOME
    # /news/ 路径是官方推文页，保留
    if '/news/' in u:
        return u
    # 其他子路径（如 /member-day）会 302 回首页，统一落到官方首页确保可达
    if u.rstrip('/') != 'https://www.mcdonalds.com.cn':
        u = MCD_HOME
    return u

def ymd(s):
    return str(s)[:10].replace('-', '')

def plusday(s):
    return (datetime.date.fromisoformat(str(s)[:10]) + datetime.timedelta(days=1)).strftime('%Y%m%d')

stamp = datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')

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

def build(rows, name):
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//McD Activity Calendar//McD CN Campaigns//CN',
         'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
         'X-WR-CALNAME:' + esc(name),
         'X-WR-TIMEZONE:Asia/Shanghai',
         'X-WR-CALDESC:' + esc(args.cal_desc + '｜跨度超过 %d 天的活动只在开始与截止两天各提醒一次' % MAX_SPAN),
         # 告诉日历客户端每 12 小时拉一次，避免等一两天才更新
         'REFRESH-INTERVAL;VALUE=DURATION:PT12H',
         'X-PUBLISHED-TTL:PT12H']
    for a in sorted(rows, key=lambda x: str(_date(x))):
        sp = span(a)
        for seg in segments(a):
            long_span = sp > MAX_SPAN
            all_day = (seg['s'] != seg['e']) or long_span
            uid = a['id'] + ('-start' if seg['tag'] == '开始' else '-end' if seg['tag'] == '截止' else '')
            L.append('BEGIN:VEVENT')
            L.append('UID:%s@mcd-activity-calendar' % uid)
            L.append('DTSTAMP:' + stamp)
            if all_day:
                L.append('DTSTART;VALUE=DATE:' + ymd(seg['s']))
                L.append('DTEND;VALUE=DATE:' + plusday(seg['e']))
            else:
                L.append('DTSTART;VALUE=DATE:' + ymd(seg['s']))
                L.append('DTEND;VALUE=DATE:' + plusday(seg['e']))
            # SUMMARY：开始/截止两条加上语义后缀，用户一眼看得出是「上线」还是「倒计时」
            if seg['tag'] == '开始':
                title = a['title'] + ' · 活动上线'
            elif seg['tag'] == '截止':
                title = a['title'] + ' · 即将截止'
            else:
                title = a['title']
            L.append('SUMMARY:' + esc(title))
            L.append('LOCATION:' + esc(a.get('region') or '全国'))
            d = ['【' + (a.get('type') or '麦当劳活动') + '】' + a['title']]
            d.append('时间：' + a.get('start_date', '') + ((' 至 ' + a['end_date']) if a.get('end_date') and a['end_date'] != a.get('start_date') else ''))
            if a.get('region'):
                d.append('适用地区：' + a['region'])
            if a.get('description'):
                d += ['', a['description']]
            link = normalize_coupon_url(a.get('coupon_link'))
            d += ['', '领取优惠券：' + link]
            d += ['', '来源：麦当劳 MCP · 活动日历']
            L.append('DESCRIPTION:' + esc('\n'.join(d)))
            L.append('CATEGORIES:' + esc((a.get('category') or a.get('type') or '麦当劳') + (',' + a['region'] if a.get('region') else '')))
            L.append('URL:' + link)
            L.append('END:VEVENT')
    L.append('END:VCALENDAR')
    return '\r\n'.join(fold(x) for x in L) + '\r\n'

rows = [a for a in D if eligible(a)]
dropped = [a for a in D if not eligible(a)]
nseg = sum(len(segments(a)) for a in rows)
split = [a for a in rows if span(a) > MAX_SPAN]
ics = build(rows, args.cal_name)
_od = os.path.dirname(os.path.abspath(args.out))
if _od:
    os.makedirs(_od, exist_ok=True)
open(args.out, 'w', encoding='utf-8', newline='').write(ics)
print('活动 %d / 排除 %d / 日程条数 %d（其中 %d 场被拆成 开始+截止）| ICS %d 字节'
      % (len(rows), len(dropped), nseg, len(split), len(ics.encode())))
print('--- 排除（长期滚动开放）---')
for a in dropped:
    print('   ', a['id'], '|', a.get('type'), '|', a['title'][:38])
print('--- 拆成 开始/截止 的（跨度 > %d 天）---' % MAX_SPAN)
for a in sorted(split, key=lambda x: -span(x)):
    print('   %4dd | %s | %s' % (span(a), a['id'], a['title'][:38]))

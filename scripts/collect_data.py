#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集麦当劳 MCP 全部数据并结构化落盘到 data/ 目录。

数据文件：
    campaigns.json      营销活动（campaign-calendar，含图片/领券 appJumpUrl）
    products.json       积分商品/收藏品/主题活动（mall-points-products，含五大类）
    coupons.json        可领优惠券（available-coupons）
    my_account.json     积分账户（query-my-account）
    my_coupons.json     我的卡包券（query-my-coupons）
    lottery.json        积分抽奖（query-lottery-info）

用法：
    python3 collect_data.py [--token TOKEN]
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_call import call

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
os.makedirs(DATA, exist_ok=True)

def sc(tool, args=None, token=None):
    r = call(tool, args, token)
    return r.get('result', {}).get('structuredContent', {})

def save(name, obj):
    p = os.path.join(DATA, name)
    json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('  ->', name, '(%d 字节)' % os.path.getsize(p))

def _norm_digits(s):
    """全角数字 → 半角"""
    full = '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
    half = '0123456789'
    return ''.join(half[full.index(c)] if c in full else c for c in s)

def _parse_dates(text):
    """从描述里解析 X月X日（至 X月X日），返回 (start, end) 或 None"""
    if not text:
        return None
    m = re.findall(r'(\d{1,2})月(\d{1,2})日', _norm_digits(text))
    if not m:
        return None
    year = 2026
    def d(mm, dd):
        return '%04d-%02d-%02d' % (year, int(mm), int(dd))
    s = d(*m[0])
    e = d(*m[1]) if len(m) >= 2 else s
    return s, e

def collect_campaigns(token):
    """campaign-calendar：解析 structuredContent.data.dailyList -> 去重活动列表。
    日期优先级：描述里解析的日期区间 > dailyList 日期；
    领券链接统一用官方推文页（App 深链 mcdapp:// 不能放进 ICS）。"""
    r = sc('campaign-calendar', None, token)
    data = r.get('data', {})
    daily = data.get('dailyList', []) or []

    # 活动标题 -> 官方推文链接（已验证可达）
    NEWS_MAP = [
        ('超值', 'https://www.mcdonalds.com.cn/news/20261008-MCF/'),
        ('厚松饼堡', 'https://www.mcdonalds.com.cn/news/20261001-breakfast/'),
        ('韩式风味蘸酱', 'https://www.mcdonalds.com.cn/news/20261008-Mcspicy/'),
        ('PEACEMINUSONE', 'https://www.mcdonalds.com.cn/news/20261008-Mcspicy/'),
        ('G-DRAGON', 'https://www.mcdonalds.com.cn/news/20261008-Mcspicy/'),
        ('龙焰', 'https://www.mcdonalds.com.cn/news/20261008-Mcspicy/'),
        ('蓝莓爆爆珠麦旋风', 'https://www.mcdonalds.com.cn/news/20261001-MaiMaiZhouMo/'),
        ('黑巧', 'https://www.mcdonalds.com.cn/news/20261008-MCF/'),
        ('麦咖啡', 'https://www.mcdonalds.com.cn/news/20261001-MaiMaiZhouMo/'),
        ('灰焰圆筒', 'https://www.mcdonalds.com.cn/news/20261001-MaiMaiZhouMo/'),
        ('麦金学期卡', 'https://www.mcdonalds.com.cn/news/20261001-MaiMaiZhouMo/'),
        ('过家家派对', 'https://www.mcdonalds.com.cn/news/20260909-HM/'),
        ('麦麦派对', 'https://www.mcdonalds.com.cn/news/20261001-MaiMaiZhouMo/'),
        ('丝巾', 'https://www.mcdonalds.com.cn/news/20261008-Mcspicy/'),
    ]
    NEWS_FALLBACK = 'https://www.mcdonalds.com.cn/news/news_list'

    def news_link(title):
        for kw, url in NEWS_MAP:
            if kw in title:
                return url
        return NEWS_FALLBACK

    seen = {}
    out = []
    for day in daily:
        date = day.get('date', '')
        for ev in day.get('events', []):
            art = ev.get('articleDto', {})
            title = (art.get('title') or '').strip()
            if not title:
                continue
            if title in seen:
                continue
            desc = art.get('content', '')
            pd = _parse_dates(desc)
            app_jump = art.get('appJumpUrl', '')
            item = {
                'id': 'camp_' + (ev.get('activityCode') or ev.get('resourceId') or re.sub(r'\W+', '', title)),
                'title': title,
                'start_date': pd[0] if pd else date,
                'end_date': pd[1] if pd else date,
                'type': '营销活动',
                'category': '活动',
                'region': '全国',
                'coupon_link': news_link(title),
                'app_jump_url': app_jump,
                'image': (art.get('imgList') or [''])[0],
                'button_text': art.get('buttonText', ''),
                'highlights': art.get('highlights', ''),
                'description': desc,
                'rolling': False,
            }
            seen[title] = item
            out.append(item)
    return out

def collect_products(token):
    """mall-points-products：积分商品/收藏品/主题活动"""
    r = sc('mall-points-products', None, token)
    items = r.get('data', []) or []
    out = []
    for p in items:
        out.append({
            'id': 'prod_' + str(p.get('spuId')),
            'spu_id': p.get('spuId'),
            'name': p.get('spuName', ''),
            'image': p.get('spuImage', ''),
            'point': p.get('point', '0'),
            'price': p.get('price', ''),
            'shop_id': p.get('shopId'),
            'category': p.get('catName', ''),
            'selling': p.get('selling', ''),
            'up_time': p.get('upTime', ''),
            'down_time': p.get('downTime', ''),
            'status': p.get('status'),
        })
    return out

def collect_coupons(token):
    r = sc('available-coupons', None, token)
    items = r.get('data', []) or []
    out = []
    for c in items:
        out.append({
            'name': c.get('couponName', ''),
            'image': c.get('couponImage', ''),
            'status': c.get('couponStatus', ''),
            'label': c.get('label', ''),
        })
    return out

def main():
    token = None
    if '--token' in sys.argv:
        token = sys.argv[sys.argv.index('--token') + 1]
    print('采集活动日历 campaign-calendar ...')
    save('campaigns.json', collect_campaigns(token))
    print('采集积分商品/收藏品 mall-points-products ...')
    save('products.json', collect_products(token))
    print('采集可领券 available-coupons ...')
    save('coupons.json', collect_coupons(token))
    print('采集积分账户 query-my-account ...')
    save('my_account.json', sc('query-my-account', None, token).get('data', {}))
    print('采集我的卡包券 query-my-coupons ...')
    save('my_coupons.json', sc('query-my-coupons', {'page': '1', 'pageSize': '200'}, token).get('data', {}))
    print('采集抽奖 query-lottery-info ...')
    save('lottery.json', sc('query-lottery-info', None, token).get('data', {}))
    # 生成前端公共数据 summary.json（只含公共数据）
    print('生成前端 summary.json ...')
    import subprocess
    subprocess.run([sys.executable, os.path.join(HERE, 'sync_summary.py')])
    print('完成')

if __name__ == '__main__':
    main()

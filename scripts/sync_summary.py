#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成前端公共数据 summary.json（只含公共数据，不含个人积分/卡包/抽奖）。

用法：
    python3 sync_summary.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

def load(name, default=None):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding='utf-8'))

def main():
    # 只含公共数据：活动、收藏品/积分商品、可领券列表
    summary = {
        'campaigns': load('campaigns.json', []),
        'products': load('products.json', []),
        'coupons': load('coupons.json', []),
    }
    out = os.path.join(DATA, 'summary.json')
    json.dump(summary, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print('summary.json 已生成（公共数据 %d 活动 / %d 商品 / %d 券），不含个人数据'
          % (len(summary['campaigns']), len(summary['products']), len(summary['coupons'])))

if __name__ == '__main__':
    main()

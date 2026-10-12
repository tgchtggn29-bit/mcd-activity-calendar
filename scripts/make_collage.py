# -*- coding: utf-8 -*-
"""把 docs/images 下的截图拼成拼图 + 生成缩略图，减小 README 图片体积。

用法：
    python3 make_collage.py <images_dir>

输出：
    - docs/images/collage-landing.png   落地页 3 张（领码/活动/地图）横排拼图
    - docs/images/collage-calendar.png  手机日历 4 张（月/列表/详情URL/领券）横排拼图
    - 每张拼图另存一份 __thumb 缩略图（宽 960px，JPEG 高压缩），README 用缩略图展示
"""
import sys, os
from PIL import Image

d = sys.argv[1] if len(sys.argv) > 1 else 'docs/images'
d = os.path.abspath(d)

LANDING = ['01-claim-code.png', '02-events.png', '03-store-map.png']
CALENDAR = ['04-calendar-month.jpg', '05-calendar-list.jpg',
            '06-event-detail-url.jpg', '07-event-detail-coupon.jpg']

def collage(files, out_name, gap=16, bg=(255, 255, 255), label_h=0):
    imgs = [Image.open(os.path.join(d, f)).convert('RGB') for f in files]
    # 统一高度到最高的一张
    H = max(im.height for im in imgs)
    scaled = []
    for im in imgs:
        w = round(im.width * H / im.height)
        scaled.append(im.resize((w, H), Image.LANCZOS))
    total_w = sum(im.width for im in scaled) + gap * (len(scaled) - 1) + 2 * gap
    total_h = H + 2 * gap + label_h
    canvas = Image.new('RGB', (total_w, total_h), bg)
    x = gap
    for im in scaled:
        canvas.paste(im, (x, gap + label_h))
        x += im.width + gap
    out = os.path.join(d, out_name)
    canvas.save(out, 'PNG', optimize=True)
    print('生成拼图', out, canvas.size, os.path.getsize(out) // 1024, 'KB')
    return out

def thumb(src, width=960, quality=78):
    im = Image.open(src).convert('RGB')
    if im.width > width:
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
    name, ext = os.path.splitext(src)
    out = name + '__thumb.jpg'
    im.save(out, 'JPEG', quality=quality, optimize=True)
    print('生成缩略图', out, im.size, os.path.getsize(out) // 1024, 'KB')
    return out

if __name__ == '__main__':
    c1 = collage(LANDING, 'collage-landing.png')
    c2 = collage(CALENDAR, 'collage-calendar.png')
    thumb(c1)
    thumb(c2)
    print('完成')

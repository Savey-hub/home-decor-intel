# -*- coding: utf-8 -*-
"""Round-3: upsert data_sources_index.json rows for Quark-cracked / dead sources.

Match existing rows by url substring; bump depth + timestamp + blocker note to
reflect the 2026-08-13 Quark browser round. Add a row if the source is missing.
Recompute summary.depth3/2/1/0_blocked. Backs up first.
"""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, '_work')
IDX = os.path.join(ROOT, 'data', 'v2', 'data_sources_index.json')

# (url_substring, new_depth, blocker_note, fallback_row_if_missing)
UPD = [
    ('compass.jinritemai.com/shop/chance', 3,
     '夸克登录态进入类目概览，抓到智能家居/家装建材近7天(08/06-08/12)大盘：支付5亿-5.5亿(+1.81%)、成交订单750万-1000万(+4.98%)、客单价¥50-100(+1.87%)，子类目全屋智能占25%-30%、卫浴建材20%-25%。本轮最硬数据。',
     {'name': '抖音电商罗盘·类目概览(智能家居/家装建材)', 'layer': 'C', 'login': '已登录'}),
    ('36kr.com/search', 3,
     '夸克进入36氪『家居』搜索页，抓到11篇窗口内文章(7-31血色黄昏/8-06靠AI半导体翻身/7-27 MORROR ART B+轮/7-13四大趋势)，已注入industry与highlights。',
     {'name': '36氪·家居搜索列表', 'layer': 'A', 'login': '免登录'}),
    ('avc-mr.com', 3,
     '夸克进入奥维云网首页，抓到8-12净化器量增价降、8-10电动轮椅半年报、8-10生态大会智慧家庭AI场景，已注入industry。',
     {'name': '奥维云网 AVC·行业资讯', 'layer': 'A', 'login': '免登录'}),
    ('jzt.jd.com/school', 3,
     '夸克进入京准通京点书院，抓到8-11/8-12数字人一键投广手册、新品前排计划、快车种草人群指南，已注入platform_jd。',
     {'name': '京准通·京点书院', 'layer': 'C', 'login': '需登录'}),
    ('school.jinritemai.com', 3,
     '夸克进入抖店学习中心，抓到8-13《抖音电商官方大促活动报名规则》等新规，已注入platform_douyin。',
     {'name': '抖店学习中心·新规速递', 'layer': 'C', 'login': '免登录'}),
    ('100ec.cn/DigitalRetail', 3,
     '夸克进入网经社数字零售台，抓到8-13当日20+条快讯(天猫AI生意管家新商版、浙江直播经济意见、拼多多AI图片合规公告)，已注入crossPlatform/policy。',
     {'name': '网经社·数字零售台快讯', 'layer': 'A', 'login': '免登录'}),
    ('caict.ac.cn', 1,
     '夸克进入信通院蓝皮书列表页成功(此前curl被WAF拦)，抓到22页目录，最新一条2026-04-03，窗口内无新蓝皮书。由WAF拦截升级为可进入但窗口内空。',
     {'name': '信通院·蓝皮书', 'layer': 'A', 'login': '免登录'}),
]

DEAD = [
    ('app_id=1838493296434206', '夸克进入返回『用户信息不存在』，该源已失效，建议剔除或替换。'),
    ('wiki/BYUAwOKIfi4sz5kgIzscUl', '夸克进入返回 Wiki-404 页面不存在，链接失效或无权限。'),
    ('wiki/UWcKwjIJIiBIu1k1zwVcgF', '夸克进入返回 Wiki-404 页面不存在，链接失效或无权限。'),
]


def main():
    if not os.path.exists(os.path.join(WORK, 'bak_data_sources_index_before_r3.json')):
        shutil.copyfile(IDX, os.path.join(WORK, 'bak_data_sources_index_before_r3.json'))
    d = json.load(open(IDX, encoding='utf-8'))
    rows = d['sources']

    def find(sub):
        return [r for r in rows if sub in r.get('url', '')]

    for sub, depth, note, fallback in UPD:
        hits = find(sub)
        if hits:
            r = max(hits, key=lambda x: x.get('depth', 0))  # update the richest existing row
            r['depth'] = depth
            r['timestamp'] = '2026-08-13'
            r['blocker'] = note
            r['login'] = fallback.get('login', r.get('login', ''))
            print('UPD', sub, '->', r['name'])
        else:
            row = {'name': fallback['name'], 'layer': fallback['layer'],
                   'url': 'https://' + sub, 'login': fallback.get('login', ''),
                   'depth': depth, 'count': '夸克抓取', 'timestamp': '2026-08-13',
                   'blocker': note}
            rows.append(row)
            print('ADD', sub, '->', row['name'])

    for sub, note in DEAD:
        hits = find(sub)
        if hits:
            for r in hits:
                r['depth'] = 0
                r['timestamp'] = '2026-08-13'
                r['blocker'] = '【已失效】' + note
                print('DEAD-UPD', sub, '->', r['name'])
        else:
            print('DEAD-miss', sub)

    # recompute summary depth buckets
    d['summary']['totalSources'] = len(rows)
    d['summary']['depth3'] = sum(1 for r in rows if r.get('depth') == 3)
    d['summary']['depth2'] = sum(1 for r in rows if r.get('depth') == 2)
    d['summary']['depth1'] = sum(1 for r in rows if r.get('depth') == 1)
    d['summary']['depth0_blocked'] = sum(1 for r in rows if r.get('depth', 0) == 0)
    d['asOf'] = '2026-08-13'

    json.dump(d, open(IDX, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('total sources:', len(rows), '| summary:', json.dumps(d['summary'], ensure_ascii=False)[:120])


if __name__ == '__main__':
    main()

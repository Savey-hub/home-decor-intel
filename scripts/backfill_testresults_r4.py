# -*- coding: utf-8 -*-
"""Backfill round-4 (Quark browser, logged-in session) testResults into data/v2/url_inventory.json.

- Updates urls[].testResult for the r4 sources (千瓜/蝉妈妈 public + 阿里内网源).
- Sets urls[].status = verdict for those ids.
- Recomputes auditSummary.statusCounts + yieldedCount, refreshes the round note.
- 内网源标注为 *_internal（数据仅入本地内部件，方案1，不进公开仓）。
Backs up to _work/bak_url_inventory_before_r4.json first.
"""
import json
import os
import shutil
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, '_work')
INV = os.path.join(ROOT, 'data', 'v2', 'url_inventory.json')

LABELS = {
    'ok_yield': '夸克登录态进入成功·有新增情报',
    'ok_yield_internal': '夸克登录态进入成功·有情报(内网,仅入本地内部件)',
    'ok_empty': '夸克进入成功·窗口内无新增',
    'ok_empty_internal': '夸克登录态进入成功·无可注入结构化数据(内网)',
    'partial': '夸克进入成功·口径不足部分可用',
    'dead': '链接失效·已确认',
    'need_login_browser': '需已登录会话·夸克当前未登录',
    'noise': '噪声源·已剔除',
}


def main():
    payload = json.load(open(os.path.join(WORK, 'inject_r4_payload.json'), encoding='utf-8'))
    results = {r['id']: r for r in payload['testResults']}

    if not os.path.exists(os.path.join(WORK, 'bak_url_inventory_before_r4.json')):
        shutil.copyfile(INV, os.path.join(WORK, 'bak_url_inventory_before_r4.json'))

    inv = json.load(open(INV, encoding='utf-8'))
    urls = inv['urls']

    updated = 0
    for u in urls:
        r = results.get(u['id'])
        if not r:
            continue
        v = r['verdict']
        tr = u.get('testResult') or {}
        tr['testedAt'] = '2026-08-13'
        tr['verdict'] = v
        tr['verdictLabel'] = LABELS.get(v, v)
        tr['yielded'] = r['yielded']
        tr['conclusion'] = r['conclusion']
        tr['round'] = 4
        tr['method'] = '本机夸克浏览器已登录会话(SendInput+扫描码)逐个进入抓取'
        u['testResult'] = tr
        u['status'] = v
        updated += 1

    # recompute audit summary
    inv['auditSummary']['testedAt'] = '2026-08-13'
    inv['auditSummary']['statusCounts'] = dict(Counter(u['status'] for u in urls))
    inv['auditSummary']['yieldedCount'] = sum(
        1 for u in urls if (u.get('testResult') or {}).get('yielded'))
    inv['auditSummary']['note'] = (
        '2026-08-13 第4轮：在已登录会话重跑用户自有付费源与阿里内网源。'
        '公开可注入：蝉妈妈品牌库(切家具建材类目,一次Ctrl+A取全量约48品牌榜,蓝盒子/公牛/顾家前三)、'
        '千瓜红书版(家居家装关键词近30天笔记505万+/互动2.26亿/企业账号占27.99%)——均为用户自有第三方付费源,已注入公开看板。'
        '阿里内网源(魔镜家装行业控比七夕环比+10.7%、FBI 4847同族控比)有效但属内网GMV,按方案1仅沉淀本地内部件、不进公开仓；'
        'Rune为按需问答式AI Agent无固定榜单、纷析与魔镜数据重叠均不入库。'
        '第3轮针对 29 个需浏览器/登录源改用本机夸克(SendInput+扫描码)逐个抓取的结论保留,每源明细见 urls[].testResult(round字段区分轮次)。')

    json.dump(inv, open(INV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print('updated testResults:', updated)
    print('statusCounts:', json.dumps(inv['auditSummary']['statusCounts'], ensure_ascii=False))
    print('yieldedCount:', inv['auditSummary']['yieldedCount'])


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Backfill round-5 (WebSearch+WebFetch public sources) testResults into data/v2/url_inventory.json.

- Updates urls[].testResult for the r5 sources.
- Sets urls[].status = verdict for those ids.
- Recomputes auditSummary.statusCounts + yieldedCount, refreshes the round note.
Backs up to _work/bak_url_inventory_before_r5.json first.
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
    'ok_yield': '公开源WebSearch/WebFetch成功·有新增情报',
    'ok_yield_internal': '内网源成功·有情报(仅入本地内部件)',
    'ok_empty': '进入成功·窗口内无新增',
    'ok_empty_internal': '内网源成功·无可注入结构化数据',
    'partial': '进入成功·口径不足部分可用',
    'dead': '链接失效·已确认',
    'need_login_browser': '需已登录会话·当前未登录',
    'noise': '噪声源·已剔除',
}


def main():
    payload = json.load(open(os.path.join(WORK, 'inject_r5_payload.json'), encoding='utf-8'))
    results = {r['id']: r for r in payload['testResults']}

    if not os.path.exists(os.path.join(WORK, 'bak_url_inventory_before_r5.json')):
        shutil.copyfile(INV, os.path.join(WORK, 'bak_url_inventory_before_r5.json'))

    inv = json.load(open(INV, encoding='utf-8'))
    urls = inv['urls']

    updated = 0
    for u in urls:
        r = results.get(u['id'])
        if not r:
            continue
        v = r['verdict']
        tr = u.get('testResult') or {}
        tr['testedAt'] = '2026-08-26'
        tr['verdict'] = v
        tr['verdictLabel'] = LABELS.get(v, v)
        tr['yielded'] = r['yielded']
        tr['conclusion'] = r['conclusion']
        tr['round'] = 5
        tr['method'] = 'WebSearch+WebFetch公开源采集(NBS/BHI/36kr/AVC/100ec/亿邦/新浪/证券时报/洛图科技等)'
        u['testResult'] = tr
        u['status'] = v
        updated += 1

    # recompute audit summary
    inv['auditSummary']['testedAt'] = '2026-08-26'
    inv['auditSummary']['statusCounts'] = dict(Counter(u['status'] for u in urls))
    inv['auditSummary']['yieldedCount'] = sum(
        1 for u in urls if (u.get('testResult') or {}).get('yielded'))
    inv['auditSummary']['note'] = (
        '2026-08-26 第5轮：WebSearch+WebFetch采集公开源(NBS/BHI/洛图科技/36氪/经济观察网/网经社/新浪财经/证券时报等)。'
        '本轮纯公开数据,无需夸克登录态。'
        '新增宏观(7月社零/房地产/70城/BHI)、平台(抖音七夕好礼季/免佣扩类/三包修订、京东818+国补+类目整顿、快手818 AI赋能)、'
        '行业(洛图智能锁H1-8.3%/摄像头H1-8.9%/奥维AI大会/经观硬仗)、商家(欧派-50~60%/索菲亚-78~85%/慕思-44~51%/居然智家-40%/'
        '志邦3连板/美的系107亿补仓顾家/爱丽跨界半导体10连板/九牧X80 AI马桶)、政策(深圳补贴/甲醛整治/绿色建材认证72种)。'
        '千瓜/蝉妈妈/阿里内网源本轮未重跑(数据仍为r4采集态),待下轮Quark登录采集刷新。')

    json.dump(inv, open(INV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print('updated testResults:', updated)
    print('statusCounts:', json.dumps(inv['auditSummary']['statusCounts'], ensure_ascii=False))
    print('yieldedCount:', inv['auditSummary']['yieldedCount'])


if __name__ == '__main__':
    main()

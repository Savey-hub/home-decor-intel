# -*- coding: utf-8 -*-
"""Backfill round-3 (Quark browser) testResults into data/v2/url_inventory.json.

- Updates urls[].testResult for the 29 browser/login sources from the r3 payload.
- Sets urls[].status = verdict for those ids (audit re-run reflects Quark round).
- Recomputes auditSummary.statusCounts + yieldedCount, appends a Quark-round note.
Backs up to _work/bak_url_inventory_before_r3.json first.
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
    'ok_yield': '夸克进入成功·有新增情报',
    'ok_empty': '夸克进入成功·窗口内无新增',
    'partial': '夸克进入成功·口径不足部分可用',
    'dead': '链接失效·已确认',
    'need_login_browser': '需已登录会话·夸克当前未登录',
    'noise': '噪声源·已剔除',
}


def main():
    payload = json.load(open(os.path.join(WORK, 'inject_r3_payload.json'), encoding='utf-8'))
    results = {r['id']: r for r in payload['testResults']}

    if not os.path.exists(os.path.join(WORK, 'bak_url_inventory_before_r3.json')):
        shutil.copyfile(INV, os.path.join(WORK, 'bak_url_inventory_before_r3.json'))

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
        tr['round'] = 3
        tr['method'] = '本机夸克浏览器(SendInput+扫描码)逐个进入抓取'
        u['testResult'] = tr
        u['status'] = v
        updated += 1

    # recompute audit summary
    inv['auditSummary']['testedAt'] = '2026-08-13'
    inv['auditSummary']['statusCounts'] = dict(Counter(u['status'] for u in urls))
    inv['auditSummary']['yieldedCount'] = sum(
        1 for u in urls if (u.get('testResult') or {}).get('yielded'))
    inv['auditSummary']['note'] = (
        '2026-08-13 全部 57 源逐个复核。第3轮针对 29 个需浏览器/登录源，'
        '按用户要求改用本机夸克浏览器(SendInput+扫描码键盘注入，绕过 Chromium 丢弃 keybd_event 的问题)逐个进入抓取，'
        '不再用 curl 代替。夸克新增有效情报源：抖音电商罗盘(家装建材近7天大盘硬数据)、36氪家居专题、奥维云网、'
        '网经社当日快讯、京准通京点书院、抖店学习中心。access-ok但窗口内无新增：信通院(由WAF拦截升级为可进入)、'
        '贝壳研究院(站点停更2023-10)、阿里研究院(停2025-03)、千川帮助中心、洞见研报、阿拉丁、千瓜/蝉妈妈(默认全类目非家居)、'
        '小红书学堂(常青课)、抖店/京麦(自家店0数据)、巨量算数(单薄)。partial：CRIC(有7月数但缺城市/口径)、京东麦头条。'
        'dead：百家号 app_id=1838493296434206(用户信息不存在)、飞书wiki两篇(Wiki-404)。'
        '仍需已登录会话重跑：纷析、魔镜、Rune、FBI 4个阿里内网源。'
        '每源明细见 urls[].testResult(round=3)。')

    json.dump(inv, open(INV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print('updated testResults:', updated)
    print('statusCounts:', json.dumps(inv['auditSummary']['statusCounts'], ensure_ascii=False))
    print('yieldedCount:', inv['auditSummary']['yieldedCount'])


if __name__ == '__main__':
    main()

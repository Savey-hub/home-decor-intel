"""Idempotent injector for round-2 (2026-08-13) harvested intelligence.

Reads _work/inject_r2_payload.json and merges into the four data JSONs.
Backs up each target to _work/bak_<name>_before_r2.json first.
"""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, '_work')

TARGETS = {
    'ip': os.path.join(ROOT, 'data', 'industry_policy.json'),
    'pd': os.path.join(ROOT, 'data', 'platform_dynamics.json'),
    'mr': os.path.join(ROOT, 'data', 'macro_realestate.json'),
    'mh': os.path.join(ROOT, 'data', 'v2', 'monthly_highlights.json'),
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def norm(s):
    return ''.join(str(s).split()).lower()


def key_of(item, keys):
    return tuple(norm(item.get(k, '')) for k in keys)


def add_unique(lst, items, keys, label):
    existing = {key_of(x, keys) for x in lst}
    added = 0
    for it in items:
        k = key_of(it, keys)
        if k in existing:
            continue
        existing.add(k)
        lst.append(it)
        added += 1
    print('  %-28s +%d (total %d)' % (label, added, len(lst)))
    return added


def add_strs(lst, items, label):
    existing = {norm(x) for x in lst}
    added = 0
    for s in items:
        if norm(s) in existing:
            continue
        existing.add(norm(s))
        lst.append(s)
        added += 1
    print('  %-28s +%d (total %d)' % (label, added, len(lst)))
    return added


def main():
    payload = load(os.path.join(WORK, 'inject_r2_payload.json'))

    data = {}
    for tag, path in TARGETS.items():
        bak = os.path.join(WORK, 'bak_%s_before_r2.json' % os.path.basename(path).replace('.json', ''))
        if not os.path.exists(bak):
            shutil.copyfile(path, bak)
        data[tag] = load(path)

    total = 0

    print('[industry_policy.json]')
    ip = data['ip']
    total += add_unique(ip['policy'], payload.get('policy', []), ('title',), 'policy')
    total += add_unique(ip['industry'], payload.get('industry', []), ('title',), 'industry')
    total += add_unique(ip['merchant'], payload.get('merchant', []), ('brand', 'date', 'type'), 'merchant')
    total += add_unique(ip['conflicts'], payload.get('conflicts_industry', []), ('item',), 'conflicts')
    total += add_strs(ip['gaps'], payload.get('gaps_industry', []), 'gaps')

    print('[platform_dynamics.json]')
    pd = data['pd']
    total += add_unique(pd['platforms']['jd'], payload.get('platform_jd', []), ('title',), 'platforms.jd')
    total += add_unique(pd['platforms']['douyin'], payload.get('platform_douyin', []), ('title',), 'platforms.douyin')
    total += add_unique(pd['crossPlatform'], payload.get('crossPlatform', []), ('title',), 'crossPlatform')

    print('[macro_realestate.json]')
    mr = data['mr']
    total += add_unique(mr['macro']['supplyChain'], payload.get('macro_supplyChain', []), ('metric', 'period'), 'macro.supplyChain')
    total += add_unique(mr['realEstate']['sales'], payload.get('macro_realEstate_sales', []), ('metric', 'period'), 'realEstate.sales')

    upd = payload.get('macro_confidence_update')
    if upd:
        hit = 0
        for it in mr['macro']['confidence']:
            if norm(upd['match']) in norm(it.get('metric', '')):
                it['yoy'] = upd['yoy']
                if upd.get('note'):
                    base = it.get('note', '').rstrip()
                    if norm(upd['note']) not in norm(base):
                        it['note'] = (base + '｜' if base else '') + upd['note']
                hit += 1
        print('  %-28s patched %d' % ('macro.confidence(yoy)', hit))

    print('[monthly_highlights.json]')
    mh = data['mh']
    for cat in ('macro', 'platform', 'policy', 'merchant'):
        items = payload.get('highlights', {}).get(cat, [])
        bad = [x for x in items if not isinstance(x, dict)]
        if bad:
            raise SystemExit('highlights.%s contains non-dict items: %r' % (cat, bad))
        total += add_unique(mh['highlights'][cat], items, ('title',), 'highlights.' + cat)

    # ---- schema guards before writing ----
    for p in ip['policy']:
        if not isinstance(p.get('subIndustry'), list):
            raise SystemExit('policy.subIndustry must be a list: %s' % p.get('title'))
    for c in pd['conflicts']:
        if not isinstance(c, str):
            raise SystemExit('platform_dynamics.conflicts must be strings')
    for c in ip['conflicts']:
        if not isinstance(c, dict):
            raise SystemExit('industry_policy.conflicts must be dicts')
    for g in ip['gaps']:
        if not isinstance(g, str):
            raise SystemExit('industry_policy.gaps must be strings')
    for cat in ('macro', 'platform', 'policy', 'merchant'):
        for x in mh['highlights'][cat]:
            if not isinstance(x, dict):
                raise SystemExit('highlights.%s non-dict' % cat)
            for req in ('date', 'title', 'impact', 'source', 'cat', 'detail', 'url'):
                x.setdefault(req, '')

    for tag, path in TARGETS.items():
        save(path, data[tag])

    print('\nTOTAL new records injected: %d' % total)


if __name__ == '__main__':
    main()

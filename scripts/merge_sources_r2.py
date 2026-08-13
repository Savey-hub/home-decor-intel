"""Merge round-2 (2026-08-13) source deep-dive rows into data/v2/data_sources_index.json."""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, '_work')
IDX = os.path.join(ROOT, 'data', 'v2', 'data_sources_index.json')


def norm(s):
    return ''.join(str(s).split())


def main():
    idx = json.load(open(IDX, encoding='utf-8'))
    pay = json.load(open(os.path.join(WORK, 'sources_r2_rows.json'), encoding='utf-8'))

    bak = os.path.join(WORK, 'bak_data_sources_index_before_r2.json')
    if not os.path.exists(bak):
        shutil.copyfile(IDX, bak)

    srcs = idx['sources']

    # 1) in-place updates on existing rows
    for up in pay.get('updates', []):
        key = norm(up['match'])
        hit = 0
        for s in srcs:
            if key in norm(s.get('name', '')):
                for k, v in up.items():
                    if k != 'match':
                        s[k] = v
                hit += 1
        print('update %-28s -> %d row(s)' % (up['match'][:28], hit))

    # 2) append new rows (idempotent by name)
    have = {norm(s.get('name')) for s in srcs}
    added = 0
    for r in pay.get('rows', []):
        if norm(r['name']) in have:
            continue
        have.add(norm(r['name']))
        srcs.append(r)
        added += 1
    print('rows appended: %d (total %d)' % (added, len(srcs)))

    # 3) summary patch + recompute depth stats
    idx['summary'].update(pay.get('summaryPatch', {}))
    idx['summary']['totalSources'] = len(srcs)
    for d in (3, 2, 1):
        idx['summary']['depth%d' % d] = sum(1 for s in srcs if s.get('depth') == d)
    idx['summary']['depth0_blocked'] = sum(1 for s in srcs if s.get('depth') == 0)
    idx['asOf'] = '2026-08-13'

    # 4) guard: every row must carry the fields the dashboard table renders
    req = ('name', 'layer', 'url', 'login', 'depth', 'count', 'timestamp', 'blocker')
    for s in srcs:
        for k in req:
            if k not in s:
                raise SystemExit('source row missing %s: %s' % (k, s.get('name')))
        if s['layer'] not in idx['layers'] and '/' not in s['layer']:
            raise SystemExit('unknown layer %r on %s' % (s['layer'], s['name']))

    json.dump(idx, open(IDX, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('depth3=%d depth2=%d depth1=%d depth0=%d total=%d' % (
        idx['summary']['depth3'], idx['summary']['depth2'],
        idx['summary']['depth1'], idx['summary']['depth0_blocked'],
        idx['summary']['totalSources']))


if __name__ == '__main__':
    main()

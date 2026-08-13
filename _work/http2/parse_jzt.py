import sys, re, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = sys.argv[1]
t = open(path, encoding='utf-8').read()
# unescape \" sequences to make JSON-ish parsing easier on both variants
variants = [t, t.replace('\\"', '"').replace('\\\\', '\\')]
items = {}
pat = re.compile(r'\{"modelId":.*?\}', re.S)
for v in variants:
    # find each occurrence of releaseDate and grab surrounding object heuristically
    for m in re.finditer(r'"releaseDate":"(\d{4}-\d{2}-\d{2})[^"]*"', v):
        s = v.rfind('{', 0, m.start())
        e = v.find('}', m.end())
        if s == -1 or e == -1:
            continue
        seg = v[s:e + 1]
        tm = re.search(r'"title":"(.*?)","', seg)
        cid = re.search(r'"contentId":"(\d+)"', seg)
        desc = re.search(r'"description":"(.*?)","', seg)
        link = re.search(r'"link":"(.*?)"', seg)
        views = re.search(r'"views":(\d+)', seg)
        title = tm.group(1) if tm else ''
        if not title:
            continue
        key = (cid.group(1) if cid else title)
        items[key] = {
            'date': m.group(1),
            'title': title,
            'contentId': cid.group(1) if cid else '',
            'desc': desc.group(1) if desc else '',
            'link': link.group(1) if link else '',
            'views': views.group(1) if views else '',
        }
print('TOTAL ITEMS', len(items))
kws = ['家装', '家居', '建材', '卫浴', '灯具', '瓷砖', '涂料', '地板', '五金', '家具', '装修', '厨卫', '厨具', '家电']
win = [v for v in items.values() if '2026-07-07' <= v['date'] <= '2026-08-13']
print('=== IN WINDOW 2026-07-07..2026-08-13:', len(win))
for v in sorted(win, key=lambda x: x['date']):
    hit = [k for k in kws if k in v['title'] + v['desc']]
    print('%s | %s | cid=%s | views=%s | HIT=%s' % (v['date'], v['title'], v['contentId'], v['views'], ','.join(hit)))
    if v['desc']:
        print('    DESC:', v['desc'][:400])
    if v['link']:
        print('    LINK:', v['link'])
print()
print('=== ALL DATES RANGE', min(v['date'] for v in items.values()), max(v['date'] for v in items.values()))
print('=== 2026-06..2026-08 items with home keywords:')
for v in sorted(items.values(), key=lambda x: x['date']):
    if v['date'] >= '2026-06-01' and any(k in v['title'] + v['desc'] for k in kws):
        print('%s | %s | cid=%s' % (v['date'], v['title'], v['contentId']))

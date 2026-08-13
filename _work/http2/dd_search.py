import sys, json, urllib.parse, urllib.request, datetime, time, os, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'


def get(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Referer': 'https://school.jinritemai.com/doudian/web/home',
        'Accept': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode('utf-8'))


def ts(x):
    try:
        return datetime.datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d')
    except Exception:
        return str(x)


KWS = ['家装', '家具', '建材', '卫浴', '灯具', '瓷砖', '涂料', '地板', '五金', '家居', '装修', '厨卫', '床上用品', '定制家居', '智能家居']
seen = {}
for kw in KWS:
    for page in (1, 2):
        u = 'https://school.jinritemai.com/api/eschool/v2/library/article/search?keyword=%s&page=%d&page_size=20' % (urllib.parse.quote(kw), page)
        try:
            d = get(u)
        except Exception as e:
            print('ERR', kw, page, e)
            continue
        arts = (d.get('data') or {}).get('articles') or []
        for a in arts:
            aid = a['id']
            nm = re.sub(r'</?em>', '', a.get('name', ''))
            rec = seen.setdefault(aid, {'id': aid, 'name': nm, 'create': ts(a.get('create_timestamp')),
                                        'update': ts(a.get('update_timestamp')), 'views': a.get('view_count'),
                                        'tags': a.get('tags'), 'kw': set(), 'obj_type': a.get('obj_type')})
            rec['kw'].add(kw)
        time.sleep(0.2)

print('TOTAL unique', len(seen))
print()
print('=== items with create OR update in 2026-07-01..2026-08-13 ===')
rows = []
for r in seen.values():
    if ('2026-07-01' <= r['create'] <= '2026-08-13') or ('2026-07-01' <= r['update'] <= '2026-08-13'):
        rows.append(r)
for r in sorted(rows, key=lambda x: x['update']):
    print('%s create=%s upd=%s views=%s | %s | kw=%s' % (r['id'], r['create'], r['update'], r['views'], r['name'], ','.join(sorted(r['kw']))))
    print('    tags:', r['tags'])
    print('    URL: https://school.jinritemai.com/doudian/web/article/%s' % r['id'])
json.dump({k: {**v, 'kw': sorted(v['kw'])} for k, v in seen.items()}, open('id53_search_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

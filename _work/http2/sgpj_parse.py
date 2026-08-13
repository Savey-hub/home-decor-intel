import re, sys, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
LO, HI = '2026-07-07', '2026-08-13'
res = {}
for f in sorted(glob.glob('id31_new_*.raw.txt')):
    d = open(f, encoding='utf-8').read()
    rows = re.split(r'class="tr1"', d)[1:]
    for r in rows:
        r = r[:r.find('</tr>') if '</tr>' in r else len(r)]
        tm = re.search(r'<a\s+href="(https://www\.sgpjbg\.com\.cn/[^"]+)"[^>]*title="([^"]+)"', r)
        if not tm:
            continue
        url, title = tm.group(1), tm.group(2)
        tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        plain = [re.sub(r'\s+', '', re.sub(r'(?s)<[^>]+>', '', t)) for t in tds]
        dm = None
        for p in plain:
            m = re.fullmatch(r'20\d\d-\d\d-\d\d', p)
            if m: dm = p; break
        date = dm or 'NA'
        if LO <= date <= HI:
            res[url] = (date, title, url, ' / '.join([p for p in plain if p]), f.split('_')[2].split('.')[0])
for k, v in sorted(res.items(), key=lambda x: x[1][0], reverse=True):
    print(v[0], '|', v[1])
    print('   ', v[2])
    print('    META:', v[3], '| kw=', v[4])
print('TOTAL in window:', len(res))

import re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p = sys.argv[1]
d = open(p, encoding='utf-8').read()
# find result rows: anchors to /baogao/ or /report/ with title attr
seen = set()
for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', d, re.S):
    href, inner = m.group(1), m.group(2)
    if not re.search(r'/(baogao|report|zhengce|shuju|heji)', href):
        continue
    t = re.sub(r'(?s)<[^>]+>', '', inner)
    t = re.sub(r'\s+', '', t)
    if len(t) < 6:
        continue
    if (href, t) in seen: continue
    seen.add((href, t))
    print(href, '|', t)
print('---DATES---')
for m in re.finditer(r'(202[4-6]-\d{2}-\d{2})', d):
    pass

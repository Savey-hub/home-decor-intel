import json, sys, re, glob, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def walk(o, out):
    if isinstance(o, dict):
        if 'insert' in o:
            v = o['insert']
            if isinstance(v, str):
                out.append(v)
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, dict) and 'src' in v2:
                        out.append('[IMG]')
                    elif isinstance(v2, str) and v2.startswith('http'):
                        out.append('[URL:%s]' % v2)
                    else:
                        out.append('[%s]' % k2)
            return
        for k, v in o.items():
            walk(v, out)
    elif isinstance(o, list):
        for i in o:
            walk(i, out)

for f in sorted(glob.glob('id53_body_*.json')):
    try:
        j = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print('== %s LOADFAIL %s' % (f, e)); continue
    d = (j.get('data') or {})
    ai = d.get('article_info') or d
    name = ai.get('name') or ai.get('title')
    c = ai.get('content') or ''
    out = []
    if c:
        try:
            cj = json.loads(c)
            walk(cj, out)
        except Exception as e:
            out.append('[CONTENT_PARSE_FAIL %s] %s' % (e, c[:2000]))
    txt = ''.join(out)
    txt = re.sub(r'\n{3,}', '\n\n', txt)
    base = f.replace('.json', '.body.txt')
    open(base, 'w', encoding='utf-8').write('TITLE: %s\n\n%s' % (name, txt))
    print('== %s | %s | bodylen=%d' % (f, name, len(txt)))
    print(txt[:1800].replace('\n', ' ')[:1800])
    print('-' * 60)

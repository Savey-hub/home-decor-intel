import sys, re, json, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def extract(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    meta = {}
    m = re.search(r'"contentId":"(\d+)","title":"(.*?)","description":"(.*?)","releaseDate":"([\d\- :]+)"', t)
    if m:
        meta = dict(contentId=m.group(1), title=m.group(2), description=m.group(3), releaseDate=m.group(4))
    else:
        m2 = re.search(r'(?is)<title>(.*?)</title>', t)
        meta = dict(title=m2.group(1) if m2 else '', releaseDate='', description='', contentId='')
        m3 = re.search(r'"releaseDate":"([\d\- :]+)"', t)
        if m3:
            meta['releaseDate'] = m3.group(1)
    # extract the escaped txt json
    i = t.find('"txt":"')
    body = ''
    if i != -1:
        j = i + 7
        # find end: unescaped quote
        k = j
        while k < len(t):
            if t[k] == '\\':
                k += 2
                continue
            if t[k] == '"':
                break
            k += 1
        esc = t[j:k]
        try:
            arr = json.loads(json.loads('"' + esc + '"'))
        except Exception as e:
            try:
                arr = json.loads(esc.encode().decode('unicode_escape'))
            except Exception:
                arr = None
                body = 'PARSE_FAIL: %s' % e
        if arr is not None:
            out = []

            def walk(node, depth=0):
                if isinstance(node, list):
                    for n in node:
                        walk(n, depth)
                    return
                if not isinstance(node, dict):
                    return
                if 'text' in node and isinstance(node['text'], str):
                    out.append(node['text'])
                    return
                typ = node.get('type', '')
                if typ in ('p', 'list', 'table-row'):
                    out.append('\n')
                if typ == 'table-cell':
                    out.append(' | ')
                if node.get('url'):
                    out.append('[URL:%s]' % node['url'])
                if node.get('src'):
                    out.append('[IMG:%s]' % node['src'])
                walk(node.get('children', []), depth + 1)
            walk(arr)
            body = ''.join(out)
            body = re.sub(r'\n\s*\n+', '\n', body)
            body = re.sub(r'( \| )+\n', '\n', body)
    return meta, body


for p in sys.argv[1:]:
    meta, body = extract(p)
    print('=' * 100)
    print('FILE:', os.path.basename(p))
    print('TITLE:', meta.get('title'))
    print('DATE:', meta.get('releaseDate'))
    print('DESC:', meta.get('description'))
    print('URL: https://jzt.jd.com/school/course/detail?contentId=%s' % meta.get('contentId'))
    print('-' * 60)
    print(body.strip()[:6000])
    out = os.path.splitext(p)[0] + '.body.txt'
    open(out, 'w', encoding='utf-8').write('TITLE: %s\nDATE: %s\nDESC: %s\n\n%s' % (meta.get('title'), meta.get('releaseDate'), meta.get('description'), body))

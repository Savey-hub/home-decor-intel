import sys, gzip, re, os, io, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def load(path):
    d = open(path, 'rb').read()
    if d[:2] == b'\x1f\x8b':
        try:
            d = gzip.decompress(d)
        except Exception:
            import zlib
            d = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(d)
    # detect charset
    head = d[:4000].decode('latin1', 'replace').lower()
    enc = 'utf-8'
    m = re.search(r'charset=["\']?([\w\-]+)', head)
    if m:
        e = m.group(1).lower()
        if e in ('gb2312', 'gbk', 'gb18030'):
            enc = 'gb18030'
        elif e.startswith('utf'):
            enc = 'utf-8'
    try:
        t = d.decode(enc)
    except Exception:
        try:
            t = d.decode('gb18030')
        except Exception:
            t = d.decode('utf-8', 'replace')
    return t, enc

def strip(t):
    t = re.sub(r'(?is)<script.*?</script>', ' ', t)
    t = re.sub(r'(?is)<style.*?</style>', ' ', t)
    t = re.sub(r'(?s)<!--.*?-->', ' ', t)
    t = re.sub(r'(?s)<[^>]+>', '\n', t)
    import html
    t = html.unescape(t)
    t = re.sub(r'[ \t\r\xa0]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t.strip()

if __name__ == '__main__':
    p = sys.argv[1]
    t, enc = load(p)
    base = os.path.splitext(p)[0]
    open(base + '.raw.txt', 'w', encoding='utf-8').write(t)
    st = strip(t)
    open(base + '.txt', 'w', encoding='utf-8').write(st)
    print('ENC=%s rawlen=%d textlen=%d' % (enc, len(t), len(st)))
    m = re.search(r'(?is)<title>(.*?)</title>', t)
    print('TITLE=', (m.group(1).strip() if m else 'NONE'))
    kws = ['家装', '家居', '建材', '卫浴', '灯具', '瓷砖', '涂料', '地板', '五金', '家具', '装修', '厨卫']
    print('KW ' + ' '.join('%s=%d' % (k, st.count(k)) for k in kws))

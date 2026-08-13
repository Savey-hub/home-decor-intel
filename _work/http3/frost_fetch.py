import re, time, urllib.request, json

HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
TAGS = ["INDUSTRY-RESEARCH", "BEST-PRACTICES", "MARKET-NEWS", "TREND-RESEARCH"]
KW = ["家居", "家装", "建材", "卫浴", "家具", "灯具", "照明", "瓷砖", "陶瓷", "涂料", "地板",
      "五金", "定制", "装修", "装饰", "装潢", "厨", "橱柜", "衣柜", "门窗", "水泥", "住房",
      "房地产", "地产", "楼市", "精装", "软装", "沙发", "床垫", "睡眠", "人居", "建筑"]

allrec = []
for tag in TAGS:
    for page in range(1, 7):
        url = f"https://www.frostchina.com/content/insight?page={page}&query[tag]={tag}"
        try:
            req = urllib.request.Request(url, headers=HDRS)
            h = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        except Exception as e:
            print("FAIL", tag, page, repr(e)); break
        t = re.sub(r"<script.*?</script>", "", h, flags=re.S)
        found = 0
        for m in re.finditer(r'href="(/content/insight/detail/[a-f0-9]+)"[^>]*>(.*?)</a>', t, re.S):
            txt = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", m.group(2))).strip()
            dm = re.match(r"(\d{4}/\d{2}/\d{2})\s*(.*)", txt)
            if dm:
                allrec.append((dm.group(1), dm.group(2).strip(), "https://www.frostchina.com" + m.group(1), tag))
                found += 1
        print(f"{tag} p{page}: {found} items")
        if found == 0: break
        time.sleep(1.0)

seen = set(); rec = []
for d, t, u, tag in allrec:
    if u in seen: continue
    seen.add(u); rec.append((d, t, u, tag))
rec.sort(reverse=True)
print("\nTOTAL uniq", len(rec), "range", rec[-1][0] if rec else "-", "->", rec[0][0] if rec else "-")
with open("frost_all.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(f"{d} | {t} | {u} | {tag}" for d, t, u, tag in rec))

win = [r for r in rec if "2026/07/07" <= r[0] <= "2026/08/13"]
print("IN WINDOW", len(win))
print("\n=== HOME-RELATED HITS (in window) ===")
n = 0
for d, t, u, tag in win:
    if any(k in t for k in KW):
        print(f"{d} | {t} | {u} | {tag}"); n += 1
print("hits", n)
print("\n=== HOME-RELATED HITS (any date) ===")
for d, t, u, tag in rec:
    if any(k in t for k in KW):
        print(f"{d} | {t} | {u} | {tag}")

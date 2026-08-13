import json, time, urllib.request, urllib.parse, os

COMPANIES = [
    ("603833", "9900029667", "欧派家居", "sse"),
    ("002572", "9900019037", "索菲亚", "szse"),
    ("603801", "9900032419", "志邦家居", "sse"),
    ("603180", "9900030658", "金牌家居", "sse"),
    ("603816", "9900027317", "顾家家居", "sse"),
    ("001323", "9900046964", "慕思股份", "szse"),
    ("001322", "9900047305", "箭牌家居", "szse"),
    ("603385", "9900030578", "惠达卫浴", "sse"),
    ("003012", "9900035896", "东鹏控股", "szse"),
    ("002918", "9900033052", "蒙娜丽莎", "szse"),
    ("603737", "9900032852", "三棵树", "sse"),
    ("000786", "gssz0000786", "北新建材", "szse"),
    ("603195", "9900037723", "公牛集团", "sse"),
    ("603515", "9900026533", "欧普照明", "sse"),
]

URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
HDRS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "http://www.cninfo.com.cn/new/index",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

out = {}
for code, org, name, col in COMPANIES:
    data = {
        "pageNum": "1", "pageSize": "50", "column": col, "tabName": "fulltext",
        "plate": "", "stock": f"{code},{org}", "searchkey": "", "secid": "",
        "category": "", "trade": "", "seDate": "2026-07-07~2026-08-13",
        "sortName": "", "sortType": "", "isHLtitle": "true",
    }
    body = urllib.parse.urlencode(data).encode()
    try:
        req = urllib.request.Request(URL, data=body, headers=HDRS)
        with urllib.request.urlopen(req, timeout=40) as r:
            j = json.loads(r.read().decode("utf-8"))
        anns = j.get("announcements") or []
        out[name] = {"code": code, "total": j.get("totalRecordNum"), "items": [
            {"title": a["announcementTitle"], "time": time.strftime("%Y-%m-%d", time.localtime(a["announcementTime"] / 1000)),
             "url": "http://static.cninfo.com.cn/" + a["adjunctUrl"], "id": a["announcementId"]}
            for a in anns]}
        print(f"OK {name} {code} total={j.get('totalRecordNum')} got={len(anns)}")
    except Exception as e:
        out[name] = {"code": code, "error": repr(e)}
        print(f"FAIL {name} {code} {e!r}")
    time.sleep(1.2)

with open("cninfo_all.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

KEY = ["业绩预告", "半年度报告", "半年报", "中期报告", "业绩快报", "主要经营数据", "经营数据"]
print("\n===== KEY ANNOUNCEMENTS =====")
lines = []
for name, d in out.items():
    for it in d.get("items", []):
        if any(k in it["title"] for k in KEY):
            lines.append(f"{it['time']} | {name}({d['code']}) | {it['title']} | {it['url']}")
for l in sorted(lines):
    print(l)
with open("cninfo_key.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(lines)))

import json, time, urllib.request, urllib.parse

COMPANIES = [
    ("001386", "9900053816", "马可波罗", "szse"),
    ("603008", "9900023007", "ST喜临门", "sse"),
]
URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
HDRS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "http://www.cninfo.com.cn/new/index",
}
out = {}
for code, org, name, col in COMPANIES:
    data = {"pageNum": "1", "pageSize": "50", "column": col, "tabName": "fulltext",
            "plate": "", "stock": f"{code},{org}", "searchkey": "", "secid": "",
            "category": "", "trade": "", "seDate": "2026-07-07~2026-08-13",
            "sortName": "", "sortType": "", "isHLtitle": "true"}
    req = urllib.request.Request(URL, data=urllib.parse.urlencode(data).encode(), headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            j = json.loads(r.read().decode("utf-8"))
        anns = j.get("announcements") or []
        print(f"OK {name} {code} total={j.get('totalRecordNum')}")
        out[name] = []
        for a in anns:
            t = time.strftime("%Y-%m-%d", time.localtime(a["announcementTime"] / 1000))
            print("   ", t, "|", a["announcementTitle"][:80], "|", "http://static.cninfo.com.cn/" + a["adjunctUrl"])
            out[name].append({"time": t, "title": a["announcementTitle"], "url": "http://static.cninfo.com.cn/" + a["adjunctUrl"]})
    except Exception as e:
        print("FAIL", name, repr(e))
    time.sleep(1.2)
json.dump(out, open("cninfo_extra.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

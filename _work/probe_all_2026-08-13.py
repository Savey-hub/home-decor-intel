# -*- coding: utf-8 -*-
"""逐个实测 url_inventory.json 中全部入口的可达性。
输出: _work/probe_2026-08-13.txt (UTF-8)
判定:
  OK        HTTP 200 且正文长度 > 2000
  THIN      HTTP 200 但正文很短(疑似 JS 单页/需渲染)
  JSAPP     正文含 <div id="app"> / __NUXT__ / react-root 且可见文字极少
  LOGIN     正文命中 登录/login 关键词且可见文字少
  HTTP_xxx  非 200
  ERR       连接异常(超时/DNS/TLS/被拦)
"""
import json, re, io, sys, os, ssl, time
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(ROOT, "data", "v2", "url_inventory.json")
OUT = os.path.join(ROOT, "_work", "probe_2026-08-13.txt")
RAW = os.path.join(ROOT, "_work", "probe_raw_2026-08-13.json")

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

TAG_RE = re.compile(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>")
STRIP_RE = re.compile(r"(?s)<[^>]+>")


def visible_text(html):
    h = TAG_RE.sub(" ", html)
    h = STRIP_RE.sub(" ", h)
    h = re.sub(r"&[a-zA-Z#0-9]{2,8};", " ", h)
    return re.sub(r"\s+", " ", h).strip()


def probe(item):
    url = item["url"]
    rec = {"id": item["id"], "name": item["name"], "url": url,
           "oldStatus": item["status"], "layer": item.get("layer", "")}
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
            body = r.read(600000)
            rec["code"] = r.getcode()
            rec["finalUrl"] = r.geturl()
            enc = "utf-8"
            ct = r.headers.get("Content-Type", "")
            m = re.search(r"charset=([\w-]+)", ct, re.I)
            if m:
                enc = m.group(1)
            html = body.decode(enc, "replace")
            if "charset=gb" in html[:2000].lower() and enc.lower().startswith("utf"):
                html = body.decode("gb18030", "replace")
    except urllib.error.HTTPError as e:
        rec["code"] = e.code
        try:
            html = e.read(200000).decode("utf-8", "replace")
        except Exception:
            html = ""
        rec["finalUrl"] = url
    except Exception as e:
        rec["code"] = 0
        rec["err"] = "%s: %s" % (type(e).__name__, str(e)[:160])
        html = ""
        rec["finalUrl"] = url
    rec["ms"] = int((time.time() - t0) * 1000)
    rec["htmlLen"] = len(html)
    vt = visible_text(html)
    rec["textLen"] = len(vt)
    rec["head"] = vt[:220]
    tm = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    rec["title"] = re.sub(r"\s+", " ", tm.group(1)).strip()[:100] if tm else ""

    low = html.lower()
    if rec["code"] == 0:
        rec["verdict"] = "ERR"
    elif rec["code"] != 200:
        rec["verdict"] = "HTTP_%d" % rec["code"]
    elif rec["textLen"] > 2000:
        rec["verdict"] = "OK"
    else:
        jsapp = any(k in low for k in ['id="app"', "id='app'", "__nuxt__",
                                       "react-root", 'id="root"', "__next_data__",
                                       "window.__initial"])
        loginish = any(k in vt for k in ["登录", "登陆"]) or "login" in low
        if loginish and rec["textLen"] < 800:
            rec["verdict"] = "LOGIN"
        elif jsapp:
            rec["verdict"] = "JSAPP"
        else:
            rec["verdict"] = "THIN"
    return rec


def main():
    inv = json.load(open(INV, encoding="utf-8"))
    items = [x for x in inv["urls"]]
    with ThreadPoolExecutor(max_workers=10) as ex:
        recs = list(ex.map(probe, items))
    recs.sort(key=lambda x: x["id"])
    json.dump(recs, open(RAW, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    with io.open(OUT, "w", encoding="utf-8") as f:
        from collections import Counter
        c = Counter(r["verdict"] for r in recs)
        f.write("探测时间 2026-08-13  共 %d 个入口\n" % len(recs))
        f.write("判定分布: %s\n\n" % dict(c))
        f.write("%-3s %-7s %-8s %-18s %-7s %-7s %s\n" %
                ("id", "旧状态", "判定", "名称", "html", "text", "title / err"))
        f.write("-" * 130 + "\n")
        for r in recs:
            f.write("%-3s %-7s %-8s %-18s %-7s %-7s %s\n" % (
                r["id"], r["oldStatus"][:7], r["verdict"], r["name"][:18],
                r["htmlLen"], r["textLen"],
                (r.get("err") or r.get("title") or "")[:70]))
        f.write("\n\n===== 逐条明细 =====\n")
        for r in recs:
            f.write("\n[%s] %s  <%s>\n" % (r["id"], r["name"], r["url"]))
            f.write("  判定=%s code=%s ms=%s html=%s text=%s\n" %
                    (r["verdict"], r["code"], r["ms"], r["htmlLen"], r["textLen"]))
            if r.get("finalUrl") and r["finalUrl"] != r["url"]:
                f.write("  跳转->%s\n" % r["finalUrl"])
            if r.get("err"):
                f.write("  异常: %s\n" % r["err"])
            if r.get("title"):
                f.write("  标题: %s\n" % r["title"])
            if r.get("head"):
                f.write("  正文首段: %s\n" % r["head"])
    print("done ->", OUT)
    print(dict(Counter(r["verdict"] for r in recs)) if True else "")


if __name__ == "__main__":
    from collections import Counter
    main()

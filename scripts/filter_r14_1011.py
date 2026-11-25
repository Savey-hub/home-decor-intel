# -*- coding: utf-8 -*-
"""R14补充：所有动态板块仅保留2026-10-01及以后的条目，11月优先、10月其后。"""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
CUT = "2026-10-01"

def date_of(it, *keys):
    for k in keys:
        v = str(it.get(k, "") or "")
        m = re.search(r"2026[-年/](\d{1,2})[-月/](\d{1,2})", v)
        if m:
            return "2026-%02d-%02d" % (int(m.group(1)), int(m.group(2)))
    return ""

def keep_dynamic(it):
    d = date_of(it, "date", "publishDate", "issueDate", "effectiveDate")
    return bool(d) and d >= CUT

def sort_desc(items, *keys):
    return sorted(items, key=lambda it: date_of(it, *keys) or "0000", reverse=True)

def is_sep_single(period):
    p = str(period or "")
    return bool(re.match(r"^2026年9月(单月)?$", p)) or "（9月单月）" in p

# ---- macro_realestate ----
m = json.load(open("data/macro_realestate.json", encoding="utf-8"))
removed = 0
for arr in ("retailSales", "wholesale", "supplyChain", "confidence"):
    old = m["macro"][arr]; new = []
    for it in old:
        pd = date_of(it, "publishDate")
        if pd >= CUT and not is_sep_single(it.get("period")):
            new.append(it)
        else:
            removed += 1
    m["macro"][arr] = new
for arr in ("sales", "investment", "newStart", "pricing", "confidence"):
    old = m["realEstate"][arr]; new = []
    for it in old:
        pd = date_of(it, "publishDate")
        if pd >= CUT and not is_sep_single(it.get("period")):
            new.append(it)
        else:
            removed += 1
    m["realEstate"][arr] = new
m["gaps"] = [g for g in m["gaps"] if date_of({"d": g}, "d") == "" or g >= CUT or "Round 14" in g or "10" in g[:12]]
json.dump(m, open("data/macro_realestate.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- platform_dynamics ----
p = json.load(open("data/platform_dynamics.json", encoding="utf-8"))
for arr in list(p["platforms"].keys()):
    old = p["platforms"][arr]
    new = [it for it in old if keep_dynamic(it)]
    removed += len(old) - len(new)
    p["platforms"][arr] = sort_desc(new, "date", "publishDate")
for arr in ("crossPlatform", "keyBrandMoves"):
    if isinstance(p.get(arr), list):
        old = p[arr]
        new = [it for it in old if keep_dynamic(it)]
        removed += len(old) - len(new)
        p[arr] = sort_desc(new, "date", "publishDate")
p["gaps"] = [g for g in p["gaps"] if "Round 14" in g or "10—11" in g or "双11" in g or "蝉妈妈" in g]
json.dump(p, open("data/platform_dynamics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- industry_policy ----
y = json.load(open("data/industry_policy.json", encoding="utf-8"))
for arr in ("policy", "industry", "merchant"):
    old = y[arr]
    new = [it for it in old if keep_dynamic(it)]
    removed += len(old) - len(new)
    y[arr] = sort_desc(new, "date", "publishDate", "issueDate")
if isinstance(y.get("platformRules"), list):
    old = y["platformRules"]
    new = [it for it in old if keep_dynamic(it)]
    removed += len(old) - len(new)
    y["platformRules"] = sort_desc(new, "date", "publishDate", "issueDate")
y["gaps"] = [g for g in y["gaps"] if "Round 14" in g or "10—11" in g or "广东" in g]
json.dump(y, open("data/industry_policy.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- monthly_highlights：10—11月专题，11月在前 ----
h = json.load(open("data/v2/monthly_highlights.json", encoding="utf-8"))
for g in ("macro", "platform", "policy", "merchant"):
    old = h["highlights"][g]
    new = [it for it in old if keep_dynamic(it)]
    removed += len(old) - len(new)
    h["highlights"][g] = sort_desc(new, "date", "publishDate")
json.dump(h, open("data/v2/monthly_highlights.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("REMOVED_PRE_OCT", removed)
print("monthly counts:", {g: len(h["highlights"][g]) for g in h["highlights"]})
print("platform counts:", {k: len(v) for k, v in p["platforms"].items()})
print("policy/industry/merchant:", len(y["policy"]), len(y["industry"]), len(y["merchant"]))

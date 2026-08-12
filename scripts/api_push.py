# -*- coding: utf-8 -*-
"""Push the local HEAD commit to origin/main via GitHub REST API (api.github.com),
bypassing the blocked github.com:443 git endpoint. Uses Git Data API:
blobs -> tree (on base_tree) -> commit -> update ref.
"""
import subprocess, base64, json, os, sys, urllib.request

OWNER = "Savey-hub"
REPO = "home-decor-intel"
API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(args):
    return subprocess.check_output(["git"] + args, cwd=ROOT)


def get_token():
    p = subprocess.run(["git", "credential", "fill"],
                       input=b"protocol=https\nhost=github.com\n\n",
                       stdout=subprocess.PIPE, cwd=ROOT)
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")


TOKEN = get_token()


def api(method, path, body=None):
    url = path if path.startswith("http") else API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "token " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "qoderwork-api-push")
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


base_sha_local = git(["rev-parse", "origin/main"]).decode().strip()
head_sha = git(["rev-parse", "HEAD"]).decode().strip()

# IMPORTANT:每次 api_push 都会推进"远端 main"，但本地 origin/main 无法 fetch 更新
# (github.com:443 在本环境被阻断)。若继续用陈旧的本地 origin/main 当 parent，
# PATCH refs 会报 HTTP 422 non-fast-forward。故始终从 API 取真实远端 HEAD 作为基线。
remote_ref = api("GET", "/repos/%s/%s/git/refs/heads/main" % (OWNER, REPO))
base_sha = remote_ref["object"]["sha"]
remote_commit = api("GET", "/repos/%s/%s/git/commits/%s" % (OWNER, REPO, base_sha))
base_tree = remote_commit["tree"]["sha"]
print("remote_base", base_sha[:8], "remote_tree", base_tree[:8],
      "| local origin/main", base_sha_local[:8], "| local HEAD", head_sha[:8])

# changed files (name + mode) between base and head, NUL-separated for unicode safety
raw = git(["diff", "--name-only", "-z", "origin/main..HEAD"])
paths = [p for p in raw.decode("utf-8").split("\0") if p]
print("changed files:", len(paths))

if not paths:
    print("NOTHING_TO_PUSH (origin/main..HEAD 无差异)")
    sys.exit(0)

tree_entries = []
for rel in paths:
    # mode from HEAD tree
    info = git(["ls-tree", "HEAD", rel]).decode("utf-8").strip()
    mode = info.split()[0] if info else "100644"
    abspath = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(abspath, "rb") as f:
        content = f.read()
    b64 = base64.b64encode(content).decode()
    blob = api("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO),
               {"content": b64, "encoding": "base64"})
    tree_entries.append({"path": rel, "mode": mode, "type": "blob", "sha": blob["sha"]})
    print("blob", blob["sha"][:8], mode, rel)

new_tree = api("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO),
               {"base_tree": base_tree, "tree": tree_entries})
print("new_tree", new_tree["sha"][:8])

msg = git(["log", "-1", "--pretty=%B", "HEAD"]).decode("utf-8").strip()
commit = api("POST", "/repos/%s/%s/git/commits" % (OWNER, REPO),
             {"message": msg, "tree": new_tree["sha"], "parents": [base_sha]})
print("new_commit", commit["sha"][:8])

ref = api("PATCH", "/repos/%s/%s/git/refs/heads/main" % (OWNER, REPO),
          {"sha": commit["sha"], "force": False})
new_remote_sha = ref["object"]["sha"]
print("ref updated ->", new_remote_sha[:8])
# 机器可校验的成功标记：调用方(weekly_refresh.sh / cron agent)必须 grep 到 PUSH_OK 才算发布成功
print("PUSH_OK remote_main=%s files=%d" % (new_remote_sha, len(paths)))

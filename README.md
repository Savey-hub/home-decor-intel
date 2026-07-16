# 家装建材家具行业竞争情报看板

天猫行业运营用竞争情报看板：宏观+房产、7大电商平台动态、政策标准时间轴、头部商家动态，覆盖家具/装修/建材/卫浴厨房/全屋智能/全屋定制/灯具光源/电工五金 8 个子行业。

- 数据窗口：近 30 天滚动 + 本月标记
- 更新频率：每周四 12:00 前
- 首版发布：2026-07-16
- 数据源：全部标注 URL 与发布日，遵循「不编造」原则

## 目录结构

```
home-decor-intel/
├── index.html                  # 已构建看板（供 GitHub Pages / 直开）
├── index.template.html         # 模板（含占位符 __*_JSON__）
├── data/
│   ├── macro_realestate.json   # 宏观 + 房产
│   ├── platform_dynamics.json  # 7 平台动态
│   └── industry_policy.json    # 政策 + 商家 + 展会
├── scripts/
│   ├── build_html.sh           # 将 3 份 JSON 注入模板 → index.html
│   └── weekly_refresh.sh       # 每周四刷新入口（拉最新数据 + rebuild + git push）
└── .nojekyll                   # GitHub Pages 关键：跳过 Jekyll
```

## 本地预览

```bash
cd home-decor-intel
python -m http.server 8903 --bind 127.0.0.1
# 浏览器打开 http://127.0.0.1:8903/index.html
```

## 更新数据

修改 `data/*.json` 后：

```bash
bash scripts/build_html.sh
```

## 未来 GitHub Pages 部署

下周迁移至 GitHub Pages：
```bash
git remote add origin git@github.com:<user>/home-decor-intel.git
git add -A && git commit -m "chore: first edition 2026-07-16"
git push -u origin main
# 仓库 Settings → Pages → 分支 main / root → 保存
```

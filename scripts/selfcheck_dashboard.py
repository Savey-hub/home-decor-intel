"""Headless front-end self-check for index.html.

Starts a local http.server on a high port, loads the dashboard in headless
Chromium, and asserts the invariants that have broken before:
  1. no "加载数据失败" banner
  2. #srcTable tbody row count == data_sources_index.sources length
  3. #gapList / #conflictList non-empty
  4. chart canvases rendered
  5. zero uncaught page errors / console errors
Exits non-zero on any failure. Server is started with `timeout` so it dies on
its own -- never kill it (kill prompts a permission dialog under cron).
"""
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('SELFCHECK_PORT', '8917'))
PY = sys.executable

from playwright.sync_api import sync_playwright  # noqa: E402


def main():
    idx = json.load(open(os.path.join(ROOT, 'data', 'v2', 'data_sources_index.json'), encoding='utf-8'))
    n_sources = len(idx['sources'])

    srv = subprocess.Popen(
        [PY, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(2.0)

    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 1000})
            console_errs, page_errs = [], []
            page.on('console', lambda m: console_errs.append(m.text) if m.type == 'error' else None)
            page.on('pageerror', lambda e: page_errs.append(str(e)))

            page.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='load', timeout=60000)
            page.wait_for_timeout(3500)

            body = page.inner_text('body')
            if '加载数据失败' in body:
                errors.append('BANNER: 页面出现「加载数据失败」')

            rows = page.eval_on_selector_all('#srcTable tbody tr', 'els => els.length')
            if rows != n_sources:
                errors.append('SRCTABLE: rows=%d expected=%d' % (rows, n_sources))

            for sel in ('#gapList', '#conflictList'):
                n = page.eval_on_selector_all(sel + ' > *', 'els => els.length')
                if n == 0:
                    errors.append('EMPTY: %s has 0 children' % sel)
                else:
                    print('  %-14s %d items' % (sel, n))

            canvases = page.eval_on_selector_all(
                'canvas', 'els => els.filter(c => c.width > 0 && c.height > 0).length')
            if canvases < 4:
                errors.append('CHARTS: only %d canvases rendered' % canvases)

            counts = page.evaluate("""() => ({
                policy: (window.POLICY_DATA && window.POLICY_DATA.policy || []).length,
                industry: (window.POLICY_DATA && window.POLICY_DATA.industry || []).length,
                merchant: (window.POLICY_DATA && window.POLICY_DATA.merchant || []).length
            })""")

            print('  srcTable rows %d / sources %d' % (rows, n_sources))
            print('  canvases      %d' % canvases)
            print('  in-page data  %s' % counts)
            if console_errs:
                errors.append('CONSOLE: %s' % console_errs[:3])
            if page_errs:
                errors.append('PAGEERROR: %s' % page_errs[:3])

            page.screenshot(path=os.path.join(ROOT, '_work', 'selfcheck_top.png'))
            browser.close()
    finally:
        srv.terminate()

    if errors:
        print('\nSELFCHECK FAILED:')
        for e in errors:
            print('  - %s' % e)
        sys.exit(1)
    print('\nSELFCHECK OK')


if __name__ == '__main__':
    main()

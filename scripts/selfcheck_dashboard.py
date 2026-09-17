"""Headless front-end self-check for index.html.

Starts a local http.server on a high port, loads the dashboard in headless
Chromium, and asserts the invariants that have broken before:
  1. no "加载数据失败" banner
  2. #srcTable tbody row count == data_sources_index.sources length
  3. #gapList / #conflictList non-empty
  4. chart canvases rendered
  5. every 2026-09 source record appears once in the current-month area and
     never in a historical area; the current archive edition is excluded
  6. the template contains no stale hard-coded July single-month label
  7. zero uncaught page errors / console errors
Exits non-zero on any failure. Server is started with `timeout` so it dies on
its own -- never kill it (kill prompts a permission dialog under cron).
"""
import json
import os
import random
import subprocess
import sys
import time
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('SELFCHECK_PORT', str(random.randint(20000, 55000))))
PY = sys.executable
CURRENT_MONTH = '2026-09'
STALE_SINGLE_MONTH_LABEL = '7月单月'

from playwright.sync_api import sync_playwright  # noqa: E402


def _load(relative_path):
    with open(os.path.join(ROOT, relative_path), encoding='utf-8') as source_file:
        return json.load(source_file)


def _duplicate_title_urls():
    datasets = {
        'macro': _load('data/macro_realestate.json'),
        'platform': _load('data/platform_dynamics.json'),
        'policy': _load('data/industry_policy.json'),
    }
    signatures = {}

    def visit(value, path):
        if isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, '%s[%d]' % (path, index))
        elif isinstance(value, dict):
            title = str(value.get('title') or '').strip()
            url = str(value.get('url') or '').strip()
            if title and url and url != '待核实':
                signatures.setdefault((title, url), set()).add(path)
            for key, child in value.items():
                if isinstance(child, (list, dict)):
                    visit(child, '%s.%s' % (path, key))

    for name, data in datasets.items():
        visit(data, name)
    return [('%s | %s' % signature, sorted(paths))
            for signature, paths in signatures.items() if len(paths) > 1]


def _sensitive_markers():
    return (
        '章' + '鹏',
        'jingdong' + 'caiji',
        '99927' + '544734',
        'Save' + 'y',
        'office-sec.' + 'alibaba-inc.com',
        '阿里' + '内' + '网',
        '内' + '网源',
        'login' + 'Account',
        '账户' + 'ID',
        '扫' + '码',
        '验' + '证码',
        'O' + 'TP',
        'S' + 'SO',
        '登录' + '态',
        '登录' + '会话',
        'Coo' + 'kie',
        'AUM' + 'ID',
        'Send' + 'Input',
        'dual_domain_' + 'token',
    )


def _scan_artifact(path):
    markers = _sensitive_markers()
    hits = []
    if path.lower().endswith('.docx'):
        with zipfile.ZipFile(path) as package:
            for name in package.namelist():
                if not (name.startswith('word/') or name.startswith('docProps/')) or not name.endswith('.xml'):
                    continue
                text = package.read(name).decode('utf-8', errors='ignore')
                hits.extend('%s:%s' % (name, marker) for marker in markers if marker in text)
    else:
        with open(path, encoding='utf-8', errors='ignore') as source_file:
            text = source_file.read()
        hits.extend(marker for marker in markers if marker in text)
    return hits


def main():
    errors = []
    idx = _load('data/v2/data_sources_index.json')
    n_sources = len([s for s in idx['sources'] if str(s.get('layer', '')).upper() != 'D'])

    duplicates = _duplicate_title_urls()
    if duplicates:
        errors.append('DATA: duplicate title+URL across arrays %s' % duplicates[:5])

    template_path = os.path.join(ROOT, 'index.template.html')
    with open(template_path, encoding='utf-8') as template_file:
        template_text = template_file.read()
    if STALE_SINGLE_MONTH_LABEL in template_text:
        errors.append('TEMPLATE: contains stale hard-coded %r' % STALE_SINGLE_MONTH_LABEL)
    if "const CURRENT_MONTH = '%s';" % CURRENT_MONTH not in template_text:
        errors.append('TEMPLATE: missing unified CURRENT_MONTH=%s' % CURRENT_MONTH)

    timeout_exe = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(PY))), 'bin', 'git', 'usr', 'bin', 'timeout.EXE')
    if not os.path.exists(timeout_exe):
        timeout_exe = 'timeout'
    subprocess.Popen(
        [timeout_exe, '600', PY, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(2.0)

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

        counts = page.evaluate("""() => {
            const data = JSON.parse(document.getElementById('dataPolicy').textContent);
            return {
                policy: (data.policy || []).length,
                industry: (data.industry || []).length,
                merchant: (data.merchant || []).length
            };
        }""")
        if any(counts[k] == 0 for k in ('policy', 'industry', 'merchant')):
            errors.append('DATA: empty policy/industry/merchant collection %s' % counts)

        isolation = page.evaluate("""month => {
            const parse = id => JSON.parse(document.getElementById(id).textContent);
            const macro = parse('dataMacro');
            const platform = parse('dataPlatform');
            const policy = parse('dataPolicy');
            const doudian = parse('dataDoudian');
            const chanmama = parse('dataChanmama');
            const juliang = parse('dataJuliang');
            const archive = parse('dataArchive');
            const currentYear = month.slice(0, 4);
            const currentMonthNumber = parseInt(month.slice(5), 10);
            const currentMonthChinese = `${currentYear}年${currentMonthNumber}月`;
            const currentMonthShort = `${currentMonthNumber}月`;
            const normalizeMonth = value => {
                const match = String(value || '').match(/(20\\d{2})(?:[-\\/]|年)(\\d{1,2})/);
                return match
                    ? `${match[1]}-${String(parseInt(match[2], 10)).padStart(2, '0')}`
                    : '';
            };
            const dateFields = ['publishDate', 'effectiveDate', 'date', 'issueDate', 'captured_at', 'scrapedAt'];
            const hasEffectiveText = item => {
                const text = `${item && item.title || ''} ${item && item.summary || ''}`;
                const datedText = dateFields.map(key => String(item && item[key] || '')).join(' ');
                const textYears = text.match(/20\\d{2}/g) || [];
                const contextYears = textYears.length ? textYears : (datedText.match(/20\\d{2}/g) || []);
                const hasDifferentExplicitYear = contextYears.length > 0 && !contextYears.includes(currentYear);
                const mentionsCurrentMonth = [month, currentMonthChinese].some(
                    token => text.includes(token)
                ) || (!hasDifferentExplicitYear && text.includes(currentMonthShort));
                return /生效|实施/.test(text) && mentionsCurrentMonth;
            };
            const itemMonth = (item, effectiveRule = false) => {
                if (!item || typeof item !== 'object') return '';
                const bucket = normalizeMonth(item.monthBucket);
                if (bucket) return bucket;
                if (effectiveRule) {
                    const effective = normalizeMonth(item.effectiveDate);
                    if (effective) return effective;
                    if (hasEffectiveText(item)) return month;
                }
                const fields = effectiveRule ? dateFields.filter(key => key !== 'effectiveDate') : dateFields;
                for (const field of fields) {
                    const value = normalizeMonth(item[field]);
                    if (value) return value;
                }
                return '';
            };
            const isCurrent = (item, effectiveRule = false) => itemMonth(item, effectiveRule) === month;
            const expected = [];
            const add = (path, items, effectiveRule = false) => (Array.isArray(items) ? items : []).forEach(
                (item, index) => {
                    if (isCurrent(item, effectiveRule)) expected.push({key: `${path}:${index}`, item});
                }
            );
            Object.entries(macro.macro || {}).forEach(([name, items]) => add(`macro.macro.${name}`, items));
            Object.entries(macro.realEstate || {}).forEach(([name, items]) => add(`macro.realEstate.${name}`, items));
            Object.entries(platform.platforms || {}).forEach(([name, items]) => add(`platform.platforms.${name}`, items));
            add('platform.crossPlatform', platform.crossPlatform);
            add('policy.policy', policy.policy, true);
            add('policy.industry', policy.industry);
            add('policy.merchant', policy.merchant);
            add('policy.platformRules', policy.platformRules, true);
            add('social.doudian', [doudian]);
            add('social.chanmama', [chanmama]);
            add('social.juliang', [juliang]);

            const renderedCounts = {};
            document.querySelectorAll('#sec-month [data-month-record-key]').forEach(el => {
                const key = el.dataset.monthRecordKey;
                renderedCounts[key] = (renderedCounts[key] || 0) + 1;
            });
            const historyKeys = new Set(Array.from(
                document.querySelectorAll('[data-history-region] [data-history-record-key]'),
                el => el.dataset.historyRecordKey
            ));
            const historicalDuplicates = expected.filter(entry => historyKeys.has(entry.key)).map(entry => entry.key);
            const currentInsideHistory = Array.from(
                document.querySelectorAll('[data-history-region] [data-month-record-key]'),
                el => el.dataset.monthRecordKey
            );
            const expectedKeys = new Set(expected.map(entry => entry.key));
            const unexpectedCurrent = Object.keys(renderedCounts).filter(key => !expectedKeys.has(key));
            const cardIssues = [];
            expected.forEach(entry => {
                const matches = Array.from(document.querySelectorAll('#sec-month [data-month-record-key]'))
                    .filter(el => el.dataset.monthRecordKey === entry.key);
                if (matches.length !== 1) return;
                const card = matches[0];
                const item = entry.item;
                if ((item.source || item.source_name) && !card.querySelector('.src')) cardIssues.push(entry.key + ':source');
                if (item.url && item.url !== '待核实' && !card.querySelector('a[href]')) cardIssues.push(entry.key + ':url');
                const dates = dateFields.map(key => item[key]).filter(Boolean);
                if (dates.length && !dates.some(value => card.textContent.includes(value))) cardIssues.push(entry.key + ':date');
            });
            const requiredGroups = ['macro', 'realestate', 'platform', 'policy', 'industry-merchant', 'social', 'rules'];
            const missingGroups = requiredGroups.filter(
                name => !document.querySelector(`#sec-month [data-month-group="${name}"]`)
            );
            const invalidGroupStates = requiredGroups.filter(name => {
                const heading = document.querySelector(`#sec-month [data-month-group="${name}"]`);
                const content = heading && heading.nextElementSibling;
                return !content || !(content.matches('.mh-grid') || content.matches('.arch-note'));
            });
            const latest = archive.latest || '';
            const latestArchiveCount = latest ? Array.from(
                document.querySelectorAll('#archiveList [data-edition-id]')
            ).filter(el => el.dataset.editionId === latest).length : 0;
            return {
                expectedKeys: expected.map(entry => entry.key),
                renderedCounts,
                historicalDuplicates,
                currentInsideHistory,
                unexpectedCurrent,
                cardIssues,
                missingGroups,
                invalidGroupStates,
                latest,
                latestArchiveCount
            };
        }""", CURRENT_MONTH)
        missing_or_duplicate = [
            key for key in isolation['expectedKeys']
            if isolation['renderedCounts'].get(key, 0) != 1
        ]
        if missing_or_duplicate:
            errors.append('MONTH: current records not rendered exactly once %s' % missing_or_duplicate[:10])
        if isolation['historicalDuplicates'] or isolation['currentInsideHistory']:
            errors.append(
                'MONTH: current records leaked into history %s' %
                (isolation['historicalDuplicates'] + isolation['currentInsideHistory'])[:10]
            )
        if isolation['unexpectedCurrent']:
            errors.append('MONTH: unexpected current record keys %s' % isolation['unexpectedCurrent'][:10])
        if isolation['cardIssues']:
            errors.append('MONTH: current cards lost source/date/URL fields %s' % isolation['cardIssues'][:10])
        if isolation['missingGroups']:
            errors.append('MONTH: missing current-month groups %s' % isolation['missingGroups'])
        if isolation['invalidGroupStates']:
            errors.append('MONTH: groups lack data grid or empty state %s' % isolation['invalidGroupStates'])
        if isolation['latestArchiveCount']:
            errors.append('ARCHIVE: current latest %s appears in history' % isolation['latest'])

        print('  srcTable rows %d / sources %d' % (rows, n_sources))
        print('  canvases      %d' % canvases)
        print('  in-page data  %s' % counts)
        print('  current month %d records, all isolated' % len(isolation['expectedKeys']))
        if console_errs:
            errors.append('CONSOLE: %s' % console_errs[:3])
        if page_errs:
            errors.append('PAGEERROR: %s' % page_errs[:3])

        page.screenshot(path=os.path.join(ROOT, '_work', 'selfcheck_top.png'))
        browser.close()

    artifacts = [os.path.join(ROOT, 'index.html')]
    for root_name in ('data', 'archive', '_build_docx'):
        root_path = os.path.join(ROOT, root_name)
        if not os.path.isdir(root_path):
            continue
        for current_dir, _, names in os.walk(root_path):
            artifacts.extend(
                os.path.join(current_dir, name)
                for name in names
                if name.lower().endswith(('.json', '.html', '.docx'))
            )
    artifacts.extend(
        os.path.join(ROOT, name)
        for name in os.listdir(ROOT)
        if name.lower().endswith('.docx')
    )
    artifacts = sorted(set(path for path in artifacts if os.path.isfile(path)))
    for artifact in artifacts:
        sensitive_hits = _scan_artifact(artifact)
        if sensitive_hits:
            errors.append('LEAK: %s contains %s' % (os.path.relpath(artifact, ROOT), sensitive_hits[:5]))
    print('  artifacts     %d scanned for sensitive markers' % len(artifacts))

    if errors:
        print('\nSELFCHECK FAILED:')
        for e in errors:
            print('  - %s' % e)
        sys.exit(1)
    print('\nSELFCHECK OK')


if __name__ == '__main__':
    main()

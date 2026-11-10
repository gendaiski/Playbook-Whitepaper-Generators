"""Exercise the real local browser companion. Requires Playwright and Chromium.

Run against an empty test workspace, with no provider keys configured:
OPENDRAFT_WORKSPACE=/tmp/opendraft-test python codex-web/server.py
python codex-web/test_browser.py
"""
import json
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

report = Path(os.environ.get('OPENDRAFT_TEST_REPORTS', '/tmp/opendraft-reports'))
report.mkdir(parents=True, exist_ok=True)
base = os.environ.get('OPENDRAFT_TEST_URL', 'http://127.0.0.1:8877')

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1050})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    request_api = page.request
    access_file = os.environ.get('OPENDRAFT_TEST_ACCESS_FILE')
    if access_file:
        assert request_api.get(base + '/api/status').status == 403
        assert request_api.get(base + '/api/jobs').status == 403
        assert request_api.get(base + '/api/files').status == 403
        assert request_api.post(base + '/api/unlock', data={'token': 'invalid'}).status == 403
        page.goto(base + '/#access=' + Path(access_file).read_text().strip())
        page.wait_for_url(base + '/')
    else:
        page.goto(base)
    page.wait_for_function("document.querySelector('#connection').textContent.includes('connected')")
    if access_file:
        # Chromium permits Secure cookies on localhost; APIRequestContext does not.
        # Carry the actual browser session cookie for these localhost-only HTTP checks.
        cookies = page.context.cookies()
        cookie = next(c for c in cookies if c['name'] == 'od_session')
        assert cookie['httpOnly'] and cookie['secure']
        request_api = pw.request.new_context(extra_http_headers={'Cookie': 'od_session=' + cookie['value']})
    assert 'No gemini key' in page.locator('#keynote').inner_text()
    page.locator('[name=topic]').fill('A browser regression research topic')
    page.get_by_role('button', name='Start research', exact=True).click()
    page.wait_for_function("document.querySelector('#notice').textContent.includes('API key')")
    assert request_api.get(base + '/api/jobs').json() == []
    assert request_api.post(base + '/api/jobs', data={'mode': 'sample'}).status == 403
    assert request_api.get(base + '/api/status', headers={'Host': 'attacker.invalid'}).status == 403
    assert request_api.get(base + '/download/settings.local.json').status == 404
    assert request_api.get(base + '/download/%2e%2e/%2e%2e/etc/passwd').status == 404

    def wait_complete(mode):
        page.wait_for_function("mode => { const t=document.querySelector('#run-title').textContent; return t.startsWith(mode+' · ') && (t.includes('completed') || t.includes('failed')); }", arg=mode, timeout=120000)
        assert 'completed' in page.locator('#run-title').inner_text(), page.locator('#log').inner_text()

    page.get_by_role('button', name='Open original sample', exact=True).click()
    wait_complete('sample')
    sample = page.locator('#downloads a').filter(has_text='.pdf').get_attribute('href')
    assert request_api.get(base + sample).body().startswith(b'%PDF')
    page.get_by_role('button', name='Documents & exports', exact=True).click()
    page.locator('#upload').set_input_files({'name': 'regression.md', 'mimeType': 'text/markdown', 'buffer': b'# Export verification\n\nThis document tests the original export backend.\n\n## Results\n\n- PDF\n- Word\n- LaTeX\n'})
    page.wait_for_function("document.querySelector('#notice').textContent.includes('uploaded')")
    page.locator('#document-form [name=file]').select_option(label='regression.md · uploads')
    page.get_by_role('button', name='Run action', exact=True).click()
    wait_complete('export')
    files = {}
    for extension in ['pdf', 'docx', 'tex']:
        href = page.locator('#downloads a').filter(has_text='document.' + extension).get_attribute('href')
        data = request_api.get(base + href).body()
        assert len(data) > 100
        if extension == 'pdf': assert data.startswith(b'%PDF')
        if extension == 'docx': assert data.startswith(b'PK')
        if extension == 'tex': assert b'\\begin{document}' in data
        (report / ('export.' + extension)).write_bytes(data)
        files[extension] = len(data)
    page.get_by_role('button', name='Original CLI help', exact=True).click()
    wait_complete('help')
    assert '--level' in page.locator('#log').inner_text()
    page.get_by_role('button', name='Documents & exports', exact=True).click()
    page.get_by_role('button', name='Fetch data', exact=True).click()
    wait_complete('data')
    assert 'World Bank' in page.locator('#log').inner_text()
    assert len(request_api.get(base + '/api/jobs').json()) == 4
    page.reload()
    page.get_by_role('button', name='Runs & original CLI output', exact=True).click()
    page.wait_for_function("document.querySelectorAll('.job').length===4")
    page.get_by_role('button', name='New paper', exact=True).click()
    page.screenshot(path=str(report / 'browser-desktop.png'), full_page=True)
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.screenshot(path=str(report / 'browser-mobile.png'), full_page=True)
    assert not errors, errors
    (report / 'browser-results.json').write_text(json.dumps({'result': 'passed', 'export_bytes': files, 'jobs': 4, 'javascript_errors': errors, 'checks': ['no-key gate', 'CSRF protection', 'host protection', 'private settings blocked', 'path traversal blocked', 'original sample PDF', 'upload', 'PDF export', 'DOCX export', 'LaTeX export', 'original CLI help', 'dataset provider listing', 'saved history', 'mobile layout']}, indent=2))
    browser.close()
    print('PASS: real browser workflows, exports, history and local access checks')

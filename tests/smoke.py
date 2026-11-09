"""Smoke-Test fuer app.html.

Laedt die App ohne Login, startet alle Module, klappt jede Section auf,
wechselt alle Tabs und oeffnet/schliesst jedes Modal.
Schlaegt fehl bei JavaScript-Fehlern, verschachtelten Modals oder
Modals, die sich nicht schliessen lassen.

Aufruf: python tests/smoke.py <url>
Optional: SUPABASE_JS=<pfad>  lokale supabase-js UMD-Datei statt CDN
"""
import os
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000/app.html'
LOCAL_SB = os.environ.get('SUPABASE_JS')
TABS = ['journal', 'hyp', 'timeline', 'verlauf']

# Fehler, die nichts mit der App zu tun haben (fehlendes Netz zur DB im Test)
IGNORE = ('Failed to load resource', 'ERR_', 'Failed to fetch', 'NetworkError')

problems = []


def add(kind, msg):
    msg = str(msg)
    if any(s in msg for s in IGNORE):
        return
    problems.append(f'{kind}: {msg[:300]}')


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 430, 'height': 900})
    page.on('pageerror', lambda e: add('JS-Fehler', e))
    page.on('console', lambda m: add('Console', m.text) if m.type == 'error' else None)
    page.on('dialog', lambda d: d.dismiss())

    if LOCAL_SB:
        page.route('**/supabase-js@2*', lambda r: r.fulfill(path=LOCAL_SB, content_type='application/javascript'))
    # Keine echten DB-Aufrufe aus dem Test heraus
    page.route('**/*.supabase.co/**', lambda r: r.abort())

    page.goto(URL, wait_until='load', timeout=60000)
    page.wait_for_timeout(2000)

    # Login ueberspringen, Module wie nach dem Login starten
    page.evaluate("""async () => {
        if (typeof showLoginOverlay === 'function') showLoginOverlay(false);
        if (typeof initAllModules === 'function') await initAllModules();
    }""")
    page.wait_for_timeout(2000)

    # 1) Verschachtelte Modals = kaputtes HTML (fehlendes </div>)
    nested = page.evaluate("""() => [...document.querySelectorAll('.modal-overlay .modal-overlay')]
        .map(e => e.id + ' in ' + e.parentElement.closest('.modal-overlay').id)""")
    for n in nested:
        problems.append(f'Modal verschachtelt: {n}')

    # 2) Alle Sections auf- und zuklappen
    sections = page.eval_on_selector_all('.section[id^="sec-"]', 'els => els.map(e => e.id.slice(4))')
    for key in sections:
        for _ in range(2):
            try:
                page.evaluate(f"toggleSection('{key}')")
                page.wait_for_timeout(100)
            except Exception as e:
                add(f'Section {key}', e)

    # 3) Alle Tabs
    for tab in TABS:
        try:
            page.evaluate(f"switchTab('{tab}')")
            page.wait_for_timeout(400)
        except Exception as e:
            add(f'Tab {tab}', e)
    page.evaluate("switchTab('journal')")

    # 4) Jedes Modal oeffnen und wieder schliessen
    modals = page.eval_on_selector_all('.modal-overlay[id]', 'els => els.map(e => e.id)')
    for mid in modals:
        state = page.evaluate(f"""() => {{
            const el = document.getElementById('{mid}');
            el.classList.add('open');
            const opened = getComputedStyle(el).display !== 'none';
            closeModal('{mid}');
            const closed = getComputedStyle(el).display === 'none';
            return [opened, closed];
        }}""")
        if not state[1]:
            problems.append(f'Modal schliesst nicht: {mid}')

    page.screenshot(path='smoke.png', full_page=False)
    browser.close()

print(f'Sections: {len(sections)}  Tabs: {len(TABS)}  Modals: {len(modals)}')
if problems:
    print(f'\n{len(problems)} Problem(e):')
    for pr in problems:
        print('  -', pr)
    sys.exit(1)
print('OK - keine Probleme')

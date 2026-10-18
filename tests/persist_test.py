import sys
from playwright.sync_api import sync_playwright
html = sys.argv[1]
INIT = ("window.__fakeNow = Date.parse('2026-06-17T11:00:00');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now()); };")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(); pg = ctx.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(400)
    pg.evaluate("() => { dogs[0].tricks.push('down'); dogs[0].treats = 4; pawPrints.push({x: 200, y: 160, f: 1, a: 1}); logDiary('Test entry', '🧪'); bowls.food = 0.3; for (let i = 0; i < 610; i++) window.__step(); }")
    pg.reload(); pg.wait_for_timeout(400)
    r = pg.evaluate("[dogs[0].tricks.join(','), dogs[0].treats, pawPrints.length, diaryEntries.map(e => e.text).join(' | '), bowls.food.toFixed(2)]")
    pg.evaluate("toggleDiary(true)")
    li = pg.evaluate("document.getElementById('diaryList').children.length")
    print(r, 'diary rows:', li, 'errors:', errs[:3])
    b.close()

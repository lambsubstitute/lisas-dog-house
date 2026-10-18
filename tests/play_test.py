"""Script a scene and grab frames. usage: play_test.py <html> <out.png> <setup js> <frames> <grab every> [iso time]"""
import sys, base64, io, json
from playwright.sync_api import sync_playwright
from PIL import Image
html, out, setup, frames, every = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
t = sys.argv[6] if len(sys.argv) > 6 else '2026-06-17T11:00:00'
INIT = ("(() => { let s = 7; Math.random = () => { s = (s * 1664525 + 1013904223) %% 4294967296; return s / 4294967296; }; })();"
        "window.__noSave = true; window.__fakeNow = Date.parse('%s');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.setTimeout = (f, ms) => { (window.__timers = window.__timers || []).push([ms / 16.7, f]); return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now());"
        "  (window.__timers || []).forEach(t => { t[0]--; if (t[0] <= 0 && !t.done) { t.done = 1; t[1](); } }); window.__timers = (window.__timers || []).filter(t => !t.done); };") % t
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1400, "height": 1000})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(500)
    pg.evaluate("() => { %s }" % setup)
    shots, log = [], []
    for i in range(frames):
        pg.evaluate("window.__step()")
        if i % every == every - 1:
            d = pg.evaluate("document.getElementById('dioramaCanvas').toDataURL('image/png')")
            shots.append(Image.open(io.BytesIO(base64.b64decode(d.split(",")[1]))).convert("RGB"))
            log.append(pg.evaluate("dogs.map(d => d.name + ':' + d.state + (d.holding ? '+' + d.holding : '') + '@' + d.scene).join(' ') + ' | ' + document.getElementById('toastBanner').textContent"))
    w, h = shots[0].size
    cols = 3
    sheet = Image.new("RGB", (w * cols // 2, h * ((len(shots) + cols - 1) // cols) // 2))
    for k, im in enumerate(shots): sheet.paste(im.resize((w // 2, h // 2)), ((k % cols) * w // 2, (k // cols) * h // 2))
    sheet.save(out)
    print('\n'.join(log)); print('errors:', errs[:5])
    b.close()

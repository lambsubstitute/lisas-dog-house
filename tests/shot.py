"""Screenshot the canvas of a game file. usage: shot.py <html> <out.png> [iso time] [frames] [setup js]"""
import sys, json, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
html, out = sys.argv[1], sys.argv[2]
t = sys.argv[3] if len(sys.argv) > 3 else '2026-06-17T13:00:00'
frames = int(sys.argv[4]) if len(sys.argv) > 4 else 120
setup = sys.argv[5] if len(sys.argv) > 5 else ''
INIT = ("window.__skipCreator = true; window.__fakeNow = Date.parse('%s');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now()); };") % t
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1400, "height": 1000})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}")
    pg.wait_for_timeout(500)
    if setup: pg.evaluate(setup)
    pg.evaluate("n => { for (let i = 0; i < n; i++) window.__step(); }", frames)
    d = pg.evaluate("document.getElementById('dioramaCanvas').toDataURL('image/png')")
    im = Image.open(io.BytesIO(base64.b64decode(d.split(",")[1]))).convert("RGB")
    im.resize((im.width*2, im.height*2), Image.NEAREST).save(out)
    print("errors:", errs[:5])
    b.close()

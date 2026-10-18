import sys, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
html, out = sys.argv[1], sys.argv[2]
INIT = ("window.__noSave = true; window.__fakeNow = Date.parse('2026-06-17T13:00:00');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now()); };")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1400, "height": 1000})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(500)
    pg.evaluate("() => { scene = 'garden'; ball.scene = null; rope.scene = null; const d = dogs[0]; dogs[1].scene = 'kitchen'; d.scene = 'garden'; d.x = 70; d.y = 165; d.update = function() { this.animTick++; if (this.state === 'walk') this.step(); }; d.goTo(320, 165, null, { speed: DOG_RUN }); }")
    frames = []
    for i in range(24):
        pg.evaluate("window.__step()")
        x = pg.evaluate("dogs[0].x")
        d = pg.evaluate("document.getElementById('dioramaCanvas').toDataURL('image/png')")
        im = Image.open(io.BytesIO(base64.b64decode(d.split(",")[1]))).convert("RGB")
        frames.append((x, im))
    # a strip following the dog, and one wide shot showing the ground covered
    strip = Image.new("RGB", (12 * 120, 2 * 100))
    for k, (x, im) in enumerate(frames[:24]):
        c = im.crop((int((x - 30) * 2), 2 * 130, int((x + 30) * 2), 2 * 180)).resize((120, 100), Image.NEAREST)
        strip.paste(c, ((k % 12) * 120, (k // 12) * 100))
    strip.save(out)
    print('distance over 24 frames:', round(frames[-1][0] - frames[0][0], 1), errs[:3])
    b.close()

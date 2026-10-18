import sys, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
html, out = sys.argv[1], sys.argv[2]
INIT = ("window.__noSave = true; window.__fakeNow = Date.parse('2026-06-17T13:00:00');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now()); };")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(400)
    rows = []
    for pose in ['stand', 'sit']:
        frames = []
        for k in range(14):
            pg.evaluate("""([pose, k]) => { scene = 'kitchen'; ball.scene = rope.scene = null;
              dogs.forEach((d, i) => { d.update = () => {}; d.getPose = () => pose; Object.assign(d, { scene: 'kitchen', x: 120 + i * 90, y: 170, facing: 1, wag: 1, animTick: 100 + k * 3, pant: true, eyesClosed: false }); });
              window.__step(); }""", [pose, k])
            d = pg.evaluate("document.getElementById('dioramaCanvas').toDataURL('image/png')")
            im = Image.open(io.BytesIO(base64.b64decode(d.split(",")[1]))).convert("RGB")
            frames.append(im.crop((2 * 88, 2 * 132, 2 * 152, 2 * 176)).resize((128, 88), Image.NEAREST))
        row = Image.new("RGB", (128 * 14, 88)); [row.paste(f, (i * 128, 0)) for i, f in enumerate(frames)]; rows.append(row)
    s = Image.new("RGB", (128 * 14, 176)); s.paste(rows[0], (0, 0)); s.paste(rows[1], (0, 88)); s.save(out)
    b.close()

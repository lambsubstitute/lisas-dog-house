import sys, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
html = sys.argv[1]
INIT = ("window.__fakeNow = Date.parse('2026-06-17T11:00:00');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now()); };")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1200, "height": 1400}); pg = ctx.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(400)
    pg.evaluate("toggleSettings(true)")
    pg.click("text=Add a dog")
    pg.fill("#house-name-2", "Bramble")
    pg.select_option("#breed-2", "spaniel"); pg.select_option("#coat-2", "brownwhite")
    n = pg.evaluate("document.querySelectorAll('#houseSection canvas').length")
    # a picture of the panel's previews
    shots = [pg.evaluate(f"document.getElementById('house-prev-{i}').toDataURL()") for i in range(3)]
    ims = [Image.open(io.BytesIO(base64.b64decode(s.split(',')[1]))).convert('RGB').resize((264, 216), Image.NEAREST) for s in shots]
    sheet = Image.new('RGB', (264 * 3 + 8, 216)); [sheet.paste(im, (i * 268, 0)) for i, im in enumerate(ims)]; sheet.save('creator.png')
    pg.click("text=Move them in")
    for i in range(30): pg.evaluate("window.__step()")
    r1 = pg.evaluate("[dogs.map(d => d.name + '/' + d.breed.name).join(', '), document.getElementById('dogCards').children.length, document.getElementById('toastBanner').textContent]")
    for i in range(620): pg.evaluate("window.__step()")
    pg.reload(); pg.wait_for_timeout(400)
    r2 = pg.evaluate("dogs.map(d => d.name).join(', ')")
    pg.evaluate("toggleSettings(true)"); pg.click("text=Back to Mac and Cheese"); pg.click("text=Move them in")
    r3 = pg.evaluate("dogs.map(d => d.name).join(', ')")
    print('previews', n, '|', r1, '| after reload:', r2, '| reset:', r3, '| errors', errs[:3])
    b.close()

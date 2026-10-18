"""Every dog pose, through the game's real drawing code, on a plain floor. usage: dog_poses.py <html> <out.png> [pose ...]
Two black Labradors (Mac, Cheese) plus a yellow Lab and a spaniel, to check the parts work for other dogs."""
import sys, json, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
html, out = sys.argv[1], sys.argv[2]
POSES = sys.argv[3:] or ['stand', 'walk', 'trot', 'sit', 'lie', 'doze', 'sleep_side', 'sniff', 'eat', 'alert']
DOGS = [{"name":"Lab","breed":"labrador","coat":"fox","collar":"#2f6fb0","size":1.3},{"name":"Spr","breed":"spaniel","coat":"brownwhite","collar":"#2f8a4a","size":1.32},{"name":"Col","breed":"collie","coat":"blackwhite","collar":"#c0392b","size":1.3},{"name":"Dax","breed":"dachshund","coat":"tan","collar":"#e0a82e","size":1.25}]
JS = """([pose, cfgs, k]) => {
  if (!window.__built) { window.__built = 1; buildHousehold(cfgs); }
  scene = 'kitchen';
  dogs.forEach((d, i) => {
    d.update = () => { d.animTick++; };
    d.getPose = () => pose; d.eyesClosed = pose === 'doze' || pose === 'sleep_side'; d.alpha = 1; d.bubble = null;
    Object.assign(d, { x: 34 + i * 84, y: 176, facing: 1, scene: 'kitchen', state: 'stand', animTick: 7 + k, wag: 0.25, pant: pose === 'trot' || pose === 'sit', holding: pose === 'chew' ? 'ball' : pose === 'run' && i === 1 ? 'rope' : null, mud: pose === 'paw' ? 0.8 : 0, wet: pose === 'shake' ? 1 : 0, dreaming: pose === 'sleep_side', barkT: 6 });
  });
  window.__step();
  return true;
}"""
INIT = ("window.__fakeNow = Date.parse('2026-06-17T13:00:00');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now()); };")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1400, "height": 1000})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}")
    pg.wait_for_timeout(600)
    rows = []
    for pose in POSES:
        pg.evaluate(JS, [pose, DOGS, 0])
        d = pg.evaluate("document.getElementById('dioramaCanvas').toDataURL('image/png')")
        im = Image.open(io.BytesIO(base64.b64decode(d.split(",")[1]))).convert("RGB")
        r = im.width // 320
        rows.append(im.crop((10 * r, 124 * r, 330 * r, 182 * r)))
    w, h = rows[0].size
    sheet = Image.new("RGB", (w * 2, h * 2 * len(rows)))
    for k, row in enumerate(rows): sheet.paste(row.resize((w * 2, h * 2), Image.NEAREST), (0, k * h * 2))
    sheet.save(out)
    print("poses:", POSES, "errors:", errs[:3])
    b.close()

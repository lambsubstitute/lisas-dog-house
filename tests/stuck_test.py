"""Balls in every awkward spot (against each wall, past the front edge): does anyone run on the spot?"""
import sys
from playwright.sync_api import sync_playwright
html = sys.argv[1]
INIT = ("window.__noSave = true; window.__fakeNow = Date.parse('2026-06-17T11:00:00');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.setTimeout = (f, ms) => { (window.__timers = window.__timers || []).push([ms / 16.7, f]); return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now());"
        "  (window.__timers || []).forEach(t => { t[0]--; if (t[0] <= 0 && !t.done) { t.done = 1; t[1](); } }); window.__timers = (window.__timers || []).filter(t => !t.done); };")
SPOTS = [('kitchen', 16, 160), ('kitchen', 306, 160), ('kitchen', 150, 186), ('kitchen', 300, 141), ('garden', 58, 150), ('garden', 312, 182), ('garden', 200, 186), ('garden', 62, 131)]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(400)
    for sc, x, y in SPOTS:
        r = pg.evaluate("""([sc, x, y]) => {
          scene = sc; dogs.forEach((d, i) => { d.scene = sc; d.x = 150 + i * 60; d.y = 165; d.stop(); d.state = 'stand'; d.timer = 5; d.carry = null; d.holding = null; });
          ball.held = null; Object.assign(ball, { scene: sc, x, y, z: 0, vx: 0, vy: 0, vz: 0, moving: false });
          dogs.forEach(d => d.chase(ball, DOG_RUN));
          let spot = 0, frames = 0;
          for (; frames < 900; frames++) {
            window.__step();
            dogs.forEach(d => { if (d.state === 'chase' && d.stuckFor > 30) spot++; });
            if (ball.held) break;
          }
          return [frames, ball.held ? ball.held.name : 'nobody', spot];
        }""", [sc, x, y])
        print(sc, x, y, '-> grabbed after', r[0], 'frames by', r[1], '| frames spent running on the spot:', r[2])
    print('errors', errs[:3])
    b.close()

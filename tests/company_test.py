import sys, base64, io, json
from playwright.sync_api import sync_playwright
html = sys.argv[1]
INIT = ("window.__fakeNow = Date.parse('2026-06-17T11:00:00');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now()); };")
def steps(pg, n): pg.evaluate(f"() => {{ for (let i = 0; i < {n}; i++) window.__step(); }}")
def shot(pg, name):
    d = pg.evaluate("document.getElementById('dioramaCanvas').toDataURL('image/png')")
    open(name, 'wb').write(base64.b64decode(d.split(',')[1]))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 900})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(400)
    # 1. following: move the mouse about the floor
    box = pg.evaluate("(() => { const r = document.getElementById('dioramaCanvas').getBoundingClientRect(); return [r.left, r.top, r.width / 320]; })()")
    L, T, s = box
    pg.evaluate("dogs.forEach(d => { d.scene = 'kitchen'; d.stop(); d.state = 'stand'; d.timer = 5; }); dogs[0].x = 60; dogs[1].x = 250; dogs[1].y = 170;")
    path = [(120, 175), (200, 170), (260, 176), (230, 165), (150, 178)]
    log = []
    for (x, y) in path:
        for k in range(12):
            pg.mouse.move(L + (x - 6 + k) * s, T + y * s)
            steps(pg, 10)
        steps(pg, 120)
        log.append(pg.evaluate("dogs.map(d => d.name + ':' + d.state + (d.following ? '*' : '') + '@' + Math.round(d.x) + ',' + Math.round(d.y)).join(' ')") + f"  you {x},{y}")
    shot(pg, 'follow.png')
    # 2. tap the floor with Fuss to call a dog
    pg.evaluate("dogs.forEach(d => { d.following = null; d.stop(); d.state = 'stand'; d.timer = 999; })")
    pg.mouse.click(L + 90 * s, T + 172 * s)
    log.append('tool ' + pg.evaluate('tool') + ' you ' + pg.evaluate('JSON.stringify(you)'))
    steps(pg, 300)
    log.append('called: ' + pg.evaluate("dogs.map(d => d.name + ':' + d.state + '@' + Math.round(d.x) + ',' + Math.round(d.y)).join(' ') + ' | ' + document.getElementById('toastBanner').textContent"))
    # 3. welcome home: pretend we were away five hours
    pg.evaluate("saveState(); const s = JSON.parse(localStorage.getItem(SAVE_KEY)); s.at -= 5 * 3600e3; localStorage.setItem(SAVE_KEY, JSON.stringify(s)); window.__noSave = true;")
    pg.reload(); pg.wait_for_timeout(1900)
    steps(pg, 150)
    shot(pg, 'welcome.png')
    log.append('welcome: ' + pg.evaluate("dogs.map(d => d.name + ':' + d.state).join(' ') + ' | ' + document.getElementById('toastBanner').textContent"))
    # 4. a hint about walkies
    pg.evaluate("company.lastWalk = Date.now() - 6 * 3600e3; dogs.forEach(d => { d.stop(); d.scene = 'kitchen'; d.state='stand'; d.timer = 999; }); you.at = -1e9; const r0 = Math.random; Math.random = () => 0.1; dogs[1].findFun(); Math.random = r0;")
    steps(pg, 500)
    shot(pg, 'hint.png')
    log.append('hint: ' + pg.evaluate("dogs.map(d => d.name + ':' + d.state + '@' + Math.round(d.x) + ',' + Math.round(d.y)).join(' ')"))
    pg.evaluate("startWalkies()"); steps(pg, 20); shot(pg, 'leadsgone.png')
    print('\n'.join(log)); print('errors', errs)

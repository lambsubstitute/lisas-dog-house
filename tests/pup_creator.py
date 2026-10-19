import sys
from playwright.sync_api import sync_playwright
html = sys.argv[1]
INIT = ("window.__fakeNow = Date.parse('2026-06-17T11:00:00');")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1100, "height": 1300})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}"); pg.wait_for_timeout(500)
    pg.evaluate("toggleSettings(true)")
    pg.click("text=Add a puppy"); pg.wait_for_timeout(200)
    pg.locator("#settingsPanel > div").screenshot(path="pup_creator.png")
    pg.click("text=Move them in"); pg.wait_for_timeout(500)
    print(pg.evaluate("dogs.map(d => d.name + (d.puppy ? ' (puppy)' : '')).join(', ')"), pg.evaluate("document.getElementById('dogCards').innerText.replace(/\\n+/g,' | ').slice(0,300)"))
    pg.evaluate("localStorage.clear()")
    print('errors', errs)

"""Fast-forward the dogs' day and report what they got up to. usage: dog_sim.py <html> <frames> <seed> [iso time]"""
import sys, json
from playwright.sync_api import sync_playwright
html, frames, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
t = sys.argv[4] if len(sys.argv) > 4 else '2026-06-17T11:00:00'
INIT = ("(() => { let s = %d; Math.random = () => { s = (s * 1664525 + 1013904223) %% 4294967296; return s / 4294967296; }; })();"
        "window.__noSave = true; window.__fakeNow = Date.parse('%s');"
        "window.requestAnimationFrame = cb => { window.__rafCb = cb; return 1; };"
        "window.setTimeout = (f, ms) => { (window.__timers = window.__timers || []).push([ms / 16.7, f]); return 1; };"
        "window.__step = () => { const cb = window.__rafCb; window.__rafCb = null; if (cb) cb(performance.now());"
        "  (window.__timers || []).forEach(t => { t[0]--; if (t[0] <= 0 && !t.done) { t.done = 1; t[1](); } }); window.__timers = (window.__timers || []).filter(t => !t.done); };") % (seed, t)
EVENTS = """(k) => {
  const ev = ['ball', 'ball', 'rope', 'treat', 'towel', 'post', 'scene', 'bowls', 'floortreat', 'walkies', 'rain', 'storm', 'clear'][k % 13];
  const f = SCENES[scene].floor, rx = f.x1 + Math.random() * (f.x2 - f.x1), ry = f.y1 + Math.random() * (f.y2 - f.y1);
  const d = dogs[Math.floor(Math.random() * dogs.length)];
  if (ev === 'ball') throwBall(rx, ry);
  if (ev === 'rope') throwRope();
  if (ev === 'treat') d.askTrick();
  if (ev === 'towel') d.towel();
  if (ev === 'post') deliverPost();
  if (ev === 'scene') goToScene(scene === 'kitchen' ? 'garden' : 'kitchen');
  if (ev === 'bowls') fillBowls();
  if (ev === 'floortreat') tossTreat(rx, ry);
  if (ev === 'walkies' && Math.random() < 0.5) startWalkies();
  if (ev === 'rain') { currentWeatherIdx = 1; updateOutside(true); }
  if (ev === 'storm') { currentWeatherIdx = 5; updateOutside(true); }
  if (ev === 'clear') { currentWeatherIdx = 4; updateOutside(true); }
  return ev;
}"""
RUN = """(n) => {
  const S = window.__S || (window.__S = { states: {}, scenes: {}, moves: 0, bad: [], stuck: 0, last: dogs.map(d => [d.x, d.y, d.state, 0]) });
  for (let i = 0; i < n; i++) {
    const before = dogs.map(d => d.scene);
    window.__step();
    dogs.forEach((d, k) => {
      S.states[d.state] = (S.states[d.state] || 0) + 1;
      if (before[k] !== d.scene) { S.scenes[d.name + '->' + d.scene] = (S.scenes[d.name + '->' + d.scene] || 0) + 1; }
      if (!isFinite(d.x) || !isFinite(d.y)) S.bad.push([globalTick, d.name, 'nan']);
      if (d.scene === 'out') { S.states.out = (S.states.out || 0) + 1; return; }
      const f = SCENES[d.scene].floor;
      if (d.state !== 'away' && d.state !== 'door' && !(d.inBed && d.inBed()) && (d.x < f.x1 - 25 || d.x > f.x2 + 6 || d.y < f.y1 - 6 || d.y > f.y2 + 1)) S.bad.push([globalTick, d.name, 'off', d.scene, Math.round(d.x), Math.round(d.y), d.state]);
      // walking for ages without arriving?
      const L = S.last[k];
      if (d.state === L[2]) { L[3]++; const lim = ['sleep', 'doze', 'out', 'stand', 'lie', 'sunbathe', 'hide', 'chew', 'sit'].includes(d.state) ? 12000 : 2400; if (L[3] === lim) { S.stuck++; S.bad.push([globalTick, d.name, 'stuck in', d.state, d.doing]); } } else { L[2] = d.state; L[3] = 0; }
    });
  }
  return { tick: globalTick, states: S.states, scenes: S.scenes, bad: S.bad.slice(0, 8), nbad: S.bad.length, stuck: S.stuck,
           dogs: dogs.map(d => [d.name, d.scene, d.state, Math.round(d.x), Math.round(d.y), d.needs.food.toFixed(2), d.needs.energy.toFixed(2)]) };
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.goto(f"file://{html}")
    pg.wait_for_timeout(500)
    import os
    if os.environ.get('SETUP'): pg.evaluate("() => { " + os.environ['SETUP'] + " }")
    done, k, evs = 0, 0, []
    every = int(os.environ.get('EVERY', '0'))
    step = every or 3000
    while done < frames:
        r = pg.evaluate(RUN, min(step, frames - done)); done += step
        if every: evs.append(pg.evaluate(EVENTS, k)); k += 1
    print(json.dumps(r, indent=None))
    print('events:', len(evs)); print('errors:', errs[:5])
    b.close()

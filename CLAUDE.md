# Lisa's Dog House

A cosy pixel-art farmhouse (kitchen and garden) where Lisa's two black Labradors, Mac and Cheese, live their day. A hobby browser game and the sister of Cozy Cat Sanctuary (`../cozy-cat-sanctuary`), built on its engine. `README.md` explains the game.

## The shape of it

- **Everything is in `index.html`**: no build step, no image or sound files. Only outside resources: the Tailwind play CDN, two Google fonts, Open-Meteo for real weather.
- Find your way by the capitalised section banners: `grep -nE '^\s*// [A-Z0-9][A-Z0-9 &:,()-]{5,}' index.html`.
- Two scenes (`scene` is the one on screen); every dog has `dog.scene` and lives on whether it's shown or not. The back door (`throughDoor`, `arrive`) moves dogs between them.
- Dogs are `PixelDog`s; behaviour is `dog.state`, `getPose()` turns it into a pose, `dogPose()` places the parts, `drawDogBody()` draws them. `dogMouth()` says where the mouth is (for carrying the ball, tug of war).
- Walking, trotting and the bound are timed by distance covered (`dog.gaitDist`), not the clock, so feet never skate. What dogs do on their own is `chooseNext` and `findFun`; GARDEN VISITORS has the squirrel and the blackbird.
- Toys and floor things (ball, rope, treats, post, paw prints) are in TOYS & THINGS ON THE FLOOR. A dog on a walk has `scene === 'out'`.
- The household (which dogs live here) is saved under `lisasDogHouse.household` (see YOUR DOGS); the rest under `lisasDogHouse.v1`. New breeds go in `BREEDS` (proportions) and `BREED_SIZE`; new coats in `DOG_COATS` (a `belly` different from `base` gives a white bib and socks).
- Saves live in `localStorage` under `lisasDogHouse.v1` (weather settings under `lisasDogHouse.weather`). If you add to the save, give old saves a default. Tests set `window.__noSave`.

## Rules

- Room pixels: each scene is 320 x 190 (`W`, `H`), drawn at `RES = 2`. Floors and spots are in `SCENES`, `K_*` and `G_*` constants; don't move furniture without moving those.
- Art follows the cat game's `cozy-cat-art` skill (light from the top left, hue-shifted shading, dithering, `hash2` not `Math.random()` in anything drawn, sprites through `spriteFX`, the strobe rule). Dogs are drawn from parts and palettes: never hard-code a coat colour, use `dog.pal`.
- Render and look at any art change (`tests/dog_poses.py`, `tests/shot.py`); run `tests/dog_sim.py` after any behaviour change, with and without `EVERY=400` (errors, off-floor and stuck counts must be 0).

## Working with Beef

- Show, don't describe: send screenshots and pose sheets early. Keep write-ups short and in plain British English.
- Commit and push only when he says to. Pushing to `main` deploys to GitHub Pages (once the repo `lambsubstitute/lisas-dog-house` exists).

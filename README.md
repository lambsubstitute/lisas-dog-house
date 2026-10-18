# Lisa's Dog House

A cosy pixel-art farmhouse where two big black Labradors, Mac and Cheese, live their day. It's the sister game to [Cozy Cat Sanctuary](https://lambsubstitute.github.io/cozy-cat-sanctuary/), built on the same engine.

Everything is in one file, `index.html`. There's nothing to install or build: open it in a browser and it runs.

## What's in the house

- **Two scenes.** The farmhouse kitchen (the red range cooker in the old inglenook, the dogs' bed in front of it, the Belfast sink under the window, the Welsh dresser, the big table and the stable door) and the garden out the back (the apple tree, the kennel nobody sleeps in, the bench, the flower border, the gate and, over the fence, the Levels and the Tor). Switch with the buttons under the room, or click the back door.
- **Mac and Cheese.** Black Labradors (Mac has the red collar, Cheese the mustard one). They potter about, sniff along the flower bed, sit, flop down, lie in the sun, eat, drink, ask to go out, come in when it rains or gets dark, and go to bed by the range at night. They carry on whether you're watching or not.
- **Fetch.** Pick up the 🎾 Ball and click where to throw it. Both dogs race for it; the winner brings it back and drops it at your feet (or runs off to chew it), and the loser sulks.
- **Tug of war.** Toss the 🪢 Rope toy. Whoever grabs it gives it a good shake, then the other one comes for it.
- **Treats and tricks.** With 🦴 Treats, click a dog for a trick and a treat. They know sit and paw, and learn lie down, spin, speak and take a bow as they earn more treats. The other dog always turns up hoping for one too. Click the floor to toss a treat for them to hoover up.
- **The post.** Every so often the post comes through the letterbox and the house goes berserk. Letters land on the mat (one may get eaten); a parcel gets opened, by teeth. Click the mat to tidy up.
- **Wet dogs.** Out in the rain they get soaked and muddy, come in, and shake it all over the kitchen, leaving muddy paw prints on the flagstones (click them to mop). Rub a wet dog with the 🧺 Towel, and watch out for the zoomies.
- **Walkies.** 🦮 Walkies (or the leads on the peg rail): they race to the garden gate, go out, and come back a few minutes later, tired, muddy and with a story.
- **A life of their own.** Left to themselves they find their own fun: they fetch the ball and play fetch with themselves when you don't throw it, start games of tug and chase, sniff hello (the dog way), scratch, stretch, dig in the flower bed, hoover under the table for crumbs and ask to go out. A squirrel runs along the fence now and then (cue barking), blackbirds land on the lawn to be chased off, and Marmalade, the big ginger cat from next door, sits on the fence washing his paws while the dogs go spare.
- **Little things.** Begging by the table at lunch and dinner, play bows, the evening zoomies, legs paddling and a dream bubble when they dream, and hiding under the table in a thunderstorm. They bound when they run, and their legs keep time with the ground.
- **The diary.** 📔 Diary keeps a log of the day, and the tricks each dog knows. Everything (needs, tricks, the diary, the bowls, the paw prints) is remembered in your browser between visits.
- **Your own dogs.** In Settings ⚙️ you can change Mac and Cheese or make your own household of up to three: name, breed (Labrador, Springer Spaniel, Border Collie, Dachshund, Jack Russell), coat, collar, character and bark. "Back to Mac and Cheese" puts the originals back.
- **On a phone** the room stays at the top with the buttons in tidy rows underneath.
- **The outside world.** Real time of day and seasons, made-up weather or the real weather where you live (Settings ⚙️), exactly as in the cat game.

Still to come: puppies, and a proper look on a real phone.

## Making changes

The look and the drawing toolkit (`painter`, `spriteFX`, dithering, the symbols and bubbles, the view outside) are the cat game's, unchanged, so its art rules apply: see `.claude/skills/cozy-cat-art/SKILL.md` in the cat game. What's new:

- **THE KITCHEN** and **THE GARDEN** sections paint each scene once (`kitchenBackdrop`, `gardenBackdrop`) and draw the live parts (the stable door, the bowls, the table in two halves so a dog can lie under it, the garden sky and weather).
- **THE DOGS, DRAWN** builds every dog from parts rather than stored pictures: a body (a capsule from rump to chest, tucked up at the waist), a neck and head (a round skull and a muzzle that can point anywhere), drop ears, legs that bend at the right joints, and a tail. A breed is just a set of proportions in `BREEDS`, and a coat is a palette in `DOG_COATS`, so new breeds and colours come from the same code. Poses are in `dogPose`.
- **TOYS & THINGS ON THE FLOOR** has the ball, the rope, treats, the post on the mat and the paw prints: thrown things fly in an arc, bounce and roll.
- **THE DOGS' DAY** is the behaviour: `PixelDog`, a state machine (`dog.state`), `chooseNext` deciding what to do next, the back door and the garden gate taking dogs from one scene to another (or out on a walk), and the games (`chase`, tug of war, tricks, the post, walkies).
- **THE DIARY** and **MEMORY** keep the log and save everything under `lisasDogHouse.v1` in local storage.

## Tests

The scripts in `tests/` drive the page in headless Chromium with Playwright.

```sh
pip install playwright pillow --break-system-packages && python3 -m playwright install chromium   # once
GAME=$PWD/index.html
python3 tests/dog_sim.py $GAME 36000 1                          # ten minutes of dog life: no errors, nobody stuck or off the floor
EVERY=400 python3 tests/dog_sim.py $GAME 36000 4                # the same, with a random event every 400 frames (ball, rope, treats, post, walkies, storms...)
python3 tests/dog_sim.py $GAME 12000 3 2026-10-18T23:30:00      # bedtime
python3 tests/dog_poses.py $GAME poses.png                       # every pose, Mac, Cheese, a yellow Lab and a spaniel
python3 tests/shot.py $GAME shot.png 2026-10-18T21:30:00         # a screenshot at a chosen time
python3 tests/play_test.py $GAME fetch.png "scene='garden'; dogs.forEach(d => d.scene = 'garden'); throwBall(260, 160)" 360 40   # script a moment, grab frames
python3 tests/persist_test.py $GAME                              # saves survive a reload
python3 tests/creator_test.py $GAME                              # adding a dog in Settings, moving them in, reloading, going back to Mac and Cheese
python3 tests/breed_poses.py $GAME breeds.png stand sit lie       # the other breeds
python3 tests/run_strip.py $GAME run.png                         # a dog bounding across the lawn, frame by frame
SETUP="currentWeatherIdx = 4; updateOutside(true);" python3 tests/dog_sim.py $GAME 36000 6 2026-06-18T15:00:00   # a dry afternoon: what they do on their own
```

Built with Claude.

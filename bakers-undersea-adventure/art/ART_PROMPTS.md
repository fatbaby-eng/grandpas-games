# Art generation sheet

The reference paintings in `art/reference/` set the style. Use the style block
below verbatim at the start of every prompt so the whole cast and every scene
match. Save results with the exact filenames listed; the game picks them up
automatically (`web/assets/images/...`, then run `python tools/build_web.py`).

## Style block (paste first)

> Children's storybook illustration, soft painterly digital art, gentle
> watercolor texture, warm rounded shapes, big glossy expressive eyes, thick
> soft outlines, bright but cosy underwater palette, in the style of a 1990s
> point-and-click children's adventure game.

## Characters

Each character needs two images, **facing right**, full body, centered, on a
**plain pure white background** with nothing else in frame (no bubbles, no
rays, no floor). Same pose in both; only the mouth changes.

| File (in `web/assets/images/characters/`) | Who | Prompt details |
|---|---|---|
| `baker.png`, `baker_talk.png` | Baker | Round golden fish, blue neckerchief, freckles, calm smile / open happy mouth. Match the reef painting exactly. |
| `coral.png`, `coral_talk.png` | Coral | Pink seahorse with white spots, little kelp bracelet on her tail, worried-but-kind eyes. |
| `grandma.png`, `grandma_talk.png` | Grandma Grouper | Big olive-green speckled grouper, round spectacles, gentle sleepy smile, a tiny bun of grey hair. |
| `puffer.png`, `puffer_talk.png` | Mr. Puffer | Tan puffer fish, fully puffed, short spines, grumpy brows but a kind mouth. |
| `shelly.png`, `shelly_talk.png` | Shelly | Green sea turtle, squinting near-sighted eyes, embarrassed blush. |
| `clam.png`, `clam_talk.png` | Captain Clam | A cream clam with a navy captain's hat, moustache, two eyes inside the open shell. (Not a turtle.) |
| `bill.png`, `bill_talk.png` | Barnacle Bill | Huge gentle blue whale with barnacles, apologetic eyebrows, tiny smile. Tail visible. |
| `dj.png`, `dj_talk.png` | DJ Dolphin | Blue dolphin with pink headphones and sunglasses pushed up, big grin. |
| `sidney.png`, `sidney_talk.png` | Sidney | Small orange-red crab, nervous smile, eye stalks. |
| `pip.png` | Pip | Tiny tan crab, unimpressed expression. |

Recommended size: 1024 x 1024 or taller. Transparent background is ideal; a
pure white background is fine (the cut-out tool removes it).

## Backgrounds

16:9, 1280 x 640 or larger, **no characters**, the lower third is open sandy
floor so Baker can walk there. Save to `web/assets/images/backgrounds/`.

| File | Scene | Prompt details |
|---|---|---|
| `coral_reef.jpg` | Coral Reef | Bright sunny reef town square; a big friendly rock on the left (Grandma's rock), a pink coral arch in the top middle (festival gate), open sand, small shells and starfish, kelp edges. |
| `kelp_forest.jpg` | Kelp Forest | Tall swaying green-gold kelp, dappled light, a clear patch of sand on the right where a machine could stand, mossy floor. |
| `sunken_ship.jpg` | Sunken Ship | Inside a cosy wooden wreck: plank walls, two round portholes with light, a ship's wheel on the left, a closed wooden door on the right, barrels. |
| `dark_cave.jpg` | Dark Cave | Deep blue cave, glowing teal mushrooms and tiny lights, a wide open space in the middle-right for a whale, soft rock floor. |
| `festival_grounds.jpg` | Festival Grounds | Dusk-purple water, strings of lanterns and bunting, an empty wooden stage in the centre, a snack stall on the left, a sparkly dance floor on the right. |

## Props (optional, later)

Same style, each on white: treasure chest (closed / open), bubble machine,
captain's chest with three coloured shells, lantern, sandcastle, snack stall,
speakers, balloon, glowing mushrooms, old boot, snail, ship's wheel.

## Notes

- The game flips sprites to face left, so always draw them facing right.
- Keep characters' feet or bellies near the bottom of the image; the game
  bottom-aligns them in their spot.
- The old vector art stays as a fallback for anything not yet painted, so
  assets can arrive one at a time.

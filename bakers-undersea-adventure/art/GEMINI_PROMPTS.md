# Gemini prompt sheet for Baker's Undersea Adventure

Every graphic the game still needs, as copy-and-paste prompts. Each prompt is
self-contained (Gemini does not remember style between prompts), so the style
block is repeated inside every one.

**Always attach a reference image with the prompt.** The best anchors are in
`art/reference/`:

- `baker_point_talk.jpg` for anything with Baker, and for the general
  character look (round, glossy, soft painted scales, thick soft outline).
- `cast_group.jpg` for the other characters' designs.
- `coral_reef_empty.jpg` for the painted-background look.
- `conch_shell.jpg` or `old_boot.jpg` for the item / prop look (clean object
  on white, dark soft outline, painted shading).

Drop results into the folders named below, then run
`python tools/build_web.py` and reload the web game. Anything you do not
generate keeps the drawn fallback, so order does not matter.

## Rules that matter for the game

1. **Characters, items and props on a plain pure white background**, nothing
   else in frame: no water, no bubbles, no floor, no shadow, no text, no labels.
2. **Characters and props face RIGHT.** The game flips them when needed.
3. **Backgrounds have no characters at all**, 16:9, and the bottom third is
   open sandy floor so Baker can walk there.
4. One subject per image. Sheets with many poses are hard to cut apart cleanly.
5. For talking frames: *identical* pose and framing, only the mouth changes.

---

## Style block (every prompt starts with this)

> Children's storybook illustration, soft painterly digital art with gentle
> watercolor texture, warm rounded shapes, big glossy expressive eyes, soft dark
> outlines, bright cosy underwater palette, matching the attached reference
> exactly in rendering style, line weight and colour.

Below, `STYLE` means that paragraph.

---

## 1. Characters

Save to `web/assets/images/characters/`. Two prompts each: idle (mouth closed)
and talk (mouth open). Add to the talk prompt: *"Exactly the same character,
pose, size and framing as the previous image, but with the mouth open as if
mid-sentence."*

| File | Prompt (after STYLE) | Status |
|---|---|---|
| `baker.png` / `baker_talk.png` | Baker, a round golden fish with a blue neckerchief tied at the front, freckles, blue eyes, pointing ahead with one fin, three-quarter view, facing right, full body on plain white. | done (from your sheets) |
| `baker_swim.png` | Same Baker in side profile swimming to the right, tail trailing left, calm smile, full body on plain white. | done |
| `coral.png` / `coral_talk.png` | Coral, a slender pink seahorse with white freckle spots, a small kelp bracelet on her curled tail, big kind worried eyes, facing right, full body on plain white. | needs talk frame |
| `grandma.png` / `grandma_talk.png` | Grandma Grouper, a large olive-green speckled grouper fish with round wire spectacles, a tiny grey bun of hair, warm sleepy smile, facing right, full body on plain white. | needs talk frame |
| `puffer.png` / `puffer_talk.png` | Mr. Puffer, a tan pufferfish fully puffed into a ball, short soft spines, cream belly, grumpy eyebrows but a friendly mouth, facing right, on plain white. | needs talk frame |
| `shelly.png` / `shelly_talk.png` | Shelly, a green sea turtle with a brown patterned shell, squinting near-sighted eyes, pink embarrassed cheeks, facing right, full body on plain white. | needs talk frame |
| `clam.png` / `clam_talk.png` | Captain Clam, a cream and pink clam shell standing open like a mouth, two round eyes and a white moustache inside, a navy blue captain's hat with a gold anchor on top, facing right, on plain white. Not a turtle. | **needed** |
| `bill.png` / `bill_talk.png` | Barnacle Bill, a huge gentle blue whale with a pale belly, a few barnacles on his back, apologetic raised eyebrows and a small shy smile, tail visible, facing right, full body on plain white. | **needed** |
| `dj.png` / `dj_talk.png` | DJ Dolphin, a sleek blue dolphin wearing pink headphones and sunglasses pushed up on his head, big toothy grin, one flipper raised, facing right, full body on plain white. | **needed** |
| `sidney.png` / `sidney_talk.png` | Sidney, a small round orange-red crab with eyes on stalks, a nervous hopeful smile, claws raised slightly, facing right, on plain white. | needs talk frame |
| `pip.png` | Pip, a tiny tan crab with an unimpressed deadpan expression, eyes on stalks, facing right, on plain white. | **needed** |

Optional extra Baker frames (save to `art/baker_poses/`, already partly
there): surprised, celebrating with both fins up, thinking with a fin on his
chin, sleepy. Same pose rules.

## 2. Backgrounds

Save to `web/assets/images/backgrounds/`. 16:9, at least 1280 x 720, no
characters, no text. Attach `coral_reef_empty.jpg` as the reference.

| File | Prompt (after STYLE) | Status |
|---|---|---|
| `coral_reef.jpg` | Done. | done |
| `kelp_forest.jpg` | Tall swaying golden-green kelp forest underwater, dappled sunlight, soft bokeh in the distance, a clear patch of mossy sand across the whole bottom third where someone could stand, a slightly open area on the right, wide 16:9 scene, no characters, no text. | done (soft version in place; a sharper one welcome) |
| `sunken_ship.jpg` | Inside a cosy old sunken wooden ship: plank walls, two round brass portholes with blue light coming through, a big ship's wheel on the left wall, a closed wooden door with iron bands on the right, barrels and crates, dust motes in light beams, open sandy wooden floor across the bottom third, wide 16:9 scene, no characters, no text. | **needed** |
| `dark_cave.jpg` | A deep blue underwater cave, rock walls and stalactites, clusters of glowing teal mushrooms and tiny glowing dots, a large open space in the middle and right big enough for a whale, soft rocky sand floor across the bottom third, mysterious but friendly, wide 16:9 scene, no characters, no text. | **needed** |
| `festival_grounds.jpg` | An underwater festival at dusk: purple-blue water, strings of glowing paper lanterns and colourful bunting, an empty wooden stage in the centre with a red curtain, a snack stall on the left, a sparkly tiled dance floor on the right, balloons, open sandy ground across the bottom third, wide 16:9 scene, no characters, no text. | **needed** |

## 3. Inventory items

Save to `web/assets/images/items/`. Square-ish, single object centred on plain
white, no shadow. Attach `conch_shell.jpg` as the reference.

| File | Prompt (after STYLE) | Status |
|---|---|---|
| `gear.png` | A small shiny brass cog gear, single object centred on plain white. | **needed** |
| `bubble_helmet.png` | Done (brass goggle). | done |
| `glasses.png` | A pair of round pink spectacles with thick lenses, single object centred on plain white. | **needed** |
| `shell_polish.png` | A small round yellow tin of shell polish with a pink lid and a tiny shell drawn on the label, single object centred on plain white. | **needed** |
| `ship_key.png` | A big old iron key with a tiny anchor shape in the bow, single object centred on plain white. | **needed** |
| `lantern.png` | An old brass ship's lantern with a warm glowing light inside and a little friendly glow-worm visible in it, single object centred on plain white. | **needed** |
| `crowbar.png` | A sturdy grey iron crowbar, single object centred on plain white. | **needed** |
| `pearl.png` | A large glowing white pearl with a soft rainbow sheen, single object centred on plain white. | **needed** |
| `recipe_page.png` | A soggy torn page of paper with a handwritten cookie recipe and a little cookie doodle, single object centred on plain white. | **needed** |
| `cookie.png` | A round golden cookie with flecks of green kelp in it, single object centred on plain white. | **needed** |
| `dance_shoes.png` | A pair of tiny sparkly pink dance shoes with little bows, single object centred on plain white. | **needed** |
| `conch_shell.png` | Done. | done |

## 4. Props (things in the scenes)

Save to `web/assets/images/props/<name>.png`. Single object on plain white,
facing right where it has a front. Attach `old_boot.jpg` as the reference.

### Coral Reef
| File | Prompt (after STYLE) | Status |
|---|---|---|
| `sandcastle.png` | A small sandcastle with four towers and a tiny red flag on top, on plain white. | you have one; please resend |
| `starfish.png` | A cheerful orange starfish with two little eyes and a smile, on plain white. | **needed** |
| `chatty_clam.png` | A small lavender clam shell half open, with a tiny bubble coming out, on plain white. | **needed** |
| `to_festival.png` | A pink coral archway decorated with colourful triangle bunting and a cream wooden sign reading FESTIVAL, on plain white. | **needed** |

### Kelp Forest
| File | Prompt (after STYLE) | Status |
|---|---|---|
| `bubble_machine.png` | A whimsical copper and brass bubble machine, boxy with a round glass porthole window, two coloured buttons, dials, a funnel on top, bubbles coming out, on plain white. | **needed** |
| `old_boot.png` | Done. | done |
| `tickly_kelp.png` | A tuft of tall swaying olive-green kelp fronds growing from a small base, on plain white. | you have one; please resend |
| `snail.png` | A tiny brown sea snail with a swirly shell and sleepy eyes on stalks, on plain white. | **needed** |
| `sleepy_fish.png` | A small blue fish asleep in a tiny hammock woven from kelp, little Z bubbles above, on plain white. | **needed** |

### Sunken Ship
| File | Prompt (after STYLE) | Status |
|---|---|---|
| `chest.png` | A closed wooden treasure chest with brass bands and three coloured shells (red, blue, yellow) set into the lid, on plain white. | **needed** |
| `chest_open.png` | The same treasure chest open, lid up, soft golden light inside, on plain white. | **needed** |
| `treasure_door.png` | A heavy arched wooden ship door with iron bands and a big iron keyhole, closed, on plain white. | **needed** |
| `treasure_room.png` | The same arched doorway standing open, dark inside with golden sparkles and a few gold coins and spoons spilling out, on plain white. | **needed** |
| `wheel.png` | A wooden ship's wheel with eight handles and a brass hub, on plain white. | **needed** |
| `porthole.png` | A round brass porthole window with a tiny goldfish peeking through blue glass, on plain white. | **needed** |
| `barrel.png` | A wooden barrel with iron hoops and a faded label reading PICKLES, on plain white. | **needed** |

### Dark Cave
| File | Prompt (after STYLE) | Status |
|---|---|---|
| `stuck_shell.png` | Done (the conch). | done |
| `glow_mushrooms.png` | A cluster of three glowing teal mushrooms of different heights, soft glow around them, on plain white. | **needed** |
| `echo_spot.png` | A dark jagged crack in a cave wall with two faint sound-wave lines coming out, on plain white. | **needed** |
| `suspicious_rock.png` | A rounded grey-purple cave rock that very slightly looks like it has a face, on plain white. | **needed** |
| `krill.png` | A little school of nine tiny pink krill swimming in a loose arrow shape, on plain white. | **needed** |

### Festival Grounds
| File | Prompt (after STYLE) | Status |
|---|---|---|
| `stage.png` | A low wide wooden festival stage front with a row of small yellow lights along the edge, seen straight on, on plain white. | **needed** |
| `dance_floor.png` | A flat rectangular tiled dance floor of glowing pink, blue, yellow and green squares, seen from slightly above, on plain white. | **needed** |
| `cookie_table.png` | A small wooden table piled high with golden kelp cookies, on plain white. | **needed** |
| `balloon.png` | A single red balloon on a string with a little highlight, on plain white. | **needed** |
| `snack_stall.png` | A small striped festival snack stall with a pink awning, a SNACKS sign and cookies on the counter, on plain white. | **needed** |
| `speakers.png` | A stack of two big black loudspeakers with round grey cones, on plain white. | **needed** |
| `confetti_cannon.png` | A small light-blue party confetti cannon on a little stand with a few bits of confetti popping out, on plain white. | **needed** |

### Signs
| File | Prompt (after STYLE) | Status |
|---|---|---|
| `signpost.png` | A wooden signpost with one blank arrow-shaped board pointing right, on plain white. (The game writes the place name on it.) | optional |

## 5. Interface

Save to `web/assets/images/ui/`. Optional; the drawn versions work.

| File | Prompt (after STYLE) | Status |
|---|---|---|
| `logo.png` | The words "Baker's Undersea Adventure" as a playful painted game logo, rounded golden letters with a soft dark outline, a tiny bubble or two, on plain white. | optional |
| `cursor_arrow.png`, `cursor_hand.png`, `cursor_eye.png`, `cursor_talk.png` | A set of four small painted cursor icons in one style: a simple arrow, a pointing hand, an eye, a speech bubble, each alone on plain white. | optional |
| `shelf.png` | A long horizontal wooden shelf plank texture with a few barnacles, 1280 x 80, seamless left to right. | optional |

## 6. Music and voice

Not graphics, but same spirit: the opening theme is composed; your narration
lines and cue times are in `music/NARRATION_SCRIPT.md`, and the dialogue
recording list is `VOICE_SCRIPT.md`.

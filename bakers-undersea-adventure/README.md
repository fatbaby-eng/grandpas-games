# Baker's Undersea Adventure

A gentle point-and-click adventure in the spirit of the Humongous Entertainment
*Freddi Fish* games. You are **Baker the Fish**. The Great Conch Shell has gone
missing on the morning of Founder's Day, and the festival cannot start without it.
Talk to everyone, click on everything, help whoever needs helping, and bring the
shell home.

Made for a 5 to 8 year old playing with a grown-up. There is nothing to lose,
no timer, and no way to get stuck.

## Running the game

Requires Python 3.11 or newer.

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

The first launch synthesises the placeholder audio into `assets/audio` if it is
missing (a couple of seconds). Everything else is already in the repo.

Run the tests with:

```bash
python -m pytest
```

## How to play

| Action | Control |
|---|---|
| Walk | Click on the sea floor (arrow cursor) |
| Talk | Click a character (speech-bubble cursor) |
| Pick up / use | Click an object (hand cursor) |
| Look | Click a funny thing (eye cursor) |
| Leave the scene | Click a labelled exit (door-arrow cursor) |
| Use an item | Click it in the bottom bar, then click a character or object. Click it again to put it away. Right-click an item to hear what it is. |
| Combine items | Select one item, then click another in the bar |
| Hint | Press the **?** button, or wait three minutes and Coral will whisper one |
| Pause menu | **Menu** button or **Esc**: save, hints on/off, sound on/off, replay mini-games, quit |
| Shortcuts | **H** toggles hints, **M** mutes, **F1** shows hotspot outlines (debugging) |

The game autosaves whenever you change scene and when you quit. "Continue" on
the title screen picks up where you left off. Save location:

- Windows: `%APPDATA%\BakersUnderseaAdventure\save.json`
- macOS: `~/Library/Application Support/BakersUnderseaAdventure/save.json`
- Linux: `~/.local/share/BakersUnderseaAdventure/save.json`

## The story (spoilers for grown-ups)

1. **Coral Reef.** Coral says the shell is missing. Grandma Grouper saw a big gray
   shadow heading toward the Kelp Forest (and lost her cookie recipe).
2. **Kelp Forest.** Mr. Puffer's bubble machine needs the **Gear** lying in the kelp.
   Fix it, catch five bubbles, and he gives you the **Bubble Helmet**. Shelly the
   turtle has lost her glasses and mistakes you for a sandwich.
3. **Sunken Ship.** Captain Clam gives you the **Ship Key** if you make him laugh
   (any joke wins) or return his pearl from the shell-puzzle chest. The treasure
   room holds the **Lantern**, a **Crowbar** and **Shelly's Glasses**.
4. **Dark Cave.** Needs the Lantern *or* the Bubble Helmet to enter. Barnacle Bill
   has the shell stuck on his tail. Pop it loose with the helmet or pry it with
   the crowbar.
5. **Festival Grounds.** The gate opens once you carry the shell. Give it to DJ
   Dolphin, play the beat, and watch the ending. Every side quest you finished
   earns its own ending slide.

Two complete routes exist (helmet route, lantern-and-crowbar route). The
Sunken Ship is entirely optional for the main quest, which is why no door there
can ever lock you out.

### Side quests

| Quest | Giver | Reward |
|---|---|---|
| Shelly's Specs | Shelly, Kelp Forest | Shell Polish (combine with the shell for a shiny ending) |
| Puffer's Bubble Trouble | Mr. Puffer, Kelp Forest | Bubble Helmet |
| The Captain's Pearl | Captain Clam, Sunken Ship | Ship Key and a tall tale |
| Dance Like a Crab | Sidney, Coral Reef | Dance Shoes (bonus dance on the festival floor) |
| Grandma's Recipe | Grandma Grouper, Coral Reef | Never-ending Kelp Cookies; every character reacts to one |

### Mini-games

Bubble Catch, Shell Puzzle, Dance Like a Crab and DJ Dolphin's Beat. None can be
lost. A **Skip** button appears after 30 seconds or three slips, and skipping
still grants the reward. All four can be replayed from **Menu > Mini-games**.

## Project layout

```
main.py                     entry point
game/engine/                scene manager, input, inventory, dialogue, cursor,
                            audio, save/load, hints, actions, player, assets
game/scenes/                BaseScene (fully data-driven) + one subclass per
                            scene for ambient effects (kelp sway, cave darkness…)
game/minigames/             the four mini-games
game/content/*.json         ALL text and game logic: scenes, items, dialogue,
                            quests, characters
assets/images, audio        placeholder art and sound (see manifest.json)
assets/audio/voice/         optional voice-over clips
tools/                      asset pack generator, voice script exporter
tests/                      inventory, save/load, content integrity, and a
                            headless full playthrough of every route and quest
```

### Everything is data

No dialogue, hint, item or puzzle lives in Python. `game/content/scenes.json`
describes each scene's walkable area, hotspots, exits and hints;
`dialogue.json` holds every line; `items.json` the inventory; `quests.json` the
quest tables, mini-game text, UI strings and ending slides; `characters.json`
names, colours and sprite filenames.

Hotspots and dialogue use a small declarative language:

- **Conditions**: `{"flag": "x"}`, `{"not_flag": "x"}`, `{"has": "item"}`,
  `{"not_has": "item"}`, `{"counter_gte": ["name", n]}`, `{"all": [...]}`,
  `{"any": [...]}`, `{"not": ...}`.
- **Actions**: `set_flag`, `clear_flag`, `give_item`, `remove_item`, `inc`,
  `dialogue`, `say`, `goto`, `minigame` (with `on_complete`), `sound`, `music`,
  `toast`, `ending`, `save`, and `{"if": cond, "then": [...], "else": [...]}`.

A character's `dialogue` is a list of `{"if": cond, "id": "..."}` entries; the
first match is used, which is how NPCs react to what you carry and how Grandma's
hints get more obvious the more you pester her (`counter_gte` on her talk count).

## Replacing the placeholder art and sound

Every placeholder is drawn or synthesised in code. Drop a real file with the
right name into `assets/` and it is used instead. `assets/manifest.json` lists
the expected filenames:

- backgrounds: 1280 x 640 PNG named in each scene's `background`
- character sprites and portraits: PNG with alpha named in `characters.json`
  (procedural sprites are used until you add them, so they keep animating)
- inventory icons: square PNG named in `items.json`
- audio: `underwater`, `festival` loops and `bubble`, `click`, `pickup`,
  `success` effects as `.ogg` or `.wav`

`python tools/make_placeholder_assets.py --force` regenerates the pack.

## Music

The underwater theme is a composed, synthesised chamber-orchestra piece; see
`music/README.md`. The full opening theme, a narrated version and the voice stem
live in `music/`, and `tools/compose_theme.py` regenerates all of it.

## Voice-over

Every dialogue line can have a recorded clip. The game looks for
`assets/audio/voice/<dialogue id>_<line number>.ogg` (or `.wav`), for example
`coral_intro_01.ogg`, and plays it when that line appears. Missing clips are
fine; the line just shows as text. A line can also name its own file with a
`"voice": "filename"` key in `dialogue.json`.

`VOICE_SCRIPT.md` is the full recording list grouped by character, generated by:

```bash
python tools/export_voice_script.py > VOICE_SCRIPT.md
```

Tips for recording: mono, 22 kHz or 44.1 kHz, trimmed close to the words, saved
as OGG Vorbis to keep the folder small. Clicking to the next line stops the
current clip.

## Assumptions made while building v1

- The spec lists a Crowbar in step 7 but not in the item table; it is included
  as a second way to free the shell, found in the treasure room.
- The treasure room is part of the Sunken Ship scene (a door that opens) rather
  than a sixth scene, keeping the five-scene map from the spec.
- Captain Clam's "joke contest" is three punchlines that all win, so a child can
  never pick wrong. The pearl puzzle is the alternative path to the same key.
- Talking to DJ Dolphin while carrying the shell hands it over automatically;
  using the shell on him does the same thing.
- Cookies are never used up, so a child can hand them to everybody.
- The Festival Gate is locked until the shell is in the inventory (the spec says
  "until shell returned"); after the ending the festival stays open to explore.
- Hint text in the bubble is attributed to Coral, the designated hint character.
- `pygame-ce` is the target; stock `pygame` 2.x also works.

## Not in v1 (by design)

Voice acting is supported but no clips ship. No controller support, no
localisation, no final art, no online features, no mobile build.

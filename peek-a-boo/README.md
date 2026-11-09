# Baker's Peek-a-Boo World

A touch game for the youngest grandkids. Tap a spot, a friend pops out and says
its name in Grandpa's voice. One HTML file, no install. Works in a phone or
tablet browser and can be added to the home screen.

Nine friends: Duck, Piggy, Owl, Horse, Sheep, Tractor, Train, Firetruck, Dino.
Eighteen levels in four bands that follow what a child is usually working on at
that age. The grown-up picks the band in the panel (press and hold the gear);
after three clean rounds in a row the game offers the next band.

| Band | Age | Levels |
|---|---|---|
| 1. Little Explorer | about 12 to 18 months | Discovery, Explorer, Where did it go?, Say hi |
| 2. Big Helper | about 18 to 24 months | Detective, Sound Safari, Match me, Dress Up |
| 3. Clever Kid | about 2 to 3 years | Big and little, Find the color, Peek and remember, Who's that?, One is different, Counting Garden |
| 4. Big Kid | about 3 to 5 years | How many?, What comes next?, B is for Baker, Sort them |

The ages follow the CDC and American Academy of Pediatrics developmental
milestone checklists (revised 2022; Zubler et al., *Pediatrics*) and
HealthyChildren.org, with object permanence after Piaget. The parent panel has a
"Why these levels at this age" fold-out for each band with the specific
milestones and the AAP screen-time guidance for under-fives. The ranges are
typical, not deadlines.

## Running it

Open `index.html` in a browser. For home-screen install and reliable audio on a
phone, serve it over HTTP or upload it to a web host:

```bash
python -m http.server 8000
```

To publish on toddboswell.com, upload `index.html` as `/peek-a-boo/index.html`.

## Files

- `index.html` — the whole game with the recorded voice built in. This is the file to ship.
- `voice-script.html` — the recording script for a phone: one line per screen in big type, tap to mark recorded, a list view, and tips. It opens with everything recorded so far already checked.
- `voice-script.md` — the same lines as a plain list.
- `recordings/raw/` — the recordings as they were made, untouched (`october-batch`, `november-batch`, `november-part3`).
- `recordings/clips/` — one clean clip per line, named after the line. This is what the build reads. Clips cut out of longer takes were verified by speech-to-text to say exactly their line.
- `tools/voice-build.js` — embeds `recordings/clips` into `index.html`.
- `tools/voice-manifest.json` — every line the game can say, file name to spoken text.
- `tools/solve.js` — plays every level to its celebration in headless Chromium and reports page errors.
- `tools/transcribe.py`, `tools/pick-takes.py`, `tools/verify-clips.py` — for new recordings: transcribe a folder with word timings, pick the best take per line (and cut lines out of one long take), and verify each cut.
- `screenshots/` — a few levels.

## Recording more voice

1. Open `voice-script.html` on your phone. Unchecked lines are what's left. Read them in order with a short pause between lines; one long take is fine.
2. Put the new files anywhere under `recordings/raw/`.
3. If they are one file per line, copy them into `recordings/clips/` (near-miss file names are matched). If it is one long take, cut it:

   ```bash
   python -m venv .venv && .venv/bin/pip install faster-whisper
   .venv/bin/python tools/transcribe.py recordings/raw/<new folder> /tmp/words.json
   python tools/pick-takes.py /tmp/words.json tools/voice-manifest.json recordings/clips
   .venv/bin/python tools/verify-clips.py recordings/clips
   ```

4. Build and ship:

   ```bash
   node tools/voice-build.js recordings/clips index.html
   ```

   Needs `node` and `ffmpeg`. Lines without a clip keep the phone's built-in voice.

### Still to record (13)

`where_did_firetruck_go`, `find_the_red_gift`, `find_the_blue_gift`, and
Dino's ten: `dino`, `find_dino`, `watch_dino_hide`, `where_did_dino_go`,
`tap_the_big_dino`, `tap_the_little_dino`, `two_dinos_a_pair`,
`dino_goes_in_the_barn`, `d_is_for_dino_find_dino`, `d_is_for_dino`.

## Sound effects and music

Every sound the game makes is synthesized in the file. Any of them can be
replaced by a recording in `recordings/clips/`, and the build picks them up:

| File name | What it is |
|---|---|
| `sfx_duck` … `sfx_dino` | the nine friend sounds (quack, oink, hoot, neigh, baa, engine, whistle, siren, roar) |
| `sfx_chime` | the happy note for flowers, numerals, and gifts |
| `sfx_celebration` | the round-won fanfare, about two seconds |
| `sfx_empty` | the soft two-note for an empty spot |
| `sfx_nudge` | the "psst" when Baker goes quiet |
| `sfx_flip` | the tick of a memory card turning |
| `sfx_count` | one short note; the game repeats it once per number |
| `music_loop` | optional; a gentle 20 to 40 second loop that plays softly during play, with its own switch in the panel |

The "Sounds and music" tier at the end of `voice-script.html` has a line to read
or make for each one.

## Testing

```bash
node tools/solve.js "$PWD/index.html" /tmp/shots
```

drives all 18 levels to their celebrations and prints any page errors. Needs
`playwright` installed where `node` can find it. Things a headless browser
can't check: the press-and-hold gear, the voice on a real phone, and audio after
the app comes back from the background.

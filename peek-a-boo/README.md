# Baker's Peek-a-Boo World

A touch game for the very youngest grandkids: tap a spot, a friend pops out and
says its name. One HTML file, no install, works on a phone or tablet in the
browser and can be added to the home screen.

Four tiers grow with the child:

| Tier | Age | Levels |
|---|---|---|
| Little Explorer | about 12 to 18 months | Discovery, Explorer, Hideaway, Say Hi |
| Big Helper | about 18 to 24 months | Detective, Safari, Match Me, Big and Little, Dress Up |
| Clever Kid | about 2 to 3 years | Colors, Memory, Shadow, Different, Counting |
| Big Kid | 3 and up | How Many, Pattern, Letters, Sort |

## Running it

Open `index.html` in a browser. For the home-screen install and audio to behave
on a phone, serve it over HTTP instead of opening the file directly, for example:

```bash
python -m http.server 8000
```

then visit `http://localhost:8000/` on the same network, or upload the folder to
a web host.

## Files

- `index.html`: the whole game, including the `VOICE_CLIPS` table that holds
  recorded voice lines once they are built in. Lines without a recording use the
  device's speech voice.
- `peek-a-boo-voice-script.md`: every line the game says, with the file name to
  record it under and recording tips.
- `peek-a-boo-oct21/`, `peek_a_boo_part3/`: recorded MP3 clips (42 so far).
  They are not yet built into `index.html`; the voice script describes the
  `peek-a-boo-voice-build.js` step that converts and embeds them.
- `*.png`: screenshots of a few levels.

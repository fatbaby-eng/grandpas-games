# Baker's Undersea Adventure: web version

The browser build of the game. Open `index.html` in any modern browser, or put
this folder on a web host. No build step, no framework: plain HTML5 canvas and
a handful of scripts.

- Same content as the Python version. `js/content.js` is generated from
  `../game/content/*.json` by `python ../tools/build_web.py`; edit the JSON,
  re-run the script, reload.
- Art is drawn with canvas paths in `js/art.js` (characters, props, item icons,
  backgrounds, cursors), in the thick-outline cartoon style of the old
  Humongous games. Each piece is a small function, so real painted art can
  replace any of them one at a time.
- Saves go to the browser's localStorage. "Continue" on the title screen picks up
  the last autosave (every scene change).
- Audio: music and effects in `assets/audio`; voice clips in `assets/audio/voice`
  named as in `../VOICE_SCRIPT.md`. `build_web.py` writes `js/voice_index.js`
  so the page only asks for clips that exist.
- Works with mouse or touch. Keyboard: arrows in the mini-games, Esc for the menu,
  H toggles hints, M mutes, F1 outlines the hotspots.

Browsers only start sound after a click, so the title screen asks for one.

## Files

| File | Role |
|---|---|
| `js/util.js` | constants, conditions, text wrapping |
| `js/state.js` | inventory, game state, localStorage save |
| `js/audio.js` | music loops, effects, voice clips |
| `js/art.js` | all drawing |
| `js/dialogue.js` | speech bubbles and choices |
| `js/actions.js` | the JSON action interpreter |
| `js/player.js` | Baker |
| `js/scene.js` | data-driven scenes, walking, interaction, ambience |
| `js/minigames.js` | the four mini-games |
| `js/ui.js` | inventory shelf, buttons, hints, toasts |
| `js/game.js` | modes, input, canvas scaling, main loop |

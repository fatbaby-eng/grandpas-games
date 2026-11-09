# Opening theme: narration script and timings

The opening theme is 78 seconds. The narration sits over the first 22 seconds,
where the arrangement is just harp, a soft string pad and the first flute
statement. Record one clip per line, warm and unhurried, like telling a bedtime
story. Keep a beat of silence at the start and end of each take.

| Clip | Starts at | Line |
|---|---|---|
| `narr_1` | 0:01.5 | Far below the waves, where the water is warm and the coral glows, there is a little town called the Coral Reef. |
| `narr_2` | 0:08.5 | Today is Founder's Day, the happiest day of the whole year. |
| `narr_3` | 0:12.5 | But this morning, the Great Conch Shell has gone missing! |
| `narr_4` | 0:16.5 | Somebody has to find it before the festival begins. And that somebody... is Baker. |

Target length per clip: about 5.5 s, 3 s, 3 s and 4.5 s. A little longer is
fine; the music keeps going.

## Rebuilding the mix with your voice

1. Save the four takes as `narr_1.wav` ... `narr_4.wav` (any sample rate, mono
   or stereo) in a folder, say `my_voice`.
2. From the `bakers-undersea-adventure` folder run:

```bash
python tools/compose_theme.py --voice-dir my_voice
```

It re-renders the music, ducks it under your voice automatically, and writes
fresh `opening_theme_with_narration`, `opening_narration_voice_only` and
`opening_theme_instrumental` files in WAV, MP3 and OGG.

## Using a different backing track

`opening_narration_voice_only.wav` is the voice alone on the full 78 second
timeline, already positioned at the times above. Drop it on a track above any
other music in Audacity, GarageBand or similar and it lines up with these cue
points. The instrumental is 6/8 at 80 beats per minute (dotted quarter) in
F major, if you want to match the feel.

## About the placeholder voice

The shipped narration uses a synthesized voice (Piper, "Ryan") as a stand-in.
It is there so you can hear the timing and the ducking. Replace it with your
own recording using the steps above.

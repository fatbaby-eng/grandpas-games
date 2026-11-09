# Baker's Peek-a-Boo: voice script

Everything the game says, in the order worth recording it. Each line has a **file name** (what to call the recording) and the **line to read**. The build script matches recordings to the game by file name, so keep the names exactly as written.

## Before you start

- **Where.** A small room with soft stuff in it (a closet full of clothes is the classic). No fan, no fridge hum, no dishwasher.
- **What.** Voice Memos on your phone is fine. Hold it about a hand's width from your mouth, a little off to the side so P and B don't pop. Same spot for every clip.
- **How.** Warm, slow, and smiling. You're talking to Baker across the kitchen table, not announcing. A one-year-old hears tone long before words.
- **One clip per line.** Tap record, wait a beat, say the line, wait a beat, stop. The build script trims the silence. Keep each under two seconds.
- **Do a few takes** of the names. Pick the one that sounds most like you.
- **Naming.** Save each clip with the file name shown. Voice Memos lets you rename a recording by tapping its title. Any of `.m4a`, `.mp3`, `.aac`, or `.wav` is fine.

## After you record

1. Put all the clips in one folder, say `clips`.
2. From the repo, run:

```
node tools/voice-build.js recordings/clips index.html
```

   It converts each clip to a small mono file, trims the silence, and writes them into the game. It needs `ffmpeg` on the machine (`brew install ffmpeg`). It tells you which lines it found and which are still missing.
3. Upload `site/peek-a-boo/index.html` as before.

Run it again any time you add more clips. Lines without a clip keep using the phone's voice, so record in whatever order you like.

## Tier 1. The names

Sixteen clips. These play on every tap, so they matter most.

| File name | Line to read |
|---|---|
| `duck` | Duck! |
| `piggy` | Piggy! |
| `owl` | Owl! |
| `horse` | Horse! |
| `sheep` | Sheep! |
| `tractor` | Tractor! |
| `train` | Train! |
| `firetruck` | Firetruck! |
| `dino` | Dino! |
| `baker` | Baker! |
| `top_hat` | Top Hat! |
| `crown` | Crown! |
| `cool_shades` | Cool Shades! |
| `hair_bow` | Hair Bow! |
| `flower` | Flower! |
| `heart` | Heart! |

## Tier 2. Prompts that never change

Thirty-three clips. The numbers are for counting, so say them like you're pointing.

| File name | Line to read |
|---|---|
| `tap_anywhere_who_s_hiding` | Tap anywhere. Who's hiding? |
| `some_spots_are_empty_keep_looking` | Some spots are empty. Keep looking! |
| `say_hi_to_everyone` | Say hi to everyone! |
| `who_sings_this` | Who sings this? |
| `find_the_one_that_looks_the_same` | Find the one that looks the same. |
| `open_the_gifts` | Open the gifts! |
| `flip_the_cards_find_the_pairs` | Flip the cards. Find the pairs! |
| `not_a_pair_try_again` | Not a pair. Try again! |
| `who_s_that_look_at_the_shadow` | Who's that? Look at the shadow. |
| `which_one_is_different` | Which one is different? |
| `count_the_butterflies` | Count the butterflies! |
| `how_many_butterflies_tap_the_number` | How many butterflies? Tap the number. |
| `what_comes_next` | What comes next? |
| `animals_go_to_the_barn_vehicles_go_to_the_garage` | Animals go to the barn. Vehicles go to the garage. |
| `the_barn_is_for_animals` | The barn is for animals. |
| `the_garage_is_for_vehicles` | The garage is for vehicles. |
| `the_big_one` | The big one! |
| `the_little_one` | The little one! |
| `band_2_big_helper` | Band 2. Big Helper! |
| `band_3_clever_kid` | Band 3. Clever Kid! |
| `band_4_big_kid` | Band 4. Big Kid! |
| `1` | 1. |
| `2` | 2. |
| `3` | 3. |
| `4` | 4. |
| `5` | 5. |
| `6` | 6. |
| `1_that_s_right` | 1! That's right! |
| `2_that_s_right` | 2! That's right! |
| `3_that_s_right` | 3! That's right! |
| `4_that_s_right` | 4! That's right! |
| `5_that_s_right` | 5! That's right! |
| `6_that_s_right` | 6! That's right! |

## Tier 3. Prompts with a friend's name in them

Eighty-nine clips. A second sitting. Anything you skip stays in the phone's voice until you get to it.

| File name | Line to read |
|---|---|
| `find_duck` | Find Duck! |
| `find_piggy` | Find Piggy! |
| `find_owl` | Find Owl! |
| `find_horse` | Find Horse! |
| `find_sheep` | Find Sheep! |
| `find_tractor` | Find Tractor! |
| `find_train` | Find Train! |
| `find_firetruck` | Find Firetruck! |
| `find_dino` | Find Dino! |
| `watch_duck_hide` | Watch Duck hide! |
| `watch_piggy_hide` | Watch Piggy hide! |
| `watch_owl_hide` | Watch Owl hide! |
| `watch_horse_hide` | Watch Horse hide! |
| `watch_sheep_hide` | Watch Sheep hide! |
| `watch_tractor_hide` | Watch Tractor hide! |
| `watch_train_hide` | Watch Train hide! |
| `watch_firetruck_hide` | Watch Firetruck hide! |
| `watch_dino_hide` | Watch Dino hide! |
| `where_did_duck_go` | Where did Duck go? |
| `where_did_piggy_go` | Where did Piggy go? |
| `where_did_owl_go` | Where did Owl go? |
| `where_did_horse_go` | Where did Horse go? |
| `where_did_sheep_go` | Where did Sheep go? |
| `where_did_tractor_go` | Where did Tractor go? |
| `where_did_train_go` | Where did Train go? |
| `where_did_firetruck_go` | Where did Firetruck go? |
| `where_did_dino_go` | Where did Dino go? |
| `tap_the_big_duck` | Tap the big Duck. |
| `tap_the_big_piggy` | Tap the big Piggy. |
| `tap_the_big_owl` | Tap the big Owl. |
| `tap_the_big_horse` | Tap the big Horse. |
| `tap_the_big_sheep` | Tap the big Sheep. |
| `tap_the_big_tractor` | Tap the big Tractor. |
| `tap_the_big_train` | Tap the big Train. |
| `tap_the_big_firetruck` | Tap the big Firetruck. |
| `tap_the_big_dino` | Tap the big Dino. |
| `tap_the_little_duck` | Tap the little Duck. |
| `tap_the_little_piggy` | Tap the little Piggy. |
| `tap_the_little_owl` | Tap the little Owl. |
| `tap_the_little_horse` | Tap the little Horse. |
| `tap_the_little_sheep` | Tap the little Sheep. |
| `tap_the_little_tractor` | Tap the little Tractor. |
| `tap_the_little_train` | Tap the little Train. |
| `tap_the_little_firetruck` | Tap the little Firetruck. |
| `tap_the_little_dino` | Tap the little Dino. |
| `two_ducks_a_pair` | Two Ducks! A pair! |
| `two_piggys_a_pair` | Two Piggys! A pair! |
| `two_owls_a_pair` | Two Owls! A pair! |
| `two_horses_a_pair` | Two Horses! A pair! |
| `two_sheeps_a_pair` | Two Sheeps! A pair! |
| `two_tractors_a_pair` | Two Tractors! A pair! |
| `two_trains_a_pair` | Two Trains! A pair! |
| `two_firetrucks_a_pair` | Two Firetrucks! A pair! |
| `two_dinos_a_pair` | Two Dinos! A pair! |
| `duck_goes_in_the_barn` | Duck goes in the barn! |
| `piggy_goes_in_the_barn` | Piggy goes in the barn! |
| `owl_goes_in_the_barn` | Owl goes in the barn! |
| `horse_goes_in_the_barn` | Horse goes in the barn! |
| `sheep_goes_in_the_barn` | Sheep goes in the barn! |
| `tractor_goes_in_the_garage` | Tractor goes in the garage! |
| `train_goes_in_the_garage` | Train goes in the garage! |
| `firetruck_goes_in_the_garage` | Firetruck goes in the garage! |
| `dino_goes_in_the_barn` | Dino goes in the barn! |
| `find_the_red_gift` | Find the red gift. |
| `find_the_blue_gift` | Find the blue gift. |
| `find_the_green_gift` | Find the green gift. |
| `find_the_yellow_gift` | Find the yellow gift. |
| `find_the_purple_gift` | Find the purple gift. |
| `find_the_pink_gift` | Find the pink gift. |
| `d_is_for_duck_find_duck` | D is for Duck. Find Duck! |
| `d_is_for_duck` | D is for Duck! |
| `p_is_for_piggy_find_piggy` | P is for Piggy. Find Piggy! |
| `p_is_for_piggy` | P is for Piggy! |
| `o_is_for_owl_find_owl` | O is for Owl. Find Owl! |
| `o_is_for_owl` | O is for Owl! |
| `h_is_for_horse_find_horse` | H is for Horse. Find Horse! |
| `h_is_for_horse` | H is for Horse! |
| `s_is_for_sheep_find_sheep` | S is for Sheep. Find Sheep! |
| `s_is_for_sheep` | S is for Sheep! |
| `t_is_for_tractor_find_tractor` | T is for Tractor. Find Tractor! |
| `t_is_for_tractor` | T is for Tractor! |
| `t_is_for_train_find_train` | T is for Train. Find Train! |
| `t_is_for_train` | T is for Train! |
| `f_is_for_firetruck_find_firetruck` | F is for Firetruck. Find Firetruck! |
| `f_is_for_firetruck` | F is for Firetruck! |
| `d_is_for_dino_find_dino` | D is for Dino. Find Dino! |
| `d_is_for_dino` | D is for Dino! |
| `b_is_for_baker_find_baker` | B is for Baker. Find Baker! |
| `b_is_for_baker` | B is for Baker! |

## Not on the list

The little corrections ("That's Duck! Where's Owl?", "That's the blue one. Find red!") come in hundreds of combinations, so they stay in the phone's voice. If there's one Baker hears a lot and you want it in yours, tell me the line and I'll add it to the manifest.

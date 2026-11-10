"""Regenerate art/gemini-prompts.html (the Gemini prompt checklist).  python tools/build_prompt_sheet.py"""
import json, pathlib
REPO = pathlib.Path(__file__).resolve().parents[1]
OUT_FRAG = pathlib.Path(__file__).resolve().parent / "_prompt_sheet_fragment.html"
OUT_FULL = REPO / "art" / "gemini-prompts.html"

STYLE = ("Match the attached reference image's art style exactly: children's storybook illustration, soft painterly digital art "
         "with gentle watercolor texture, warm rounded shapes, big glossy expressive eyes, soft dark outlines, bright cosy underwater palette.")
CHAR_RULES = ("Full body, facing to the RIGHT, centered, single character only, on a plain pure white background. "
              "No water, no bubbles, no floor, no shadow, no text, no labels, no extra objects.")
TALK_RULES = ("Use the attached image as the character. Recreate it exactly: same character, same pose, same size, same framing, same colours, "
              "plain pure white background. Make only one change: the mouth is open as if speaking mid-sentence. No text, no extra objects.")
ITEM_RULES = ("Single object, centered, roughly square composition, on a plain pure white background. Soft dark outline, painted shading. "
              "No shadow, no text, no hands, no extra objects.")
PROP_RULES = ("Single object, centered, facing to the RIGHT if it has a front, on a plain pure white background. Soft dark outline, painted shading. "
              "No shadow, no text, no characters, no extra objects.")
BG_RULES = ("Wide 16:9 landscape scene, at least 1280 by 720 pixels. No characters, no creatures with faces, no text. "
            "The bottom third of the picture is open sandy floor with nothing standing on it, so a character can walk there. "
            "Detail and colour on the left and right sides, the middle more open.")

sections = []

def sec(title, intro, folder, kind, items):
    sections.append({"title": title, "intro": intro, "folder": folder, "kind": kind, "items": items})

sec("Characters", "Two images each: idle (mouth closed) and talk (mouth open). Generate the idle one first, then attach that result and run the talk prompt. Characters already painted only need their talk frame.",
    "web/assets/images/characters/", "char", [
    {"name": "Captain Clam", "file": "clam.png", "ref": "art/reference/cast_group.jpg", "status": "needed",
     "subject": "Captain Clam: a cream and pink clam shell standing open like a mouth, two round friendly eyes and a white walrus moustache inside the shell, wearing a navy blue captain's hat with a small gold anchor. He is a clam, not a turtle."},
    {"name": "Captain Clam, talking", "file": "clam_talk.png", "ref": "your clam.png result", "status": "needed", "talk": True},
    {"name": "Barnacle Bill", "file": "bill.png", "ref": "art/reference/cast_group.jpg", "status": "needed",
     "subject": "Barnacle Bill: a huge gentle blue whale with a pale ridged belly, a few small barnacles on his back, apologetic raised eyebrows, a small shy smile, tail fluke visible."},
    {"name": "Barnacle Bill, talking", "file": "bill_talk.png", "ref": "your bill.png result", "status": "needed", "talk": True},
    {"name": "DJ Dolphin", "file": "dj.png", "ref": "art/reference/cast_group.jpg", "status": "needed",
     "subject": "DJ Dolphin: a sleek blue bottlenose dolphin wearing pink headphones around his head and sunglasses pushed up on his forehead, big toothy grin, one flipper raised like he is waving to a crowd."},
    {"name": "DJ Dolphin, talking", "file": "dj_talk.png", "ref": "your dj.png result", "status": "needed", "talk": True},
    {"name": "Pip", "file": "pip.png", "ref": "art/reference/cast_group.jpg", "status": "needed",
     "subject": "Pip: a tiny tan sand crab with eyes on stalks and a flat, unimpressed, deadpan expression, claws folded."},
    {"name": "Coral, talking", "file": "coral_talk.png", "ref": "web/assets/images/characters/coral.png", "status": "needed", "talk": True},
    {"name": "Grandma Grouper, talking", "file": "grandma_talk.png", "ref": "web/assets/images/characters/grandma.png", "status": "needed", "talk": True},
    {"name": "Mr. Puffer, talking", "file": "puffer_talk.png", "ref": "web/assets/images/characters/puffer.png", "status": "needed", "talk": True},
    {"name": "Shelly, talking", "file": "shelly_talk.png", "ref": "web/assets/images/characters/shelly.png", "status": "needed", "talk": True},
    {"name": "Sidney, talking", "file": "sidney_talk.png", "ref": "web/assets/images/characters/sidney.png", "status": "needed", "talk": True},
    {"name": "Baker idle / talk / swim", "file": "baker.png, baker_talk.png, baker_swim.png", "ref": "", "status": "done", "subject": ""},
    {"name": "Coral, Grandma, Puffer, Shelly, Sidney idle", "file": "coral.png, grandma.png, puffer.png, shelly.png, sidney.png", "ref": "", "status": "done", "subject": ""},
])

sec("Backgrounds", "One per scene. No characters at all; the game draws them on top. Attach the finished reef painting so every scene matches it.",
    "web/assets/images/backgrounds/", "bg", [
    {"name": "Sunken Ship", "file": "sunken_ship.jpg", "ref": "art/reference/coral_reef_empty.jpg", "status": "needed",
     "subject": "The inside of a cosy old sunken wooden ship: warm plank walls, two round brass portholes with blue light shining through, a big wooden ship's wheel on the left wall, a closed arched wooden door with iron bands on the right side, wooden barrels and crates along the walls, dust motes drifting in light beams, a few small fish."},
    {"name": "Dark Cave", "file": "dark_cave.jpg", "ref": "art/reference/coral_reef_empty.jpg", "status": "needed",
     "subject": "A deep blue underwater cave, soft rock walls and a few stalactites, clusters of glowing teal mushrooms and tiny glowing dots like fireflies, a large open empty space in the middle and right side big enough for a whale to rest in, mysterious but friendly and not scary."},
    {"name": "Festival Grounds", "file": "festival_grounds.jpg", "ref": "art/reference/coral_reef_empty.jpg", "status": "needed",
     "subject": "An underwater festival at dusk: purple-blue water, strings of glowing paper lanterns and colourful triangle bunting across the top, an empty wooden stage in the centre with a small red curtain, a striped snack stall on the left, a sparkly tiled dance floor on the right, a few balloons tied to rocks."},
    {"name": "Kelp Forest, sharper", "file": "kelp_forest.jpg", "ref": "art/reference/coral_reef_empty.jpg", "status": "optional",
     "subject": "A tall swaying golden-green kelp forest, dappled sunlight from above, soft bokeh in the far distance but crisp kelp in front, a clear patch on the right side where a machine could stand, mossy sand floor."},
    {"name": "Coral Reef", "file": "coral_reef.jpg", "ref": "", "status": "done", "subject": ""},
])

sec("Inventory items", "Small square icons shown in the shelf at the bottom of the screen. Attach the conch shell so they share its finish.",
    "web/assets/images/items/", "item", [
    {"name": "Gear", "file": "gear.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A small shiny brass cog gear with eight teeth."},
    {"name": "Shelly's Glasses", "file": "glasses.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A pair of round pink spectacles with thick glass lenses."},
    {"name": "Shell Polish", "file": "shell_polish.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A small round yellow tin of shell polish with a pink lid and a tiny seashell drawn on its label."},
    {"name": "Ship Key", "file": "ship_key.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A big old iron key with a tiny anchor shape worked into the bow."},
    {"name": "Lantern", "file": "lantern.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "An old brass ship's lantern with a warm glowing light inside, and a tiny friendly glow-worm visible through the glass."},
    {"name": "Crowbar", "file": "crowbar.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A sturdy grey iron crowbar with a curved claw end."},
    {"name": "Lucky Pearl", "file": "pearl.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A large glowing white pearl with a soft rainbow sheen."},
    {"name": "Recipe Page", "file": "recipe_page.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A soggy torn page of cream paper with a handwritten cookie recipe and a small cookie doodle in the corner; the writing is just scribbles, not real letters."},
    {"name": "Kelp Cookie", "file": "cookie.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A round golden-brown cookie with little flecks of green kelp baked into it."},
    {"name": "Dance Shoes", "file": "dance_shoes.png", "ref": "art/reference/conch_shell.jpg", "status": "needed", "subject": "A pair of tiny sparkly pink dance shoes with little bows."},
    {"name": "Bubble Helmet, Great Conch Shell", "file": "bubble_helmet.png, conch_shell.png", "ref": "", "status": "done", "subject": ""},
])

PROPS = [
    ("Coral Reef", [
        ("Sandcastle", "sandcastle.png", "A small sandcastle with four towers, battlements and a tiny red flag on the tallest tower.", "needed"),
        ("Starfish", "starfish.png", "A cheerful orange starfish with two little eyes and a smile.", "needed"),
        ("Chatty clam", "chatty_clam.png", "A small lavender clam shell half open with a single tiny bubble coming out.", "needed"),
        ("Festival arch", "to_festival.png", "A pink coral archway decorated with colourful triangle bunting, with a cream wooden sign hanging in the middle that reads FESTIVAL.", "needed"),
    ]),
    ("Kelp Forest", [
        ("Bubble machine", "bubble_machine.png", "A whimsical copper and brass bubble machine: a boxy body with a round glass porthole window in the front, a red button and a green button, little dials, a funnel on top, and a few bubbles floating out.", "needed"),
        ("Tickly kelp", "tickly_kelp.png", "A tuft of tall swaying olive-green kelp fronds growing from a small rounded base.", "needed"),
        ("Snail", "snail.png", "A tiny brown sea snail with a swirly shell and sleepy eyes on stalks.", "needed"),
        ("Sleepy fish", "sleepy_fish.png", "A small blue fish asleep in a tiny hammock woven from kelp, with two or three small Z-shaped bubbles above it.", "needed"),
        ("Old boot", "old_boot.png", "", "done"),
    ]),
    ("Sunken Ship", [
        ("Treasure chest, closed", "chest.png", "A closed wooden treasure chest with brass bands and three coloured seashells, one red, one blue, one yellow, set into the curved lid.", "needed"),
        ("Treasure chest, open", "chest_open.png", "The same wooden treasure chest with brass bands and three coloured shells on the lid, now open with the lid up and soft golden light glowing from inside.", "needed"),
        ("Treasure room door, closed", "treasure_door.png", "A heavy arched wooden ship door with dark iron bands and a big iron keyhole, closed.", "needed"),
        ("Treasure room door, open", "treasure_room.png", "The same arched wooden doorway standing open, dark inside with golden sparkles, a few gold coins and old silver spoons spilling out of the bottom.", "needed"),
        ("Ship's wheel", "wheel.png", "A wooden ship's wheel with eight handles and a brass hub.", "needed"),
        ("Porthole", "porthole.png", "A round brass porthole window with rivets, with a tiny goldfish peeking through the blue glass.", "needed"),
        ("Barrel", "barrel.png", "A wooden barrel with iron hoops and a faded paper label that reads PICKLES.", "needed"),
    ]),
    ("Dark Cave", [
        ("Glowing mushrooms", "glow_mushrooms.png", "A cluster of three glowing teal mushrooms of different heights with a soft glow around them.", "needed"),
        ("Echo crack", "echo_spot.png", "A dark jagged crack in a grey-blue cave rock with two faint curved sound-wave lines coming out of it.", "needed"),
        ("Suspicious rock", "suspicious_rock.png", "A rounded grey-purple cave rock that very slightly looks like it has a sleepy face.", "needed"),
        ("Krill", "krill.png", "A little school of nine tiny pink krill swimming together in a loose arrow shape.", "needed"),
        ("Stuck conch shell", "stuck_shell.png", "", "done"),
    ]),
    ("Festival Grounds", [
        ("Stage", "stage.png", "A low wide wooden festival stage front seen straight on, with a row of small warm yellow lights along the front edge.", "needed"),
        ("Dance floor", "dance_floor.png", "A flat rectangular tiled dance floor of glowing pink, blue, yellow and green squares, seen from slightly above.", "needed"),
        ("Cookie table", "cookie_table.png", "A small wooden table piled high with golden kelp cookies.", "needed"),
        ("Balloon", "balloon.png", "A single red balloon on a white string with a little highlight.", "needed"),
        ("Snack stall", "snack_stall.png", "A small festival snack stall with a pink and white striped awning, a wooden sign that reads SNACKS, and a few cookies on the counter.", "needed"),
        ("Speakers", "speakers.png", "A stack of two big black loudspeakers with round grey cones.", "needed"),
        ("Confetti cannon", "confetti_cannon.png", "A small light-blue party confetti cannon on a little stand, with a few bits of pink, yellow and green confetti popping out.", "needed"),
    ]),
    ("Signs", [
        ("Signpost", "signpost.png", "A wooden signpost with one blank arrow-shaped board pointing to the right. The board is empty; the game writes the place name on it.", "optional"),
    ]),
]
items = []
for scene, props in PROPS:
    for name, file, subject, status in props:
        items.append({"name": f"{name}", "scene": scene, "file": file, "ref": "art/reference/old_boot.jpg", "status": status, "subject": subject})
sec("Scene props", "Things Baker can click on in each scene. Attach the boot so the finish matches.", "web/assets/images/props/", "prop", items)

sec("Interface, optional", "The drawn interface works. These only need doing if you want the whole screen painted.", "web/assets/images/ui/", "item", [
    {"name": "Game logo", "file": "logo.png", "ref": "art/reference/baker_point_talk.jpg", "status": "optional", "subject": "The words BAKER'S UNDERSEA ADVENTURE as a playful painted game logo, rounded golden letters with a soft dark outline and a few tiny bubbles."},
    {"name": "Cursor: arrow", "file": "cursor_arrow.png", "ref": "art/reference/old_boot.jpg", "status": "optional", "subject": "A simple chunky white arrow cursor icon with a soft dark outline."},
    {"name": "Cursor: hand", "file": "cursor_hand.png", "ref": "art/reference/old_boot.jpg", "status": "optional", "subject": "A simple chunky pointing-hand cursor icon, white glove style, with a soft dark outline."},
    {"name": "Cursor: eye", "file": "cursor_eye.png", "ref": "art/reference/old_boot.jpg", "status": "optional", "subject": "A simple chunky eye icon with a blue iris and a soft dark outline."},
    {"name": "Cursor: speech bubble", "file": "cursor_talk.png", "ref": "art/reference/old_boot.jpg", "status": "optional", "subject": "A simple chunky white speech bubble icon with three dots inside and a soft dark outline."},
])

def prompt_for(kind, it):
    if it.get("status") == "done" or not (it.get("subject") or it.get("talk")):
        return ""
    if it.get("talk"):
        return TALK_RULES
    rules = {"char": CHAR_RULES, "bg": BG_RULES, "item": ITEM_RULES, "prop": PROP_RULES}[kind]
    return f"{STYLE} {it['subject']} {rules}"

data = []
for s in sections:
    out = []
    for it in s["items"]:
        out.append({**it, "prompt": prompt_for(s["kind"], it)})
    data.append({**s, "items": out})

body = r'''
<title>Baker Art Prompts</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap">
<style>
/* Layout: one long checklist, sticky progress bar, cards in a single column so prompts stay readable. */
:root{
  --bg:#f6f1e4; --paper:#fffaf0; --ink:#1f2a4d; --muted:#5f6b8a; --line:#e3d9c3;
  --coral:#e26d5a; --coral-ink:#8e3426; --sea:#1f6f9f; --sand:#f1e3bf;
  --ok:#2e8b57; --ok-bg:#e3f4ea; --opt:#8a7bb5; --opt-bg:#efeaf8; --need:#c8581a; --need-bg:#fde9db;
  --display:'Fredoka','Trebuchet MS',sans-serif; --body:'Nunito','Segoe UI',system-ui,sans-serif; --mono:ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0f1a2e; --paper:#172641; --ink:#eef2fb; --muted:#a9b4cf; --line:#2c3d60; --coral:#ff8a74; --coral-ink:#ffc3b5; --sea:#7cc4ee; --sand:#2a3b5c;
  --ok:#7fd6a3; --ok-bg:#1d3a2c; --opt:#c7b8f2; --opt-bg:#2e2a4a; --need:#ffb07a; --need-bg:#4a2e1c; color-scheme:dark } }
:root[data-theme="dark"]{
  --bg:#0f1a2e; --paper:#172641; --ink:#eef2fb; --muted:#a9b4cf; --line:#2c3d60; --coral:#ff8a74; --coral-ink:#ffc3b5; --sea:#7cc4ee; --sand:#2a3b5c;
  --ok:#7fd6a3; --ok-bg:#1d3a2c; --opt:#c7b8f2; --opt-bg:#2e2a4a; --need:#ffb07a; --need-bg:#4a2e1c; color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.5;margin:0;padding-block:0 60px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:900px;margin:0 auto}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:clamp(30px,5vw,44px);font-weight:700;line-height:1.1}
h2{font-size:26px;font-weight:600;margin-top:48px}
h3{font-size:19px;font-weight:600}
p{margin:0}
.lead{color:var(--muted);max-width:62ch;margin-top:10px}
header{padding-block:36px 8px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--coral-ink);font-weight:700}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);padding-block:12px;border-bottom:2px solid var(--line);display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.bar .track{flex:1 1 200px;height:12px;background:var(--line);border-radius:999px;overflow:hidden;min-width:0}
.bar .fill{height:100%;width:0;background:linear-gradient(90deg,var(--sea),var(--coral));border-radius:999px;transition:width .3s}
.bar .count{font-family:var(--display);font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.filters{display:flex;gap:8px;flex-wrap:wrap}
.filters button{font:600 13px var(--body);padding:6px 12px;border-radius:999px;border:2px solid var(--line);background:var(--paper);color:var(--ink);cursor:pointer}
.filters button[aria-pressed="true"]{border-color:var(--coral);background:var(--coral);color:#fff}
.filters button:focus-visible,.copy:focus-visible,input:focus-visible{outline:3px solid var(--sea);outline-offset:2px}
.how{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:22px}
.how .step{background:var(--paper);border:2px solid var(--line);border-radius:14px;padding:16px;min-width:0}
.how .step b{font-family:var(--display);font-size:18px;font-weight:600;display:block;margin-bottom:6px}
.rules{margin-top:22px;background:var(--sand);border-radius:14px;padding:16px 18px}
.rules ul{margin:8px 0 0;padding-left:20px}
.rules li{margin:4px 0}
code,.path{font-family:var(--mono);font-size:13px;background:var(--sand);padding:2px 6px;border-radius:6px;word-break:break-all}
.sec-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-top:48px}
.sec-head .folder{font-family:var(--mono);font-size:13px;color:var(--muted)}
.sec-intro{color:var(--muted);max-width:68ch;margin-top:6px}
.cards{display:grid;gap:14px;margin-top:16px}
.card{background:var(--paper);border:2px solid var(--line);border-radius:16px;padding:16px;display:grid;grid-template-columns:28px 1fr;gap:12px 14px;min-width:0}
.card.is-done{opacity:.6}
.card input[type=checkbox]{width:24px;height:24px;margin:2px 0 0;accent-color:var(--coral);cursor:pointer}
.card .top{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:center;min-width:0}
.pill{font:700 11px var(--body);letter-spacing:.08em;text-transform:uppercase;padding:3px 9px;border-radius:999px}
.pill.needed{background:var(--need-bg);color:var(--need)} .pill.done{background:var(--ok-bg);color:var(--ok)} .pill.optional{background:var(--opt-bg);color:var(--opt)}
.meta{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;font-size:14px;color:var(--muted);margin-top:4px;min-width:0}
.meta dt{font-weight:700;color:var(--ink)} .meta dd{margin:0;min-width:0;word-break:break-word}
.prompt{position:relative;margin-top:10px;background:var(--bg);border:1px dashed var(--line);border-radius:12px;padding:14px 14px 14px;min-width:0}
.prompt pre{margin:0;white-space:pre-wrap;word-break:break-word;font:15px/1.5 var(--body);padding-right:84px}
.copy{position:absolute;top:10px;right:10px;font:600 13px var(--body);background:var(--coral);color:#fff;border:0;border-radius:999px;padding:7px 14px;cursor:pointer}
.copy.ok{background:var(--ok)}
.card.is-done .prompt{display:none}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.toolbar button{font:600 13px var(--body);padding:7px 12px;border-radius:999px;border:2px solid var(--line);background:var(--paper);color:var(--ink);cursor:pointer}
footer{margin-top:56px;color:var(--muted);font-size:14px;max-width:68ch}
@media (prefers-reduced-motion:reduce){.bar .fill{transition:none}}
</style>
<div class="wrap">
<header>
  <div class="eyebrow">Baker's Undersea Adventure</div>
  <h1>Art prompts for Gemini</h1>
  <p class="lead">Every picture the game still needs, as a prompt you can paste straight into Gemini. Tick things off as you save them; the page remembers on this computer.</p>
  <div class="how">
    <div class="step"><b>1. Attach the reference</b>Each card names an image to attach first. It keeps every result in the same painted style as Baker and the reef.</div>
    <div class="step"><b>2. Paste the prompt</b>Press Copy, paste into Gemini with the image attached, generate. If the result has a shadow, text or a background, say “Again, on plain white with nothing else” and regenerate.</div>
    <div class="step"><b>3. Save with the exact name</b>Save the result into the folder shown on the card with the file name shown. Spelling matters; the game finds files by name.</div>
    <div class="step"><b>4. Rebuild and look</b>In <code>bakers-undersea-adventure</code> run <code>python tools/build_web.py</code>, reload <code>web/index.html</code>. White backgrounds are removed automatically when I pull the files in; transparent PNGs are even better.</div>
  </div>
  <div class="rules"><b>Rules the game depends on</b>
    <ul>
      <li>Characters, items and props: one subject on plain white, facing right. The game flips them when they need to face left.</li>
      <li>Talk frames: generate the idle picture first, then attach that result and use the talk prompt, so only the mouth changes.</li>
      <li>Backgrounds: 16:9, no characters, bottom third open sand.</li>
      <li>Done and optional cards are collapsed; use the filter to hide them.</li>
    </ul>
  </div>
</header>
<div class="bar" id="bar">
  <div class="count" id="count">0 of 0 done</div>
  <div class="track"><div class="fill" id="fill"></div></div>
  <div class="filters" id="filters">
    <button data-f="all" aria-pressed="true">All</button>
    <button data-f="needed" aria-pressed="false">Still needed</button>
    <button data-f="optional" aria-pressed="false">Optional</button>
    <button data-f="done" aria-pressed="false">Done</button>
  </div>
</div>
<main id="main"></main>
<footer>
  <p>Files live under <code>bakers-undersea-adventure/</code>. When a batch is saved, push it to GitHub or send the images here and I will cut them out and wire them in. The reference images named on the cards are in <code>art/reference/</code>.</p>
</footer>
</div>
<script>
const DATA = __DATA__;
const KEY = "baker_art_prompts_done_v1";
let done = {};
try { done = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { done = {}; }
function save() { try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {} }
let filter = "all";
const main = document.getElementById("main");
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
function render() {
  let total = 0, ticked = 0, html = "";
  for (const sec of DATA) {
    const cards = sec.items.filter(it => {
      const st = it.status === "done" ? "done" : it.status;
      const isDone = st === "done" || !!done[sec.folder + it.file];
      if (filter === "all") return true;
      if (filter === "done") return isDone;
      if (filter === "needed") return st === "needed" && !isDone;
      if (filter === "optional") return st === "optional" && !isDone;
      return true;
    });
    if (!cards.length) continue;
    html += `<section><div class="sec-head"><h2>${esc(sec.title)}</h2><span class="folder">${esc(sec.folder)}</span></div><p class="sec-intro">${esc(sec.intro)}</p><div class="cards">`;
    let lastScene = null;
    for (const it of cards) {
      const id = sec.folder + it.file;
      const preDone = it.status === "done";
      const isDone = preDone || !!done[id];
      if (!preDone) total++; if (!preDone && done[id]) ticked++;
      if (it.scene && it.scene !== lastScene) { html += `<h3 style="margin-top:10px">${esc(it.scene)}</h3>`; lastScene = it.scene; }
      html += `<article class="card ${isDone ? "is-done" : ""}">
        <input type="checkbox" id="cb-${esc(id)}" aria-label="Done: ${esc(it.name)}" ${isDone ? "checked" : ""} ${preDone ? "disabled" : ""} data-id="${esc(id)}">
        <div style="min-width:0">
          <div class="top"><h3>${esc(it.name)}</h3><span class="pill ${esc(it.status)}">${it.status === "done" ? "done" : it.status === "optional" ? "optional" : "needed"}</span></div>
          <dl class="meta">
            <dt>Save as</dt><dd><span class="path">${esc(sec.folder + it.file)}</span></dd>
            ${it.ref ? `<dt>Attach</dt><dd><span class="path">${esc(it.ref)}</span></dd>` : ""}
          </dl>
          ${it.prompt ? `<div class="prompt"><button class="copy" data-copy="${esc(it.prompt)}">Copy</button><pre>${esc(it.prompt)}</pre></div>` : ""}
        </div></article>`;
    }
    html += `</div></section>`;
  }
  main.innerHTML = html || `<p class="sec-intro" style="margin-top:40px">Nothing in this filter.</p>`;
  document.getElementById("count").textContent = `${ticked} of ${total} done`;
  document.getElementById("fill").style.width = total ? (100 * ticked / total) + "%" : "0%";
}
main.addEventListener("change", e => { const cb = e.target.closest("input[type=checkbox]"); if (!cb || cb.disabled) return; done[cb.dataset.id] = cb.checked; if (!cb.checked) delete done[cb.dataset.id]; save(); render(); });
main.addEventListener("click", e => {
  const b = e.target.closest(".copy"); if (!b) return;
  const text = b.dataset.copy;
  const flash = ok => { b.textContent = ok ? "Copied" : "Select and copy"; b.classList.toggle("ok", ok); setTimeout(() => { b.textContent = "Copy"; b.classList.remove("ok"); }, 1600); };
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(() => flash(true), () => { selectPre(b); flash(false); });
  else { selectPre(b); flash(false); }
});
function selectPre(b) { const pre = b.parentElement.querySelector("pre"); const r = document.createRange(); r.selectNodeContents(pre); const s = window.getSelection(); s.removeAllRanges(); s.addRange(r); try { document.execCommand("copy"); } catch (e) {} }
document.getElementById("filters").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; filter = b.dataset.f; for (const x of e.currentTarget.querySelectorAll("button")) x.setAttribute("aria-pressed", String(x === b)); render(); });
render();
</script>
'''.replace("__DATA__", json.dumps(data, ensure_ascii=False))

OUT_FRAG.write_text(body, encoding="utf-8")
full = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + body + '\n</head>\n<body></body>\n</html>\n')
# in the standalone file the markup must sit in <body>, so split at the first <div class="wrap">
head_part, body_part = body.split('<div class="wrap">', 1)
full = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head_part + '</head>\n<body>\n<div class="wrap">' + body_part + '\n</body>\n</html>\n')
OUT_FULL.write_text(full, encoding="utf-8")
n = sum(1 for s in data for it in s["items"] if it["prompt"])
print("prompts:", n, "| fragment", OUT_FRAG.stat().st_size // 1024, "KB | repo file", OUT_FULL.relative_to(REPO))

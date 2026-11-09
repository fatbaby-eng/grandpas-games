import sys, os, re, json
from faster_whisper import WhisperModel
d = sys.argv[1]
model = WhisperModel("small.en", device="cpu", compute_type="int8")
manifest = json.load(open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), 'voice-manifest.json')))
bad = 0
for f in sorted(os.listdir(d)):
    if not f.endswith('.m4a'): continue
    segs, _ = model.transcribe(os.path.join(d, f), language="en", beam_size=5, initial_prompt="Duck, Piggy, Owl, Horse, Sheep, Tractor, Train, Firetruck, Baker. Tap the big duck. Two piggies! A pair! Duck goes in the barn. Where did Sheep go? D is for Duck.")
    heard = " ".join(s.text for s in segs).strip()
    want = manifest[f[:-4]]
    def norm(t):
        t = t.lower().replace('fire truck', 'firetruck').replace('piggies', 'piggys').replace('ache ', 'h ').replace('aitch ', 'h ')
        return [w if w != 'sheep' else 'sheeps' for w in re.sub(r"[^a-z0-9' ]", '', t).split()]
    ok = norm(heard) == norm(want)
    bad += 0 if ok else 1
    print(("OK  " if ok else "??  ") + f[:-4].ljust(34) + " heard: " + heard)
print("mismatches:", bad)

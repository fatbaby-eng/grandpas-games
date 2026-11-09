import json, sys, os, hashlib
from faster_whisper import WhisperModel

src_dir, out_path = sys.argv[1], sys.argv[2]
model = WhisperModel("small.en", device="cpu", compute_type="int8")
prompt = ("Duck, Piggy, Owl, Horse, Sheep, Tractor, Train, Firetruck, Dino, Baker. "
          "Where did Sheep go? Tap the big duck. Tap the little duck. Two ducks! A pair! Two piggies! A pair! "
          "Duck goes in the barn! Tractor goes in the garage! Find the red gift. D is for Duck. Find Duck!")
result = {}
for root, _, files in os.walk(src_dir):
    for f in sorted(files):
        if not f.lower().endswith((".mp3", ".m4a", ".wav")):
            continue
        p = os.path.join(root, f)
        md5 = hashlib.md5(open(p, "rb").read()).hexdigest()[:10]
        segs, info = model.transcribe(p, language="en", word_timestamps=True, initial_prompt=prompt, beam_size=5, condition_on_previous_text=False)
        words, text = [], []
        for s in segs:
            text.append(s.text)
            for w in s.words:
                words.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)})
        result[p] = {"md5": md5, "duration": round(info.duration, 2), "text": " ".join(text).strip(), "words": words}
        print("%-70s %5.1fs %s  %s" % (os.path.relpath(p, src_dir), info.duration, md5, result[p]["text"][:90]), flush=True)
json.dump(result, open(out_path, "w"), indent=0)

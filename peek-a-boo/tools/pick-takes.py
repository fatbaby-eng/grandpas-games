"""Pick the best take for each voice line from a folder of transcribed recordings.

usage: pick_takes.py <words.json from transcribe_dir.py> <manifest.json> <out dir> [skip-list.json]

For each manifest line (file stem -> spoken text): look for the phrase in the
transcript of the recording named after it (last occurrence wins, since the last
take is usually the keeper); if there is none, look in every other recording
(long multi-line takes). Cut the span out with a little room on each side,
never crossing into a neighbouring word.
"""
import json, os, re, subprocess, sys

words_path, manifest_path, out_dir = sys.argv[1:4]
skip = set(json.load(open(sys.argv[4]))) if len(sys.argv) > 4 else set()
os.makedirs(out_dir, exist_ok=True)
recs = json.load(open(words_path))
manifest = json.load(open(manifest_path))

ALIASES = {"piggies": "piggys", "piggie": "piggy", "sheeps": "sheeps", "ache": "h", "aitch": "h", "firetrucks": "firetrucks"}
def norm_tok(t):
    t = re.sub(r"[^a-z0-9']", "", t.lower())
    return ALIASES.get(t, t)
def phrase_tokens(text):
    return [norm_tok(t) for t in re.findall(r"[A-Za-z0-9']+", text)]
def equivalent(a, b):
    if a == b: return True
    return {a, b} in ({"sheep", "sheeps"}, {"piggys", "piggies"}, {"firetruck", "firetrucks"})

def tokens_of(rec):
    toks = []; ws = rec["words"]; i = 0
    while i < len(ws):
        w = dict(ws[i]); w["n"] = norm_tok(w["w"])
        if w["n"] == "fire" and i + 1 < len(ws) and norm_tok(ws[i + 1]["w"]).startswith("truck"):
            nxt = norm_tok(ws[i + 1]["w"]); w["n"] = "firetruck" + ("s" if nxt.endswith("s") else ""); w["e"] = ws[i + 1]["e"]; i += 1
        toks.append(w); i += 1
    return toks

def find_all(toks, phrase):
    hits = []
    for i in range(len(toks) - len(phrase) + 1):
        if all(equivalent(toks[i + k]["n"], phrase[k]) for k in range(len(phrase))):
            hits.append((i, i + len(phrase) - 1))
    return hits

def stem_of(path):
    return re.sub(r"\.[a-z0-9]+$", "", os.path.basename(path).lower())

def similar(a, b):
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio()

tok_cache = {p: tokens_of(r) for p, r in recs.items()}
by_stem = {stem_of(p): p for p in recs}

chosen, missing = {}, []
for stem, text in manifest.items():
    if stem in skip: continue
    phrase = phrase_tokens(text)
    # 1. its own recording (exact or near-miss name), last occurrence
    own = by_stem.get(stem)
    if not own:
        best = max(by_stem, key=lambda s: similar(s, stem))
        if similar(best, stem) >= 0.85 and best not in manifest: own = by_stem[best]
    cand = None
    if own:
        hits = find_all(tok_cache[own], phrase)
        if hits: cand = (own, hits[-1], "own file, take %d of %d" % (len(hits), len(hits)))
    # 2. any long take
    if not cand:
        for p, toks in tok_cache.items():
            if recs[p]["duration"] < 8: continue
            hits = find_all(toks, phrase)
            if hits: cand = (p, hits[-1], "cut from %s (occurrence %d of %d)" % (os.path.basename(p), len(hits), len(hits))); break
    if cand: chosen[stem] = cand
    else: missing.append(stem)

# cut
report = []
for stem, (path, (a, b), how) in chosen.items():
    toks = tok_cache[path]; dur = recs[path]["duration"]
    prev_end = toks[a - 1]["e"] if a > 0 else 0.0
    next_start = toks[b + 1]["s"] if b + 1 < len(toks) else dur
    s = max(prev_end + 0.03, toks[a]["s"] - 0.35, 0.0)
    e = min(next_start - 0.03, toks[b]["e"] + 0.40, dur)
    if e - s < 0.3: e = min(dur, s + 0.6)
    length = round(e - s, 3)
    out = os.path.join(out_dir, stem + ".m4a")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % s, "-t", "%.3f" % length, "-i", path,
                           "-af", "afade=t=in:d=0.03,afade=t=out:st=%.3f:d=0.05,loudnorm=I=-18:TP=-2" % max(0, length - 0.05),
                           "-ac", "1", "-ar", "24000", "-c:a", "aac", "-b:a", "40k", out])
    report.append((stem, length, how))
    print("%-34s %4.2fs  %s" % (stem, length, how))
print("\ncut %d lines; no recording found for %d: %s" % (len(chosen), len(missing), ", ".join(missing)))
json.dump({"chosen": {k: [v[0], v[1], v[2]] for k, v in chosen.items()}, "missing": missing}, open(os.path.join(out_dir, "_report.json"), "w"), indent=1)

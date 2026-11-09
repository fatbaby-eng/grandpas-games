// Puts recorded voice clips into Baker's Peek-a-Boo.
//
//   node tools/voice-build.js recordings/clips index.html
//
// Clips are matched by file name against tools/voice-manifest.json
// (the names in voice-script.md). Each clip is converted to a
// small mono AAC file with the silence trimmed, base64-encoded, and written
// between the VOICE_CLIPS_START / VOICE_CLIPS_END markers in the game. Needs
// ffmpeg on the PATH. Safe to run again after adding more clips.
const fs = require('fs'), path = require('path'), os = require('os'), { execFileSync } = require('child_process');
const [clipDir, htmlPath] = process.argv.slice(2);
if (!clipDir || !htmlPath) { console.error('usage: node docs/peek-a-boo-voice-build.js <clips folder> <index.html>'); process.exit(1); }
const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'voice-manifest.json'), 'utf8'));
const exts = ['.m4a', '.mp3', '.aac', '.wav', '.caf', '.ogg'];
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'peek-voice-'));
const clips = {}, found = [], missing = [], plain = [];
const MIME = { '.m4a': 'audio/mp4', '.mp3': 'audio/mpeg', '.aac': 'audio/aac', '.wav': 'audio/wav', '.caf': 'audio/x-caf', '.ogg': 'audio/ogg' };
const TRIM = 'silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.1,areverse,silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.15,areverse,loudnorm=I=-18:TP=-2';
function ff(args) { try { execFileSync('ffmpeg', ['-y', '-loglevel', 'error'].concat(args), { stdio: ['ignore', 'ignore', 'pipe'] }); return true; } catch (e) { return false; } }
// recordings on disk, by stem; a near-miss name (a typo like whatch_duck_hide) still matches
const onDisk = {}; for (const f of fs.readdirSync(clipDir)) { const ext = path.extname(f).toLowerCase(); if (exts.includes(ext)) onDisk[path.basename(f, path.extname(f)).toLowerCase()] = path.join(clipDir, f); }
function similar(a, b) { const m = a.length, n = b.length, d = []; for (let i = 0; i <= m; i++) { d[i] = [i]; for (let j = 1; j <= n; j++) d[i][j] = i === 0 ? j : Math.min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] === b[j-1] ? 0 : 1)); } return 1 - d[m][n] / Math.max(m, n); }
const nearMiss = [];
// only recordings whose name matches no line at all are candidates for a near-miss match
const leftover = Object.keys(onDisk).filter(stem => !(stem in manifest));
for (const [file, key] of Object.entries(manifest)) {
  let src = onDisk[file];
  if (!src) { let best = null, score = 0.84; for (const stem of leftover) { const sc = similar(file, stem); if (sc > score) { score = sc; best = stem; } } if (best) { src = onDisk[best]; nearMiss.push(best + ' -> ' + file); leftover.splice(leftover.indexOf(best), 1); } }
  if (!src) { missing.push(file); continue; }
  const out = path.join(tmp, file + '.m4a'), mp3 = path.join(tmp, file + '.mp3');
  let data = null, mime = null;
  // best: trimmed, normalized, small mono AAC. then: plain small AAC. then: MP3. last: the file as recorded.
  if (ff(['-i', src, '-af', TRIM, '-ac', '1', '-ar', '24000', '-c:a', 'aac', '-b:a', '40k', out]) || ff(['-i', src, '-ac', '1', '-ar', '24000', '-c:a', 'aac', '-b:a', '40k', out])) { data = fs.readFileSync(out); mime = 'audio/mp4'; }
  else if (ff(['-i', src, '-ac', '1', '-ar', '24000', '-c:a', 'libmp3lame', '-b:a', '48k', mp3])) { data = fs.readFileSync(mp3); mime = 'audio/mpeg'; }
  else { data = fs.readFileSync(src); mime = MIME[path.extname(src).toLowerCase()] || 'audio/mpeg'; plain.push(file); }
  clips[key] = 'data:' + mime + ';base64,' + data.toString('base64');
  found.push(file);
}
// sound effects and music: sfx_<id> and music_loop files in the same folder
const SFX_IDS = ['duck', 'pig', 'owl', 'horse', 'sheep', 'tractor', 'train', 'firetruck', 'dino', 'chime', 'celebration', 'empty', 'nudge', 'flip', 'count'];
const sfx = {}, music = {};
function encodeAny(src, out, extra) {
  if (ff(['-i', src].concat(extra, ['-ac', '1', '-ar', '24000', '-c:a', 'aac', '-b:a', extra.length ? '64k' : '48k', out]))) return 'data:audio/mp4;base64,' + fs.readFileSync(out).toString('base64');
  return 'data:' + (MIME[path.extname(src).toLowerCase()] || 'audio/mpeg') + ';base64,' + fs.readFileSync(src).toString('base64');
}
for (const id of SFX_IDS) { const stem = 'sfx_' + id; if (onDisk[stem]) { sfx[id] = encodeAny(onDisk[stem], path.join(tmp, stem + '.m4a'), ['-af', 'silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.1,areverse,loudnorm=I=-16:TP=-1.5']); found.push(stem); } }
if (onDisk['music_loop']) { music.loop = encodeAny(onDisk['music_loop'], path.join(tmp, 'music_loop.m4a'), ['-af', 'loudnorm=I=-20:TP=-2']); found.push('music_loop'); }

let html = fs.readFileSync(htmlPath, 'utf8');
function writeBlock(startMark, endMark, varName, obj) {
  const a = html.indexOf(startMark), b = html.indexOf(endMark);
  if (a < 0 || b < 0) { console.error(startMark + ' not found in ' + htmlPath); process.exit(1); }
  const body = Object.keys(obj).length ? '{\n      ' + Object.entries(obj).map(([k, v]) => JSON.stringify(k) + ': ' + JSON.stringify(v)).join(',\n      ') + '\n    }' : '{}';
  html = html.slice(0, a) + startMark + '\n    var ' + varName + ' = ' + body + ';\n    ' + html.slice(b);
}
writeBlock('/* VOICE_CLIPS_START */', '/* VOICE_CLIPS_END */', 'VOICE_CLIPS', clips);
if (html.includes('/* SOUND_CLIPS_START */')) { writeBlock('/* SOUND_CLIPS_START */', '/* SOUND_CLIPS_END */', 'SOUND_CLIPS', sfx); writeBlock('/* MUSIC_CLIPS_START */', '/* MUSIC_CLIPS_END */', 'MUSIC_CLIPS', music); }
fs.writeFileSync(htmlPath, html);
const kb = Math.round(Object.values(clips).reduce((n, s) => n + s.length, 0) * 0.75 / 1024);
console.log('wrote ' + Object.keys(clips).length + ' voice clips, ' + Object.keys(sfx).length + ' sound effects, ' + Object.keys(music).length + ' music loop (' + kb + ' KB of voice) into ' + htmlPath);
if (nearMiss.length) console.log('matched by near-miss name: ' + nearMiss.join(', '));
if (plain.length) console.log('ffmpeg could not convert ' + plain.length + ' clips, so they went in as recorded (larger): ' + plain.join(', '));
if (missing.length) console.log('still using the phone voice for ' + missing.length + ' lines: ' + missing.slice(0, 12).join(', ') + (missing.length > 12 ? ', ...' : ''));

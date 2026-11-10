// Music loops, sound effects and optional voice-over clips via HTMLAudio.
(function (B) {
  const BASE = "assets/audio/";
  class AudioManager {
    constructor() {
      this.muted = false; this.musicName = null; this.music = null; this.voice = null;
      this.sfx = {}; this.unlocked = false; this.missing = new Set();
    }
    unlock() { this.unlocked = true; if (this.musicName) { const n = this.musicName; this.musicName = null; this.playMusic(n); } }
    _make(name, exts) {
      const a = document.createElement("audio");
      let i = 0;
      const tryNext = () => { if (i >= exts.length) { this.missing.add(name); return; } a.src = BASE + name + exts[i++]; };
      a.addEventListener("error", tryNext);
      tryNext();
      return a;
    }
    play(name, volume) {
      if (!name || this.muted || !this.unlocked || this.missing.has(name)) return;
      if (!this.sfx[name]) this.sfx[name] = this._make(name, [".ogg", ".wav", ".mp3"]);
      const a = this.sfx[name].cloneNode();
      a.volume = volume == null ? 0.8 : volume;
      a.play().catch(() => {});
    }
    playMusic(name, volume) {
      if (name === this.musicName) return;
      this.musicName = name;
      if (this.music) { this.music.pause(); this.music = null; }
      if (!name || this.muted || !this.unlocked) return;
      const a = this._make(name, [".ogg", ".mp3", ".wav"]);
      a.loop = true; a.volume = volume == null ? 0.5 : volume;
      a.play().catch(() => {});
      this.music = a;
    }
    toggleMute() {
      this.muted = !this.muted;
      if (this.muted) { if (this.music) this.music.pause(); this.stopVoice(); }
      else if (this.music) this.music.play().catch(() => {}); else { const n = this.musicName; this.musicName = null; this.playMusic(n); }
      return this.muted;
    }
    playVoice(name) {
      this.stopVoice();
      if (!name || this.muted || !this.unlocked || this.missing.has("voice/" + name)) return;
      if (window.BUA_VOICES && !window.BUA_VOICES.includes(name)) return;      // clip not recorded yet
      const a = this._make("voice/" + name, [".ogg", ".wav", ".mp3", ".m4a"]);
      a.volume = 1; a.play().catch(() => {});
      this.voice = a;
    }
    stopVoice() { if (this.voice) { this.voice.pause(); this.voice = null; } }
  }
  B.AudioManager = AudioManager;
})(window.BUA);

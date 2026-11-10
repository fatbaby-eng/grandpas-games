// Speech-bubble dialogue driven by dialogue.json (same schema as the Python game).
(function (B) {
  class Dialogue {
    constructor(game) { this.g = game; this.lines = []; this.end = []; this.index = -1; this.active = false; this.choices = []; this.currentId = null; this.t = 0; this.speakerRect = null; }
    start(id) { const e = this.g.content.dialogue[id]; if (!e) { console.warn("no dialogue", id); return; } this.currentId = id; this._begin(e.lines || [], e.end || []); }
    startLines(lines, end) { this.currentId = null; this._begin(lines, end || []); }
    _begin(lines, end) { this.lines = lines.slice(); this.end = end.slice(); this.index = -1; this.active = true; this.advance(); }
    advance() {
      if (!this.active) return;
      this.index++; this.choices = [];
      if (this.index >= this.lines.length) { this.active = false; this.g.audio.stopVoice(); const end = this.end; this.end = []; if (end.length) this.g.actions.run(end); return; }
      const line = this.lines[this.index];
      const voice = line.voice || (this.currentId ? `${this.currentId}_${String(this.index + 1).padStart(2, "0")}` : null);
      if (voice) this.g.audio.playVoice(voice);
      if (line.actions) this.g.actions.run(line.actions);
      if (line.choices) this.choices = line.choices.map((c, i) => ({ c, rect: [0, 0, 0, 0] }));
    }
    choose(choice) { if (choice.actions) this.g.actions.run(choice.actions); if (choice.next) this.start(choice.next); else { this.choices = []; this.advance(); } }
    line() { return this.active && this.index >= 0 && this.index < this.lines.length ? this.lines[this.index] : null; }
    speaker() { const l = this.line(); return l ? (l.speaker || "baker") : null; }
    handle(ev) {
      if (!this.active) return false;
      if (ev.type === "down") {
        if (this.choices.length) { for (const ch of this.choices) if (B.rectHit(ch.rect, ev.x, ev.y)) { this.g.audio.play("click"); this.choose(ch.c); return true; } return true; }
        this.advance(); return true;
      }
      if (ev.type === "key" && (ev.key === " " || ev.key === "Enter") && !this.choices.length) { this.advance(); return true; }
      return ev.type === "down";
    }
    update(dt) { this.t += dt; }
    draw(ctx) {
      const line = this.line(); if (!line) return;
      const sp = line.speaker || "baker"; const ch = this.g.content.characters[sp] || { name: sp, color: [200, 200, 200] };
      const bx = 60, bw = B.W - 120, by = B.PLAY_H - 215, bh = 195;
      // bubble with tail toward the speaker
      ctx.save();
      ctx.shadowColor = "rgba(0,0,0,0.25)"; ctx.shadowBlur = 16; ctx.shadowOffsetY = 6;
      ctx.beginPath(); B.roundRect(ctx, bx, by, bw, bh, 28); ctx.fillStyle = "rgba(255,252,240,0.97)"; ctx.fill();
      ctx.restore();
      ctx.beginPath(); B.roundRect(ctx, bx, by, bw, bh, 28); ctx.lineWidth = 4; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
      const anchor = this.speakerRect && sp !== "baker" ? this.speakerRect : (sp === "baker" ? this.g.player.rect() : null);
      if (anchor) {
        const ax = B.clamp(anchor[0] + anchor[2] / 2, bx + 60, bx + bw - 60);
        ctx.beginPath(); ctx.moveTo(ax - 18, by + 2); ctx.lineTo(ax, by - 26); ctx.lineTo(ax + 18, by + 2); ctx.fillStyle = "rgba(255,252,240,0.97)"; ctx.fill();
        ctx.beginPath(); ctx.moveTo(ax - 18, by + 1); ctx.lineTo(ax, by - 26); ctx.lineTo(ax + 18, by + 1); ctx.stroke();
      }
      B.Art.drawPortrait(ctx, sp, bx + 22, by + 22, 120);
      B.text(ctx, ch.name, bx + 165, by + 18, { size: 26, weight: 700, color: B.rgb(B.shade(ch.color, 0.75)) });
      if (this.choices.length) {
        B.text(ctx, line.text, bx + 165, by + 52, { size: 22, maxWidth: bw - 200 });
        let y = by + 84;
        for (const ch2 of this.choices) {
          ch2.rect = [bx + 165, y, bw - 200, 34];
          ctx.beginPath(); B.roundRect(ctx, ch2.rect[0], ch2.rect[1], ch2.rect[2], ch2.rect[3], 12);
          const hov = this.g.input.hover && B.rectHit(ch2.rect, this.g.input.x, this.g.input.y);
          ctx.fillStyle = hov ? "#ffe59a" : "#fff1c4"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
          B.text(ctx, ch2.c.text, bx + 165 + (bw - 200) / 2, y + 7, { size: 20, weight: 600, align: "center" });
          y += 38;
        }
      } else {
        B.text(ctx, line.text, bx + 165, by + 62, { size: 27, maxWidth: bw - 200 });
        if (Math.floor(this.t * 2) % 2 === 0) B.text(ctx, "click to continue", bx + bw - 24, by + bh - 34, { size: 17, align: "right", color: "#9a95a8" });
      }
    }
  }
  B.Dialogue = Dialogue;
})(window.BUA);

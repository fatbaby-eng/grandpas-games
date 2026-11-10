// The four mini-games. None can be lost; Skip appears after 30 s or 3 slips.
(function (B) {
  class Mini {
    constructor(game, info, onComplete) {
      this.g = game; this.info = info || {}; this.onComplete = onComplete || []; this.t = 0; this.fails = 0; this.done = false; this.msg = ""; this.msgT = 0;
      this.area = [60, 20, B.W - 120, B.PLAY_H - 40]; this.skipRect = [this.area[0] + this.area[2] - 150, this.area[1] + 14, 130, 44]; this.fromMenu = false;
      this.setup();
    }
    setup() {} onEvent() {} onUpdate() {} onDraw() {}
    canSkip() { return this.t >= B.SKIP_AFTER || this.fails >= B.SKIP_FAILS; }
    say(t, s) { this.msg = t; this.msgT = s || 1.6; }
    fail(t) { this.fails++; this.g.audio.play("bubble"); this.say(t || this.info.retry_text || "Almost! Try again."); }
    skip() { if (this.canSkip() && !this.done) this.finish(true); }
    finish(skipped) { if (this.done) return; this.done = true; this.g.audio.play("success"); this.g.endMinigame(this, !!skipped); }
    handle(ev) {
      if (ev.type === "down" && this.canSkip() && B.rectHit(this.skipRect, ev.x, ev.y)) { this.skip(); return true; }
      if (ev.type === "key" && ev.key === "Escape" && this.canSkip()) { this.skip(); return true; }
      this.onEvent(ev); return true;
    }
    update(dt) { this.t += dt; if (this.msgT > 0) { this.msgT -= dt; if (this.msgT <= 0) this.msg = ""; } this.onUpdate(dt); }
    draw(ctx) {
      const [ax, ay, aw, ah] = this.area;
      ctx.fillStyle = "rgba(0,20,50,0.6)"; ctx.fillRect(0, 0, B.W, B.PLAY_H);
      ctx.beginPath(); B.roundRect(ctx, ax, ay, aw, ah, 26); ctx.fillStyle = "#e6f4ff"; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
      B.text(ctx, this.info.title || "", ax + aw / 2, ay + 14, { size: 40, weight: 700, align: "center" });
      B.text(ctx, this.info.instructions || "", ax + aw / 2, ay + 64, { size: 21, align: "center", color: "#3c4664", maxWidth: aw - 340 });
      this.onDraw(ctx);
      if (this.msg) B.text(ctx, this.msg, ax + aw / 2, ay + ah - 62, { size: 30, weight: 700, align: "center", color: "#c8581a" });
      if (this.canSkip()) { const r = this.skipRect; ctx.beginPath(); B.roundRect(ctx, r[0], r[1], r[2], r[3], 14); ctx.fillStyle = "#dcdce6"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = B.Art.OUT; ctx.stroke(); B.text(ctx, this.info.skip_text || "Skip", r[0] + r[2] / 2, r[1] + 9, { size: 24, weight: 600, align: "center" }); }
      else B.text(ctx, `skip appears in ${Math.max(0, Math.ceil(B.SKIP_AFTER - this.t))}s`, ax + aw - 20, ay + 22, { size: 15, align: "right", color: "#7a8296" });
    }
  }

  class BubbleCatch extends Mini {
    setup() { this.net = [this.area[0] + this.area[2] / 2 - 75, this.area[1] + 120, 150, 40]; this.bubbles = []; this.streak = 0; this.spawn = 0; this.keys = 0; this.GOAL = 5; this.shapes = this.info.shapes || ["bubble"]; }
    onEvent(ev) {
      if (ev.type === "move") this.net[0] = B.clamp(ev.x - 75, this.area[0], this.area[0] + this.area[2] - 150);
      if (ev.type === "key") { if (ev.key === "ArrowLeft") this.keys = -1; if (ev.key === "ArrowRight") this.keys = 1; }
      if (ev.type === "keyup") this.keys = 0;
    }
    onUpdate(dt) {
      this.net[0] = B.clamp(this.net[0] + this.keys * 500 * dt, this.area[0], this.area[0] + this.area[2] - 150);
      this.spawn -= dt;
      if (this.spawn <= 0) { this.spawn = B.rand(0.9, 1.4); this.bubbles.push({ x: B.rand(this.area[0] + 80, this.area[0] + this.area[2] - 80), y: this.area[1] + this.area[3] - 40, vy: B.rand(140, 220), ph: B.rand(0, 6), r: B.rand(26, 40), label: B.choice(this.shapes), caught: false }); }
      for (const b of this.bubbles) {
        b.y -= b.vy * dt; b.x += 40 * dt * (Math.floor(this.t * 2 + b.ph) % 2 ? 1 : -1);
        if (!b.caught && B.rectHit(this.net, b.x, b.y)) { b.caught = true; this.streak++; this.g.audio.play("pickup"); this.say((this.info.catch_text || "{label}!").replace("{label}", b.label), 0.8); if (this.streak >= this.GOAL) this.finish(); }
        else if (!b.caught && b.y < this.net[1] - 10) { b.caught = true; if (this.streak > 0) { this.streak = 0; this.fail(); } }
      }
      this.bubbles = this.bubbles.filter(b => b.y > this.area[1] + 60 && !(b.caught && b.y < this.net[1] + this.net[3]));
    }
    onDraw(ctx) {
      B.text(ctx, `Caught in a row: ${this.streak} / ${this.GOAL}`, this.area[0] + 24, this.area[1] + 20, { size: 26, weight: 700, color: "#1e3c78" });
      const n = this.net; ctx.beginPath(); B.roundRect(ctx, n[0], n[1], n[2], n[3], 12); ctx.fillStyle = "#ffc85a"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = "#785014"; ctx.stroke();
      for (let i = 1; i < 6; i++) { ctx.beginPath(); ctx.moveTo(n[0] + i * 25, n[1]); ctx.lineTo(n[0] + i * 25, n[1] + n[3]); ctx.lineWidth = 1; ctx.stroke(); }
      for (const b of this.bubbles) { if (b.caught) continue; B.Art.circle(ctx, b.x, b.y, b.r, "rgba(180,230,255,0.9)", 2.5); ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(b.x - b.r * 0.4, b.y - b.r * 0.4, b.r / 5, 0, 7); ctx.fill(); B.text(ctx, b.label, b.x, b.y - 9, { size: 17, weight: 600, align: "center", color: "#142850" }); }
    }
  }

  class ShellPuzzle extends Mini {
    setup() {
      this.colors = this.info.colors || [[255, 120, 120], [120, 200, 255], [255, 230, 120]];
      const n = this.colors.length; this.target = [0, 1, 2].map(() => Math.floor(Math.random() * n)); this.cur = [0, 1, 2].map(() => Math.floor(Math.random() * n));
      if (this.cur.join() === this.target.join()) this.cur[0] = (this.cur[0] + 1) % n;
      const cx = this.area[0] + this.area[2] / 2; this.rects = [0, 1, 2].map(i => [cx - 260 + i * 200, this.area[1] + 290, 140, 120]); this.check = [cx - 80, this.area[1] + this.area[3] - 130, 160, 50]; this.auto = null;
    }
    onEvent(ev) {
      if (this.auto != null || ev.type !== "down") return;
      if (B.rectHit(this.check, ev.x, ev.y)) { this.doCheck(); return; }
      this.rects.forEach((r, i) => { if (B.rectHit(r, ev.x, ev.y)) { this.cur[i] = (this.cur[i] + 1) % this.colors.length; this.g.audio.play("click"); } });
    }
    doCheck() {
      if (this.cur.join() === this.target.join()) { this.say(this.info.win_text || "It matches!", 1); this.finish(); }
      else { this.fail(); if (this.fails >= 3) { this.say(this.info.auto_text || "The shells sort themselves out!", 2); this.cur = this.target.slice(); this.auto = 1.6; } }
    }
    onUpdate(dt) { if (this.auto != null) { this.auto -= dt; if (this.auto <= 0) this.finish(); } }
    shell(ctx, r, col) { const c = B.rgb(col), d = B.rgb(B.shade(col, 0.7)); ctx.beginPath(); ctx.ellipse(r[0] + r[2] / 2, r[1] + r[3] / 2, r[2] / 2, r[3] / 2, 0, 0, 7); ctx.fillStyle = c; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = d; ctx.stroke(); for (let i = 1; i < 5; i++) { ctx.beginPath(); ctx.moveTo(r[0] + r[2] / 2, r[1] + r[3]); ctx.lineTo(r[0] + r[2] * i / 5, r[1] + 6); ctx.lineWidth = 2; ctx.stroke(); } }
    onDraw(ctx) {
      const cx = this.area[0] + this.area[2] / 2;
      B.text(ctx, this.info.pattern_text || "Match this pattern:", cx, this.area[1] + 120, { size: 22, align: "center", color: "#3c4664" });
      this.target.forEach((t, i) => this.shell(ctx, [cx - 150 + i * 110, this.area[1] + 160, 80, 70], this.colors[t]));
      this.rects.forEach((r, i) => { this.shell(ctx, r, this.colors[this.cur[i]]); B.text(ctx, "click", r[0] + r[2] / 2, r[1] + r[3] + 6, { size: 18, align: "center", color: "#7a8296" }); });
      if (this.auto == null) { const r = this.check; ctx.beginPath(); B.roundRect(ctx, r[0], r[1], r[2], r[3], 14); ctx.fillStyle = "#ffaa3c"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = B.Art.OUT; ctx.stroke(); B.text(ctx, this.info.check_text || "Check!", r[0] + r[2] / 2, r[1] + 10, { size: 26, weight: 700, align: "center" }); }
    }
  }

  const ARROWS = ["left", "up", "down", "right"], KEYS = { ArrowLeft: "left", ArrowUp: "up", ArrowDown: "down", ArrowRight: "right" };
  class CrabDance extends Mini {
    setup() { this.seq = [0, 0, 0, 0].map(() => B.choice(ARROWS)); this.phase = "show"; this.si = 0; this.st = 0.8; this.ii = 0; this.flash = null; this.ft = 0; this.rects = {}; ARROWS.forEach((a, i) => this.rects[a] = [this.area[0] + this.area[2] / 2 - 290 + i * 160, this.area[1] + 330, 130, 110]); this.crabX = this.area[0] + this.area[2] / 2; }
    press(d) {
      if (this.phase !== "input") return;
      this.flash = d; this.ft = 0.3;
      if (d === this.seq[this.ii]) { this.ii++; this.g.audio.play("click"); this.crabX += d === "left" ? -60 : d === "right" ? 60 : 0; if (this.ii >= this.seq.length) { this.say(this.info.win_text || "Perfect moves!", 1); this.finish(); } }
      else { this.fail(this.info.retry_text); this.phase = "show"; this.si = 0; this.st = 1.2; this.ii = 0; }
    }
    onEvent(ev) { if (ev.type === "key" && KEYS[ev.key]) this.press(KEYS[ev.key]); if (ev.type === "down") for (const a of ARROWS) if (B.rectHit(this.rects[a], ev.x, ev.y)) this.press(a); }
    onUpdate(dt) {
      if (this.ft > 0) { this.ft -= dt; if (this.ft <= 0) this.flash = null; }
      if (this.phase === "show") { this.st -= dt; if (this.st <= 0) { if (this.si < this.seq.length) { this.flash = this.seq[this.si]; this.ft = 0.45; this.g.audio.play("bubble"); this.si++; this.st = 0.75; } else { this.phase = "input"; this.say(this.info.your_turn_text || "Your turn!", 1.2); } } }
    }
    onDraw(ctx) {
      const cx = this.area[0] + this.area[2] / 2;
      const status = this.phase === "show" ? (this.info.watch_text || "Watch Sidney...") : `${this.info.repeat_text || "Repeat the moves"}  ${this.ii} / ${this.seq.length}`;
      B.text(ctx, status, cx, this.area[1] + 120, { size: 24, weight: 700, align: "center", color: "#1e3c78" });
      B.Art.drawCharacter(ctx, "sidney", this.crabX - 60, this.area[1] + 190, 120, 90, { t: this.t });
      for (const a of ARROWS) {
        const r = this.rects[a], lit = this.flash === a; ctx.beginPath(); B.roundRect(ctx, r[0], r[1], r[2], r[3], 16); ctx.fillStyle = lit ? "#ffdc5a" : "#c8d2e6"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
        const x = r[0] + r[2] / 2, y = r[1] + r[3] / 2, P = { left: [[x - 35, y], [x + 20, y - 30], [x + 20, y + 30]], right: [[x + 35, y], [x - 20, y - 30], [x - 20, y + 30]], up: [[x, y - 35], [x - 30, y + 20], [x + 30, y + 20]], down: [[x, y + 35], [x - 30, y - 20], [x + 30, y - 20]] }[a];
        B.Art.path(ctx, P); ctx.fillStyle = "#283c64"; ctx.fill();
      }
      B.text(ctx, this.info.keys_text || "Arrow keys or click the arrows", cx, this.area[1] + 460, { size: 18, align: "center", color: "#7a8296" });
    }
  }

  class DJBeat extends Mini {
    setup() { this.N = 8; this.notes = []; for (let i = 0; i < this.N; i++) this.notes.push([this.area[0] + 90 + i * 135, this.area[1] + 250, 100, 100]); this.cols = []; for (let i = 0; i < this.N; i++) this.cols.push(`rgb(${(80 + i * 23) % 256},${(160 + i * 41) % 256},${(220 - i * 17 + 256) % 256})`); this.order = [...Array(this.N).keys()].sort(() => Math.random() - 0.5); this.i = 0; this.wob = {}; }
    onEvent(ev) { if (ev.type !== "down") return; this.notes.forEach((r, i) => { if (B.rectHit(r, ev.x, ev.y)) { if (i === this.order[this.i]) { this.i++; this.g.audio.play("pickup"); if (this.i >= this.N) { this.say(this.info.win_text || "What a beat!", 1); this.finish(); } } else { this.wob[i] = 0.4; this.g.audio.play("click"); } } }); }
    onUpdate(dt) { for (const k of Object.keys(this.wob)) { this.wob[k] -= dt; if (this.wob[k] <= 0) delete this.wob[k]; } }
    onDraw(ctx) {
      const cx = this.area[0] + this.area[2] / 2;
      B.text(ctx, `${this.info.progress_text || "Notes"}  ${this.i} / ${this.N}`, cx, this.area[1] + 120, { size: 24, weight: 700, align: "center", color: "#1e3c78" });
      B.Art.drawCharacter(ctx, "dj", cx - 110, this.area[1] + 380, 220, 150, { t: this.t, talking: true });
      this.notes.forEach((r, i) => {
        const x = r[0] + r[2] / 2 + (this.wob[i] ? Math.sin(this.t * 40) * 6 : 0), y = r[1] + r[3] / 2, lit = this.i < this.N && this.order[this.i] === i, done = this.order.slice(0, this.i).includes(i);
        if (lit) { const g = ctx.createRadialGradient(x, y, 20, x, y, 80); g.addColorStop(0, `rgba(255,255,160,${0.5 + 0.4 * Math.sin(this.t * 8)})`); g.addColorStop(1, "rgba(255,255,160,0)"); ctx.fillStyle = g; ctx.fillRect(x - 80, y - 80, 160, 160); }
        B.Art.circle(ctx, x, y, 50, done ? "#c8c8c8" : this.cols[i], 3);
        B.text(ctx, "♪", x, y - 28, { size: 48, align: "center" });
      });
    }
  }

  B.MINIGAMES = { bubble_catch: BubbleCatch, shell_puzzle: ShellPuzzle, crab_dance: CrabDance, dj_beat: DJBeat };
})(window.BUA);

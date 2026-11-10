// Data-driven scene: hotspots, walking, interaction, ambient effects per scene.
(function (B) {
  const CURSOR = { npc: "talk", item: "hand", humor: "eye", exit: "exit", object: "hand" };

  class Scene {
    constructor(game, id, data) {
      this.g = game; this.id = id; this.data = data;
      this.walkable = data.walkable || [[0, 380], [B.W, 380], [B.W, 630], [0, 630]];
      this.t = 0; this.hover = null; this.talkingTo = null; this.particles = []; this.bg = null; this.debug = false;
      this.confetti = []; for (let i = 0; i < 120; i++) this.confetti.push([Math.random() * B.W, -Math.random() * B.PLAY_H, 40 + Math.random() * 80, ["#ff5a5a", "#ffc83c", "#5adc78", "#5aa0ff", "#e678ff"][i % 5]]);
    }
    onEnter() {
      if (!this.bg) this.bg = B.Art.paintBackground({ ...this.data, id: this.id });
      this.g.audio.playMusic(this.data.music || "underwater");
      this.g.actions.run(this.data.on_enter);
      for (const once of this.data.on_enter_once || []) {
        if (once.flag && !this.g.state.hasFlag(once.flag) && B.check(once.if, this.g.state)) { this.g.state.setFlag(once.flag); this.g.actions.run(once.actions); break; }
      }
    }
    onExit() { this.talkingTo = null; this.g.player.stop(); }

    visible() {
      const s = this.g.state, out = [];
      for (const hs of this.data.hotspots || []) {
        if (hs.type === "item") { const flag = hs.pickup_flag || `picked_${hs.id}`; if (s.hasFlag(flag) || s.inventory.has(hs.item)) continue; }
        if (!B.check(hs.visible_if, s)) continue;
        if (hs.hidden_if && B.check(hs.hidden_if, s)) continue;
        out.push(hs);
      }
      return out;
    }
    at(x, y) { const v = this.visible(); for (let i = v.length - 1; i >= 0; i--) if (B.rectHit(v[i].rect, x, y)) return v[i]; return null; }
    byId(id) { return (this.data.hotspots || []).find(h => h.id === id) || null; }
    cursorFor(hs) { return hs ? (CURSOR[hs.type] || "hand") : "arrow"; }

    handle(ev) {
      if (ev.type === "move") { this.hover = ev.y < B.PLAY_H ? this.at(ev.x, ev.y) : null; return false; }
      if (ev.type === "key" && ev.key === "F1") { this.debug = !this.debug; return true; }
      if (ev.type === "down" && ev.y < B.PLAY_H) {
        if (ev.button === 2) { this.g.state.inventory.deselect(); return true; }
        this.click(ev.x, ev.y); return true;
      }
      return false;
    }
    click(x, y) {
      if (this.g.transitioning) return;
      const p = this.g.player, inv = this.g.state.inventory, sel = inv.selected, hs = this.at(x, y);
      this.talkingTo = null;
      if (!hs) { if (sel) { inv.deselect(); return; } p.setTarget(B.clampToPoly(x, y, this.walkable)); return; }
      const wt = hs.walk_to;
      if (wt && (Math.abs(p.x - wt[0]) > 3 || Math.abs(p.y - wt[1]) > 3)) p.setTarget(wt, () => this.interact(hs, sel));
      else { if (hs.type !== "exit") p.facing = (hs.rect[0] + hs.rect[2] / 2) >= p.x ? "right" : "left"; this.interact(hs, sel); }
    }
    interact(hs, item) {
      const g = this.g, s = g.state;
      if (!this.visible().includes(hs)) return;
      g.dialogue.speakerRect = hs.rect;
      if (item) { s.inventory.deselect(); this.useItem(hs, item); return; }
      switch (hs.type) {
        case "npc": {
          if (hs.counter) s.inc(hs.counter);
          const c = B.pick(hs.dialogue, s); const id = c && typeof c === "object" ? c.id : c;
          if (id) { this.talkingTo = hs.id; g.dialogue.start(id); }
          g.actions.run(hs.on_talk); break;
        }
        case "item": {
          s.setFlag(hs.pickup_flag || `picked_${hs.id}`);
          g.actions.run([{ give_item: hs.item }]);
          this.burst(hs.rect[0] + hs.rect[2] / 2, hs.rect[1] + hs.rect[3] / 2, 10);
          const pickup = g.content.items[hs.item].pickup;
          if (pickup) g.dialogue.startLines([{ speaker: "baker", text: pickup, voice: `pickup_${hs.item}` }]);
          g.actions.run(hs.actions); break;
        }
        case "humor": {
          g.audio.play(hs.sound || "bubble");
          this.burst(hs.rect[0] + hs.rect[2] / 2, hs.rect[1] + hs.rect[3] / 2, 14);
          let n = s.inc(`humor_${this.id}_${hs.id}`) - 1, text = hs.text;
          if (Array.isArray(text)) { n %= text.length; text = text[n]; } else n = 0;
          if (text) g.dialogue.startLines([{ speaker: hs.speaker || "baker", text, voice: `humor_${this.id}_${hs.id}_${String(n + 1).padStart(2, "0")}` }]);
          g.actions.run(hs.actions); break;
        }
        case "exit":
          if (B.check(hs.requires, s)) { g.actions.run(hs.actions); g.switchScene(hs.to, hs.spawn); } else g.actions.run(hs.blocked);
          break;
        case "object":
          if (hs.on_click) g.actions.run(hs.on_click);
          else if (hs.dialogue) { const c = B.pick(hs.dialogue, s); const id = c && typeof c === "object" ? c.id : c; if (id) g.dialogue.start(id); }
          else if (hs.examine) g.dialogue.startLines([{ speaker: "baker", text: hs.examine }]);
          break;
      }
    }
    useItem(hs, item) {
      const g = this.g, uses = hs.use || {}, entry = item in uses ? uses[item] : uses["*"];
      const wrong = g.content.quests.wrong_item_dialogue || "wrong_item";
      if (entry == null) { g.dialogue.start(wrong); return; }
      if (Array.isArray(entry)) { g.actions.run(entry); return; }
      if (!B.check(entry.if, g.state)) { g.actions.run(entry.else || [{ dialogue: wrong }]); return; }
      if (entry.consume) g.state.inventory.remove(item);
      g.actions.run(entry.actions);
    }
    burst(x, y, n) { for (let i = 0; i < n; i++) this.particles.push({ x: x + B.rand(-14, 14), y: y + B.rand(-10, 10), vx: B.rand(-25, 25), vy: B.rand(-90, -40), life: B.rand(0.8, 1.6), max: 1.6, r: B.rand(3, 8) }); }

    update(dt) {
      this.t += dt;
      const g = this.g; g.player.update(dt); g.state.playerPos = [Math.round(g.player.x), Math.round(g.player.y)];
      for (const p of this.particles) { p.x += p.vx * dt; p.y += p.vy * dt; p.life -= dt; }
      this.particles = this.particles.filter(p => p.life > 0);
      if (!g.dialogue.active) this.talkingTo = null;
      if (Math.random() < dt * 0.7) this.particles.push({ x: Math.random() * B.W, y: B.PLAY_H + 10, vx: B.rand(-10, 10), vy: B.rand(-70, -30), life: B.rand(5, 9), max: 9, r: B.rand(2, 5) });
      if (this.id === "festival_grounds" && g.state.hasFlag("shell_returned")) for (const c of this.confetti) { c[1] += c[2] * dt; c[0] += Math.sin(this.t * 2 + c[1] * 0.01) * 20 * dt; if (c[1] > B.PLAY_H) { c[1] = -B.rand(0, 60); c[0] = Math.random() * B.W; } }
    }

    draw(ctx) {
      const g = this.g;
      ctx.drawImage(this.bg, 0, 0);
      this.drawAmbientBack(ctx);
      const items = [];
      for (const hs of this.visible()) {
        if (hs.draw === false) continue;
        const r = hs.rect;
        if (hs.type === "npc" && hs.character) {
          const talking = this.talkingTo === hs.id && g.dialogue.speaker() === hs.character;
          const facing = hs.facing || ((r[0] + r[2] / 2) > g.player.x ? "left" : "right");
          items.push({ y: r[1] + r[3], draw: () => B.Art.drawCharacter(ctx, hs.character, r[0], r[1], r[2], r[3], { facing, talking, t: this.t + B.hash(hs.id) % 10 }) });
        } else if (hs.type === "item") {
          const size = Math.min(r[2], r[3]);
          items.push({ y: r[1] + r[3], draw: () => { ctx.save(); ctx.translate(0, Math.sin(this.t * 3 + r[0]) * 3); B.Art.drawIcon(ctx, hs.item, r[0] + (r[2] - size) / 2, r[1] + (r[3] - size) / 2, size); ctx.restore(); } });
        } else items.push({ y: r[1] + r[3] - 1, draw: () => B.Art.drawProp(ctx, this, hs, this.t) });
      }
      items.sort((a, b) => a.y - b.y);
      let drawn = false; const py = g.player.y, talkingBaker = g.dialogue.speaker() === "baker";
      for (const it of items) { if (!drawn && it.y > py) { g.player.draw(ctx, talkingBaker); drawn = true; } it.draw(); }
      if (!drawn) g.player.draw(ctx, talkingBaker);
      if (this.hover && !g.dialogue.active && !g.minigame) {
        const r = this.hover.rect; ctx.save(); ctx.strokeStyle = "rgba(255,255,200,0.9)"; ctx.lineWidth = 3; ctx.setLineDash([8, 6]); ctx.lineDashOffset = -this.t * 30; ctx.beginPath(); B.roundRect(ctx, r[0] - 6, r[1] - 6, r[2] + 12, r[3] + 12, 14); ctx.stroke(); ctx.restore();
      }
      for (const p of this.particles) { ctx.strokeStyle = `rgba(220,240,255,${Math.max(0, p.life / p.max)})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 7); ctx.stroke(); }
      this.drawAmbientFront(ctx);
      if (this.debug) { ctx.strokeStyle = "#0f0"; ctx.lineWidth = 2; ctx.beginPath(); this.walkable.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.stroke(); for (const hs of this.data.hotspots) { ctx.strokeStyle = "#f0f"; ctx.strokeRect(...hs.rect); B.text(ctx, hs.id, hs.rect[0], hs.rect[1] - 16, { size: 13, color: "#f0f" }); } }
    }
    drawAmbientBack(ctx) {
      if (this.id === "coral_reef") for (let i = 0; i < 9; i++) { const x = 60 + i * 140, s = Math.sin(this.t * 2 + i) * 8; for (let k = 0; k < 5; k++) { ctx.strokeStyle = `rgb(255,${120 + k * 20},170)`; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x + k * 7, 632); ctx.quadraticCurveTo(x + k * 7 + s, 605, x + k * 7 + s * 1.3, 580 - k * 4); ctx.stroke(); } }
      if (this.id === "sunken_ship") for (let i = 0; i < 30; i++) { const x = (i * 97 + this.t * 12 * (1 + i % 3)) % B.W, y = 80 + (i * 53 + Math.sin(this.t + i) * 20) % 540; ctx.fillStyle = "rgba(240,230,190,0.8)"; ctx.fillRect(x, y, 2, 2); }
      if (this.id === "festival_grounds") for (let i = 0; i < 8; i++) { const x = 80 + i * 160 + Math.sin(this.t + i) * 12, y = 150 + (i * 37 + this.t * 15) % 240; const col = ["#ff5a5a", "#ffc83c", "#5adc78", "#5aa0ff", "#e678ff"][i % 5]; ctx.strokeStyle = "#fff"; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x + 18, y + 46); ctx.lineTo(x + 18 + Math.sin(this.t * 2 + i) * 6, y + 90); ctx.stroke(); B.Art.ellipse(ctx, x + 18, y + 23, 18, 23, col, 3); }
    }
    drawAmbientFront(ctx) {
      const g = this.g;
      if (this.id === "kelp_forest") { for (let i = 0; i < 7; i++) { const x = 30 + i * 190; ctx.strokeStyle = "rgba(30,120,60,0.45)"; ctx.lineWidth = 14; ctx.lineCap = "round"; ctx.beginPath(); for (let s = 0; s < 9; s++) { const px = x + Math.sin(this.t * 1.5 + i + s * 0.5) * (6 + s * 3), py = 640 - s * 70; s ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.stroke(); } }
      if (this.id === "dark_cave") {
        const inv = g.state.inventory; const px = g.player.x, py = g.player.y - 30;
        let radius = 130; if (inv.has("lantern")) radius = 400; else if (inv.has("bubble_helmet")) radius = 310;
        radius += Math.sin(this.t * 3) * 8;
        if (!this.darkCv) { this.darkCv = document.createElement("canvas"); this.darkCv.width = B.W; this.darkCv.height = B.PLAY_H; }
        const d = this.darkCv.getContext("2d");
        d.globalCompositeOperation = "source-over"; d.fillStyle = "rgba(0,5,20,0.84)"; d.fillRect(0, 0, B.W, B.PLAY_H);
        d.globalCompositeOperation = "destination-out";
        const cut = (x, y, r, strength) => { const gr = d.createRadialGradient(x, y, r * 0.25, x, y, r); gr.addColorStop(0, `rgba(0,0,0,${strength})`); gr.addColorStop(1, "rgba(0,0,0,0)"); d.fillStyle = gr; d.fillRect(x - r, y - r, r * 2, r * 2); };
        cut(px, py, radius, 1);
        const known = g.state.hasFlag("found_bill") || g.state.hasFlag("shell_freed");
        cut(830, 300, 420, known ? 0.85 : 0.55);                     // glow-worms perched on Bill
        for (let i = 0; i < 26; i++) { const x = (i * 151) % B.W, y = 40 + (i * 83) % 560; cut(x, y, 40, 0.5 + 0.3 * Math.sin(this.t * 2 + i)); }
        ctx.drawImage(this.darkCv, 0, 0);
        for (let i = 0; i < 26; i++) { const x = (i * 151) % B.W, y = 40 + (i * 83) % 560, a = 0.5 + 0.4 * Math.sin(this.t * 2 + i); ctx.fillStyle = `rgba(120,255,220,${a})`; ctx.beginPath(); ctx.arc(x, y, 4 + i % 3, 0, 7); ctx.fill(); }
      }
      if (this.id === "festival_grounds" && g.state.hasFlag("shell_returned")) for (const c of this.confetti) { c[1] += c[2] * dt; c[0] += Math.sin(this.t * 2 + c[1] * 0.01) * 20 * dt; if (c[1] > B.PLAY_H) { c[1] = -B.rand(0, 60); c[0] = Math.random() * B.W; } }
    }

    draw(ctx) {
      const g = this.g;
      ctx.drawImage(this.bg, 0, 0);
      this.drawAmbientBack(ctx);
      const items = [];
      for (const hs of this.visible()) {
        if (hs.draw === false) continue;
        const r = hs.rect;
        if (hs.type === "npc" && hs.character) {
          const talking = this.talkingTo === hs.id && g.dialogue.speaker() === hs.character;
          const facing = hs.facing || ((r[0] + r[2] / 2) > g.player.x ? "left" : "right");
          items.push({ y: r[1] + r[3], draw: () => B.Art.drawCharacter(ctx, hs.character, r[0], r[1], r[2], r[3], { facing, talking, t: this.t + B.hash(hs.id) % 10 }) });
        } else if (hs.type === "item") {
          const size = Math.min(r[2], r[3]);
          items.push({ y: r[1] + r[3], draw: () => { ctx.save(); ctx.translate(0, Math.sin(this.t * 3 + r[0]) * 3); B.Art.drawIcon(ctx, hs.item, r[0] + (r[2] - size) / 2, r[1] + (r[3] - size) / 2, size); ctx.restore(); } });
        } else items.push({ y: r[1] + r[3] - 1, draw: () => B.Art.drawProp(ctx, this, hs, this.t) });
      }
      items.sort((a, b) => a.y - b.y);
      let drawn = false; const py = g.player.y, talkingBaker = g.dialogue.speaker() === "baker";
      for (const it of items) { if (!drawn && it.y > py) { g.player.draw(ctx, talkingBaker); drawn = true; } it.draw(); }
      if (!drawn) g.player.draw(ctx, talkingBaker);
      if (this.hover && !g.dialogue.active && !g.minigame) {
        const r = this.hover.rect; ctx.save(); ctx.strokeStyle = "rgba(255,255,200,0.9)"; ctx.lineWidth = 3; ctx.setLineDash([8, 6]); ctx.lineDashOffset = -this.t * 30; ctx.beginPath(); B.roundRect(ctx, r[0] - 6, r[1] - 6, r[2] + 12, r[3] + 12, 14); ctx.stroke(); ctx.restore();
      }
      for (const p of this.particles) { ctx.strokeStyle = `rgba(220,240,255,${Math.max(0, p.life / p.max)})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 7); ctx.stroke(); }
      this.drawAmbientFront(ctx);
      if (this.debug) { ctx.strokeStyle = "#0f0"; ctx.lineWidth = 2; ctx.beginPath(); this.walkable.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.stroke(); for (const hs of this.data.hotspots) { ctx.strokeStyle = "#f0f"; ctx.strokeRect(...hs.rect); B.text(ctx, hs.id, hs.rect[0], hs.rect[1] - 16, { size: 13, color: "#f0f" }); } }
    }
    drawAmbientBack(ctx) {
      if (this.id === "coral_reef") for (let i = 0; i < 9; i++) { const x = 60 + i * 140, s = Math.sin(this.t * 2 + i) * 8; for (let k = 0; k < 5; k++) { ctx.strokeStyle = `rgb(255,${120 + k * 20},170)`; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x + k * 7, 632); ctx.quadraticCurveTo(x + k * 7 + s, 605, x + k * 7 + s * 1.3, 580 - k * 4); ctx.stroke(); } }
      if (this.id === "sunken_ship") for (let i = 0; i < 30; i++) { const x = (i * 97 + this.t * 12 * (1 + i % 3)) % B.W, y = 80 + (i * 53 + Math.sin(this.t + i) * 20) % 540; ctx.fillStyle = "rgba(240,230,190,0.8)"; ctx.fillRect(x, y, 2, 2); }
      if (this.id === "festival_grounds") for (let i = 0; i < 8; i++) { const x = 80 + i * 160 + Math.sin(this.t + i) * 12, y = 150 + (i * 37 + this.t * 15) % 240; const col = ["#ff5a5a", "#ffc83c", "#5adc78", "#5aa0ff", "#e678ff"][i % 5]; ctx.strokeStyle = "#fff"; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x + 18, y + 46); ctx.lineTo(x + 18 + Math.sin(this.t * 2 + i) * 6, y + 90); ctx.stroke(); B.Art.ellipse(ctx, x + 18, y + 23, 18, 23, col, 3); }
    }
    drawAmbientFront(ctx) {
      const g = this.g;
      if (this.id === "kelp_forest") { for (let i = 0; i < 7; i++) { const x = 30 + i * 190; ctx.strokeStyle = "rgba(30,120,60,0.45)"; ctx.lineWidth = 14; ctx.lineCap = "round"; ctx.beginPath(); for (let s = 0; s < 9; s++) { const px = x + Math.sin(this.t * 1.5 + i + s * 0.5) * (6 + s * 3), py = 640 - s * 70; s ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.stroke(); } }
      if (this.id === "dark_cave") {
        const inv = g.state.inventory; const px = g.player.x, py = g.player.y - 30;
        let radius = 120; if (inv.has("lantern")) radius = 380; else if (inv.has("bubble_helmet")) radius = 300;
        radius += Math.sin(this.t * 3) * 8;
        const dark = ctx.createRadialGradient(px, py, radius * 0.3, px, py, radius);
        dark.addColorStop(0, "rgba(0,5,20,0)"); dark.addColorStop(0.7, "rgba(0,5,20,0.55)"); dark.addColorStop(1, "rgba(0,5,20,0.86)");
        ctx.fillStyle = dark; ctx.fillRect(0, 0, B.W, B.PLAY_H);
        const known = g.state.hasFlag("found_bill") || g.state.hasFlag("shell_freed");
        const gl = ctx.createRadialGradient(850, 310, 40, 850, 310, 360); gl.addColorStop(0, `rgba(120,255,220,${known ? 0.22 : 0.1})`); gl.addColorStop(1, "rgba(120,255,220,0)");
        ctx.fillStyle = gl; ctx.fillRect(0, 0, B.W, B.PLAY_H);
        for (let i = 0; i < 26; i++) { const x = (i * 151) % B.W, y = 40 + (i * 83) % 560, a = 0.4 + 0.4 * Math.sin(this.t * 2 + i); ctx.fillStyle = `rgba(120,255,220,${a})`; ctx.beginPath(); ctx.arc(x, y, 4 + i % 3, 0, 7); ctx.fill(); }
      }
      if (this.id === "festival_grounds" && g.state.hasFlag("shell_returned")) for (const c of this.confetti) { ctx.fillStyle = c[3]; ctx.fillRect(c[0], c[1], 7, 11); }
    }
  }
  B.Scene = Scene;
})(window.BUA);

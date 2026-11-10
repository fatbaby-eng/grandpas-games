// Inventory shelf, buttons, toasts, hint bubble.
(function (B) {
  class Button {
    constructor(rect, label, cb, color) { this.rect = rect; this.label = label; this.cb = cb; this.color = color || "#ffaa3c"; this.enabled = true; }
    hit(x, y) { return this.enabled && B.rectHit(this.rect, x, y); }
    draw(ctx, hoverX, hoverY, size) {
      const r = this.rect, hov = this.hit(hoverX, hoverY);
      ctx.beginPath(); B.roundRect(ctx, r[0], r[1], r[2], r[3], 16); ctx.fillStyle = !this.enabled ? "#b4b4be" : hov ? "#ffd27a" : this.color; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
      B.text(ctx, this.label, r[0] + r[2] / 2, r[1] + r[3] / 2 - (size || 24) * 0.6, { size: size || 24, weight: 600, align: "center" });
    }
  }

  class UI {
    constructor(game) {
      this.g = game; this.toastText = null; this.toastT = 0;
      this.hintBtn = new Button([B.W - 170, B.PLAY_H + 14, 70, 52], "?");
      this.menuBtn = new Button([B.W - 92, B.PLAY_H + 14, 78, 52], "Menu");
      this.hint = { visible: false, text: "", timer: 0, lastProgress: -1, lastScene: null, rect: [B.W - 460, 20, 440, 120] };
    }
    toast(text, s) { this.toastText = text; this.toastT = s || 2.5; }
    slots() { const out = []; let x = 16; for (const id of this.g.state.inventory.items) { out.push([id, [x, B.PLAY_H + 8, 64, 64]]); x += 74; } return out; }

    handleBar(ev) {
      if (ev.y < B.PLAY_H) return false;
      if (ev.type !== "down") return true;
      const g = this.g, inv = g.state.inventory;
      if (this.hintBtn.hit(ev.x, ev.y)) { this.requestHint(); return true; }
      if (this.menuBtn.hit(ev.x, ev.y)) { g.openPause(); return true; }
      for (const [id, r] of this.slots()) if (B.rectHit(r, ev.x, ev.y)) {
        if (ev.button === 2) { g.describeItem(id); return true; }
        if (inv.selected && inv.selected !== id) g.useItemOnItem(inv.selected, id); else { inv.toggle(id); g.audio.play("click"); }
        return true;
      }
      inv.deselect(); return true;
    }
    drawBar(ctx) {
      const g = this.g;
      // wooden shelf
      ctx.fillStyle = "#8b5a2b"; ctx.fillRect(0, B.PLAY_H, B.W, B.BAR_H);
      ctx.fillStyle = "#a66d35"; ctx.fillRect(0, B.PLAY_H, B.W, 10);
      ctx.strokeStyle = "rgba(0,0,0,0.25)"; ctx.lineWidth = 2; for (let x = 0; x < B.W; x += 160) { ctx.beginPath(); ctx.moveTo(x, B.PLAY_H + 12); ctx.lineTo(x + 40, B.H); ctx.stroke(); }
      ctx.strokeStyle = B.Art.OUT; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(0, B.PLAY_H); ctx.lineTo(B.W, B.PLAY_H); ctx.stroke();
      const inv = g.state.inventory; let hover = null;
      for (const [id, r] of this.slots()) {
        ctx.beginPath(); B.roundRect(ctx, r[0], r[1], r[2], r[3], 12); ctx.fillStyle = "rgba(255,240,200,0.35)"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = inv.selected === id ? "#ffe066" : "rgba(60,30,10,0.6)"; ctx.stroke();
        B.Art.drawIcon(ctx, id, r[0] + 8, r[1] + 8, r[2] - 16);
        if (B.rectHit(r, g.input.x, g.input.y)) hover = id;
      }
      if (hover) B.text(ctx, g.content.items[hover].name, 16, B.H - 22, { size: 17, weight: 600, color: "#fff5d6", stroke: "#3a2208", strokeWidth: 3 });
      this.hintBtn.draw(ctx, g.input.x, g.input.y, 34); this.menuBtn.draw(ctx, g.input.x, g.input.y, 22);
    }

    // hints ------------------------------------------------------------------
    currentHint() { const sc = this.g.scene; if (!sc) return null; const c = B.pick(sc.data.hints || [], this.g.state); return c ? c.text : (this.g.content.quests.generic_hint || null); }
    requestHint() { const t = this.currentHint(); if (t) { this.hint.text = t; this.hint.visible = true; this.hint.timer = 0; } }
    updateHint(dt) {
      const g = this.g, h = this.hint;
      if (g.state.progress !== h.lastProgress || g.state.sceneId !== h.lastScene) { h.lastProgress = g.state.progress; h.lastScene = g.state.sceneId; h.timer = 0; h.visible = false; return; }
      if (g.dialogue.active || g.minigame) return;
      h.timer += dt;
      if (g.state.hintsEnabled && !h.visible && h.timer >= B.HINT_DELAY) this.requestHint();
    }
    handleHint(ev) { if (this.hint.visible && ev.type === "down" && B.rectHit(this.hint.rect, ev.x, ev.y)) { this.hint.visible = false; return true; } return false; }
    drawHint(ctx) {
      const h = this.hint; if (!h.visible) return;
      ctx.save(); ctx.font = B.font(22); const lines = B.wrap(ctx, h.text, 400); ctx.restore();
      h.rect[3] = 56 + lines.length * 28;
      const r = h.rect; ctx.beginPath(); B.roundRect(ctx, r[0], r[1], r[2], r[3], 20); ctx.fillStyle = "rgba(255,250,205,0.97)"; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = "#e6aa28"; ctx.stroke();
      ctx.beginPath(); ctx.moveTo(r[0] + 60, r[1] + r[3] - 2); ctx.lineTo(r[0] + 44, r[1] + r[3] + 22); ctx.lineTo(r[0] + 90, r[1] + r[3] - 2); ctx.fillStyle = "rgba(255,250,205,0.97)"; ctx.fill(); ctx.stroke();
      B.text(ctx, "Coral whispers:", r[0] + 18, r[1] + 12, { size: 17, weight: 700, color: "#966414" });
      B.text(ctx, h.text, r[0] + 18, r[1] + 38, { size: 22, maxWidth: 400 });
    }

    updateToast(dt) { if (this.toastT > 0) { this.toastT -= dt; if (this.toastT <= 0) this.toastText = null; } }
    drawToast(ctx) {
      if (!this.toastText) return;
      ctx.save(); ctx.font = B.font(26, 600); const w = ctx.measureText(this.toastText).width + 40; ctx.restore();
      const x = B.W / 2 - w / 2, y = B.PLAY_H - 70;
      ctx.beginPath(); B.roundRect(ctx, x, y, w, 46, 14); ctx.fillStyle = "rgba(255,252,240,0.95)"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
      B.text(ctx, this.toastText, B.W / 2, y + 8, { size: 26, weight: 600, align: "center" });
    }
  }
  B.Button = Button; B.UI = UI;
})(window.BUA);

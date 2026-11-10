// The Game: canvas scaling, input, modes (title / playing / paused / minigames / ending), save/load.
(function (B) {
  class Game {
    constructor(canvas) {
      this.canvas = canvas; this.ctx = canvas.getContext("2d");
      this.content = window.BUA_CONTENT;
      this.audio = new B.AudioManager();
      this.actions = new B.Actions(this);
      this.ui = new B.UI(this);
      this.player = new B.Player();
      this.input = { x: 0, y: 0, hover: false, scale: 1, ox: 0, oy: 0 };
      this.mode = "title"; this.minigame = null; this.scene = null; this.scenes = {}; this.transition = null; this.fade = 0;
      this.ending = []; this.endingIndex = 0; this.cursor = "arrow"; this.t = 0; this.last = 0;
      this.resetState(new B.GameState(this.content.quests.start_scene || "coral_reef"));
      this.buildMenus();
      this.bindInput();
      this.resize(); window.addEventListener("resize", () => this.resize());
      requestAnimationFrame(ts => this.frame(ts));
    }
    resetState(state) { this.state = state; this.dialogue = new B.Dialogue(this); this.ui.hint.visible = false; this.minigame = null; }
    get transitioning() { return !!this.transition || this.fade > 0; }

    // ---- menus -----------------------------------------------------------------
    buildMenus() {
      const ui = this.content.quests.ui || {}, cx = B.W / 2;
      this.titleButtons = [
        new B.Button([cx - 150, 410, 300, 58], ui.new_game || "New Game", () => this.newGame()),
        new B.Button([cx - 150, 480, 300, 58], ui.continue || "Continue", () => this.loadGame()),
      ];
      this.pauseButtons = [
        new B.Button([cx - 150, 170, 300, 50], ui.resume || "Resume", () => this.closePause()),
        new B.Button([cx - 150, 230, 300, 50], ui.save || "Save Game", () => { this.save(); this.ui.toast(ui.saved || "Game saved!"); this.closePause(); }),
        new B.Button([cx - 150, 290, 300, 50], "", () => { this.state.hintsEnabled = !this.state.hintsEnabled; if (!this.state.hintsEnabled) this.ui.hint.visible = false; }),
        new B.Button([cx - 150, 350, 300, 50], "", () => this.audio.toggleMute()),
        new B.Button([cx - 150, 410, 300, 50], ui.minigames || "Mini-games", () => { this.mode = "minigames"; }),
        new B.Button([cx - 150, 470, 300, 50], ui.to_title || "Quit to Title", () => this.toTitle(), "#dcdce6"),
      ];
      this.minigameButtons = []; let y = 200;
      for (const [id, info] of Object.entries(this.content.quests.minigames || {})) { this.minigameButtons.push(new B.Button([cx - 200, y, 400, 50], info.title || id, () => this.startMinigame(id, [], true))); y += 60; }
      this.minigameButtons.push(new B.Button([cx - 200, y + 10, 400, 50], ui.back || "Back", () => { this.mode = "paused"; }, "#dcdce6"));
    }
    refreshToggles() { const ui = this.content.quests.ui || {}, on = ui.on || "On", off = ui.off || "Off"; this.pauseButtons[2].label = `${ui.hints || "Hints"}: ${this.state.hintsEnabled ? on : off}`; this.pauseButtons[3].label = `${ui.sound || "Sound"}: ${this.audio.muted ? off : on}`; }

    // ---- flow ------------------------------------------------------------------
    newGame() { this.resetState(new B.GameState(this.content.quests.start_scene || "coral_reef")); this.scenes = {}; this.mode = "playing"; this.switchScene(this.state.sceneId, null, true); this.actions.run(this.content.quests.on_new_game); }
    loadGame() { const d = B.Save.load(); if (!d) { this.ui.toast((this.content.quests.ui || {}).no_save || "No saved game yet."); return; } this.resetState(B.GameState.fromJSON(d)); this.scenes = {}; this.mode = "playing"; this.switchScene(this.state.sceneId, this.state.playerPos.slice(), true); }
    save() { if (this.scene) B.Save.save(this.state); }
    toTitle() { this.save(); this.mode = "title"; this.audio.playMusic(this.content.quests.title_music || "underwater"); }
    openPause() { if (this.mode === "playing") { this.refreshToggles(); this.mode = "paused"; } }
    closePause() { if (this.mode === "paused" || this.mode === "minigames") this.mode = "playing"; }

    getScene(id) { if (!this.scenes[id]) this.scenes[id] = new B.Scene(this, id, this.content.scenes[id]); return this.scenes[id]; }
    switchScene(id, spawn, instant) {
      if (instant || !this.scene) { this.doSwitch(id, spawn); this.fade = instant ? 0 : 1; this.transition = null; return; }
      this.transition = { id, spawn, t: 0 };
    }
    doSwitch(id, spawn) {
      if (this.scene) this.scene.onExit();
      const sc = this.getScene(id); this.scene = sc; this.state.sceneId = id;
      const pos = spawn || sc.data.spawn || [640, 520]; this.player.teleport(pos); this.state.playerPos = pos.slice();
      sc.onEnter(); this.save();
    }

    // ---- mini-games / ending --------------------------------------------------
    startMinigame(id, onComplete, fromMenu) { const cls = B.MINIGAMES[id]; if (!cls) return; this.minigame = new cls(this, (this.content.quests.minigames || {})[id], onComplete); this.minigame.fromMenu = !!fromMenu; this.mode = "playing"; }
    endMinigame(mg, skipped) { const done = mg.onComplete; this.minigame = null; this.state.minigamesDone.add(mg.constructor.name); this.ui.hint.timer = 0; if (mg.fromMenu) return; this.actions.run(done); }
    startEnding() { this.ending = (this.content.quests.ending || []).filter(s => B.check(s.if, this.state)); this.endingIndex = 0; this.mode = "ending"; this.audio.playMusic(this.content.quests.ending_music || "festival"); this.save(); }
    advanceEnding() { this.endingIndex++; if (this.endingIndex >= this.ending.length) this.mode = "playing"; }

    // ---- items -----------------------------------------------------------------
    useItemOnItem(a, b) {
      const items = this.content.items, entry = (items[a].combine || {})[b] || (items[b].combine || {})[a];
      this.state.inventory.deselect();
      if (!entry) { this.dialogue.start(this.content.quests.wrong_item_dialogue || "wrong_item"); return; }
      for (const id of entry.consume || []) this.state.inventory.remove(id);
      this.actions.run(entry.actions);
    }
    describeItem(id) { const it = this.content.items[id]; this.dialogue.startLines([{ speaker: "baker", text: it.description || it.name }]); }

    // ---- input -----------------------------------------------------------------
    resize() {
      const s = Math.min(window.innerWidth / B.W, window.innerHeight / B.H);
      this.canvas.style.width = Math.floor(B.W * s) + "px"; this.canvas.style.height = Math.floor(B.H * s) + "px";
      this.input.scale = s;
    }
    toGame(e) { const r = this.canvas.getBoundingClientRect(); return [(e.clientX - r.left) / r.width * B.W, (e.clientY - r.top) / r.height * B.H]; }
    bindInput() {
      const cv = this.canvas;
      cv.addEventListener("pointermove", e => { const [x, y] = this.toGame(e); this.input.x = x; this.input.y = y; this.input.hover = true; this.dispatch({ type: "move", x, y }); });
      cv.addEventListener("pointerdown", e => { const [x, y] = this.toGame(e); this.input.x = x; this.input.y = y; this.audio.unlock(); this.dispatch({ type: "down", x, y, button: e.button }); e.preventDefault(); });
      cv.addEventListener("contextmenu", e => e.preventDefault());
      cv.addEventListener("pointerleave", () => { this.input.hover = false; });
      window.addEventListener("keydown", e => { if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " "].includes(e.key)) e.preventDefault(); this.dispatch({ type: "key", key: e.key }); });
      window.addEventListener("keyup", e => this.dispatch({ type: "keyup", key: e.key }));
    }
    dispatch(ev) {
      if (ev.type === "key") {
        if (ev.key === "Escape") { if (this.mode === "playing" && !this.minigame) { this.openPause(); return; } if (this.mode === "paused" || this.mode === "minigames") { this.closePause(); return; } }
        if (ev.key === "h" && this.mode === "playing") { this.state.hintsEnabled = !this.state.hintsEnabled; if (!this.state.hintsEnabled) this.ui.hint.visible = false; return; }
        if (ev.key === "m") { this.audio.toggleMute(); return; }
      }
      if (ev.type === "move" && this.mode === "playing" && !this.minigame && !this.dialogue.active) this.scene && this.scene.handle(ev);
      if (ev.type === "move") { if (this.minigame) this.minigame.onEvent(ev); return; }
      const buttons = this.mode === "title" ? this.titleButtons : this.mode === "paused" ? this.pauseButtons : this.mode === "minigames" ? this.minigameButtons : null;
      if (buttons) { if (ev.type === "down") for (const b of buttons) if (b.hit(ev.x, ev.y)) { this.audio.play("click"); b.cb(); return; } return; }
      if (this.mode === "ending") { if (ev.type === "down" || (ev.type === "key" && (ev.key === " " || ev.key === "Enter"))) this.advanceEnding(); return; }
      if (this.minigame) { this.minigame.handle(ev); return; }
      if (this.dialogue.handle(ev)) return;
      if (this.ui.handleHint(ev)) return;
      if (ev.type === "down" && this.ui.handleBar(ev)) return;
      if (this.scene) this.scene.handle(ev);
    }

    // ---- loop ------------------------------------------------------------------
    frame(ts) {
      const dt = Math.min(0.05, (ts - this.last) / 1000 || 0.016); this.last = ts; this.t += dt;
      this.update(dt); this.draw();
      requestAnimationFrame(t2 => this.frame(t2));
    }
    update(dt) {
      this.ui.updateToast(dt);
      if (this.transition) { this.fade = Math.min(1, this.fade + dt / 0.35); if (this.fade >= 1) { const tr = this.transition; this.transition = null; this.doSwitch(tr.id, tr.spawn); } }
      else if (this.fade > 0) this.fade = Math.max(0, this.fade - dt / 0.35);
      if (this.mode === "playing") {
        this.state.playTime += dt;
        if (this.minigame) this.minigame.update(dt);
        else { if (this.scene) this.scene.update(dt); this.dialogue.update(dt); this.ui.updateHint(dt); }
      } else if (this.mode === "ending" && this.scene) this.scene.update(dt);
      // cursor
      const inv = this.state.inventory;
      if (this.mode !== "playing" || this.minigame || this.dialogue.active) this.cursor = "arrow";
      else if (inv.selected && this.input.y < B.PLAY_H) this.cursor = "item";
      else this.cursor = this.input.y < B.PLAY_H && this.scene ? this.scene.cursorFor(this.scene.hover) : "arrow";
    }
    draw() {
      const ctx = this.ctx; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, B.W, B.H);
      if (this.mode === "title") this.drawTitle(ctx);
      else {
        if (this.scene) this.scene.draw(ctx);
        if (this.fade > 0) { ctx.fillStyle = `rgba(0,0,0,${this.fade})`; ctx.fillRect(0, 0, B.W, B.PLAY_H); }
        this.ui.drawBar(ctx);
        if (this.mode === "playing") { if (this.minigame) this.minigame.draw(ctx); else { this.dialogue.draw(ctx); this.ui.drawHint(ctx); } }
        else if (this.mode === "paused") this.drawMenu(ctx, (this.content.quests.ui || {}).paused || "Paused", this.pauseButtons);
        else if (this.mode === "minigames") this.drawMenu(ctx, (this.content.quests.ui || {}).minigames || "Mini-games", this.minigameButtons);
        else if (this.mode === "ending") this.drawEnding(ctx);
      }
      this.ui.drawToast(ctx);
      if (this.input.hover) B.Art.drawCursor(ctx, this.cursor, this.input.x, this.input.y, this.cursor === "item" ? this.state.inventory.selected : null);
    }
    drawTitle(ctx) {
      const painted = B.Art.Images.find("title.jpg", "title.png", "title.webp");
      const im = painted && B.Art.Images.get(painted);
      if (im) {
        const s = Math.max(B.W / im.naturalWidth, B.H / im.naturalHeight), dw = im.naturalWidth * s, dh = im.naturalHeight * s;
        ctx.drawImage(im, (B.W - dw) / 2, (B.H - dh) / 2, dw, dh);
        // title in the open water top-left, buttons bottom-left, Baker stays visible on the right
        B.text(ctx, "Baker's", 70, 48, { size: 50, weight: 700, color: "#fff6dc", stroke: B.Art.OUT, strokeWidth: 9 });
        B.text(ctx, "Undersea", 70, 100, { size: 82, weight: 700, color: "#ffd84d", stroke: B.Art.OUT, strokeWidth: 11 });
        B.text(ctx, "Adventure", 70, 186, { size: 82, weight: 700, color: "#ffd84d", stroke: B.Art.OUT, strokeWidth: 11 });
        this.titleButtons[0].rect = [90, 560, 300, 58]; this.titleButtons[1].rect = [90, 630, 300, 58];
        this.titleButtons[1].enabled = B.Save.exists();
        for (const b of this.titleButtons) b.draw(ctx, this.input.x, this.input.y, 30);
        B.text(ctx, this.content.quests.tagline || "", 420, 580, { size: 24, color: "#fff6dc", stroke: B.Art.OUT, strokeWidth: 6, maxWidth: 560 });
        B.text(ctx, "Click anywhere to turn the sound on. Press M to mute.", 420, 650, { size: 18, color: "#e6f4ff", stroke: B.Art.OUT, strokeWidth: 4 });
        return;
      }
      const start = this.content.quests.start_scene || "coral_reef";
      const sc = this.getScene(start); if (!sc.bg) sc.bg = B.Art.paintBackground({ ...sc.data, id: start });
      ctx.drawImage(sc.bg, 0, 0); ctx.fillStyle = "#8b5a2b"; ctx.fillRect(0, B.PLAY_H, B.W, B.BAR_H);
      ctx.fillStyle = "rgba(0,20,50,0.25)"; ctx.fillRect(0, 0, B.W, B.PLAY_H);
      B.Art.drawCharacter(ctx, "baker", B.W / 2 - 150, 190, 300, 200, { t: this.t });
      B.text(ctx, "Baker's", B.W / 2, 36, { size: 54, weight: 700, align: "center", color: "#fff1c4", stroke: B.Art.OUT, strokeWidth: 9 });
      B.text(ctx, "Undersea Adventure", B.W / 2, 92, { size: 72, weight: 700, align: "center", color: "#ffd84d", stroke: B.Art.OUT, strokeWidth: 10 });
      B.text(ctx, this.content.quests.tagline || "", B.W / 2, 560, { size: 26, align: "center", color: "#e6f4ff", stroke: B.Art.OUT, strokeWidth: 5 });
      this.titleButtons[0].rect = [B.W / 2 - 150, 410, 300, 58]; this.titleButtons[1].rect = [B.W / 2 - 150, 480, 300, 58];
      this.titleButtons[1].enabled = B.Save.exists();
      for (const b of this.titleButtons) b.draw(ctx, this.input.x, this.input.y, 30);
      B.text(ctx, "Click anywhere to turn the sound on. Press M to mute.", B.W / 2, 672, { size: 20, align: "center", color: "#fff5d6" });
    }
    drawMenu(ctx, title, buttons) {
      ctx.fillStyle = "rgba(0,10,30,0.6)"; ctx.fillRect(0, 0, B.W, B.H);
      ctx.beginPath(); B.roundRect(ctx, B.W / 2 - 240, 80, 480, 500, 26); ctx.fillStyle = "#fffcf0"; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
      B.text(ctx, title, B.W / 2, 100, { size: 44, weight: 700, align: "center" });
      for (const b of buttons) b.draw(ctx, this.input.x, this.input.y, 26);
    }
    drawEnding(ctx) {
      if (!this.ending.length) return;
      const s = this.ending[Math.min(this.endingIndex, this.ending.length - 1)];
      ctx.beginPath(); B.roundRect(ctx, 140, 120, B.W - 280, 380, 30); ctx.fillStyle = "rgba(255,250,230,0.97)"; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = B.Art.OUT; ctx.stroke();
      let y = 160; if (s.speaker) { B.Art.drawPortrait(ctx, s.speaker, B.W / 2 - 60, y, 120); y += 140; }
      B.text(ctx, s.text, B.W / 2, y, { size: 32, align: "center", maxWidth: B.W - 360 });
      B.text(ctx, (this.content.quests.ui || {}).click_continue || "click to continue", B.W - 170, 468, { size: 20, align: "right", color: "#9a95a8" });
    }
  }
  B.Game = Game;
})(window.BUA);

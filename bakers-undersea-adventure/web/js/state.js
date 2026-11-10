// Inventory, game state and localStorage save/load.
(function (B) {
  class Inventory {
    constructor(onChange) { this.items = []; this.selected = null; this.onChange = onChange; }
    add(id) { if (this.items.includes(id)) return false; this.items.push(id); this._c(); return true; }
    remove(id) { const i = this.items.indexOf(id); if (i < 0) return false; this.items.splice(i, 1); if (this.selected === id) this.selected = null; this._c(); return true; }
    has(id) { return this.items.includes(id); }
    select(id) { if (id == null || this.items.includes(id)) this.selected = id; }
    deselect() { this.selected = null; }
    toggle(id) { this.selected = this.selected === id ? null : (this.items.includes(id) ? id : this.selected); }
    load(list) { this.items = [...new Set(list)]; this.selected = null; this._c(); }
    _c() { if (this.onChange) this.onChange(); }
  }

  class GameState {
    constructor(startScene) {
      this.flags = new Set(); this.counters = {};
      this.inventory = new Inventory(() => this.progress++);
      this.sceneId = startScene || "coral_reef"; this.playerPos = [640, 520];
      this.hintsEnabled = true; this.minigamesDone = new Set(); this.playTime = 0; this.progress = 0;
    }
    hasFlag(f) { return this.flags.has(f); }
    setFlag(f) { if (this.flags.has(f)) return false; this.flags.add(f); this.progress++; return true; }
    clearFlag(f) { if (!this.flags.has(f)) return false; this.flags.delete(f); this.progress++; return true; }
    inc(c) { this.counters[c] = (this.counters[c] || 0) + 1; return this.counters[c]; }
    toJSON() {
      return { version: 1, scene: this.sceneId, player_pos: this.playerPos.map(Math.round), inventory: [...this.inventory.items],
        flags: [...this.flags].sort(), counters: { ...this.counters }, hints_enabled: this.hintsEnabled,
        minigames_done: [...this.minigamesDone], play_time: Math.round(this.playTime) };
    }
    static fromJSON(d) {
      const s = new GameState(d.scene);
      s.playerPos = d.player_pos || [640, 520];
      s.flags = new Set(d.flags || []); s.counters = { ...(d.counters || {}) };
      s.inventory.load(d.inventory || []); s.hintsEnabled = d.hints_enabled !== false;
      s.minigamesDone = new Set(d.minigames_done || []); s.playTime = d.play_time || 0;
      return s;
    }
  }

  const SAVE_KEY = "bakers_undersea_adventure_save_v1";
  const Save = {
    exists() { try { return !!localStorage.getItem(SAVE_KEY); } catch (e) { return false; } },
    save(state) { try { localStorage.setItem(SAVE_KEY, JSON.stringify(state.toJSON())); return true; } catch (e) { return false; } },
    load() { try { const raw = localStorage.getItem(SAVE_KEY); return raw ? JSON.parse(raw) : null; } catch (e) { return null; } },
    clear() { try { localStorage.removeItem(SAVE_KEY); } catch (e) { /* ignore */ } },
  };

  B.Inventory = Inventory; B.GameState = GameState; B.Save = Save;
})(window.BUA);

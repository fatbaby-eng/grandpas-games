// Interpreter for the JSON action lists (same vocabulary as the Python game).
(function (B) {
  class Actions {
    constructor(game) { this.g = game; }
    run(actions) {
      if (!actions) return;
      if (!Array.isArray(actions)) actions = [actions];
      for (const a of actions) this.one(a);
    }
    one(a) {
      const g = this.g, s = g.state;
      if ("if" in a) { this.run(B.check(a.if, s) ? a.then : a.else); return; }
      if ("set_flag" in a) s.setFlag(a.set_flag);
      if ("clear_flag" in a) s.clearFlag(a.clear_flag);
      if ("inc" in a) s.inc(a.inc);
      if ("give_item" in a && s.inventory.add(a.give_item)) { g.audio.play("pickup"); g.ui.toast(`Got: ${g.content.items[a.give_item].name}!`); }
      if ("remove_item" in a) s.inventory.remove(a.remove_item);
      if ("sound" in a) g.audio.play(a.sound);
      if ("music" in a) g.audio.playMusic(a.music);
      if ("toast" in a) g.ui.toast(a.toast);
      if ("say" in a) g.dialogue.startLines([{ speaker: a.speaker || "baker", text: a.say, voice: a.voice }]);
      if ("dialogue" in a) g.dialogue.start(a.dialogue);
      if ("goto" in a) g.switchScene(a.goto, a.spawn);
      if ("minigame" in a) g.startMinigame(a.minigame, a.on_complete || []);
      if ("ending" in a) g.startEnding();
      if ("save" in a) g.save();
    }
  }
  B.Actions = Actions;
})(window.BUA);

// Baker: walks in straight lines to click targets, faces the way he's going.
(function (B) {
  class Player {
    constructor() { this.x = 640; this.y = 520; this.target = null; this.onArrive = null; this.facing = "right"; this.W = 120; this.H = 78; this.t = 0; }
    get moving() { return !!this.target; }
    rect() { return [this.x - this.W / 2, this.y - this.H, this.W, this.H]; }
    teleport(p) { this.x = p[0]; this.y = p[1]; this.target = null; this.onArrive = null; }
    setTarget(p, cb) { this.target = [p[0], p[1]]; this.onArrive = cb || null; if (Math.abs(p[0] - this.x) > 4) this.facing = p[0] > this.x ? "right" : "left"; }
    stop() { this.target = null; this.onArrive = null; }
    update(dt) {
      this.t += dt;
      if (!this.target) return;
      const dx = this.target[0] - this.x, dy = this.target[1] - this.y, d = Math.hypot(dx, dy), step = B.PLAYER_SPEED * dt;
      if (d <= step) { this.x = this.target[0]; this.y = this.target[1]; this.target = null; const cb = this.onArrive; this.onArrive = null; if (cb) cb(); }
      else { this.x += dx / d * step; this.y += dy / d * step; }
    }
    draw(ctx, talking) {
      const r = this.rect();
      // soft shadow on the sand
      ctx.fillStyle = "rgba(0,0,0,0.18)"; ctx.beginPath(); ctx.ellipse(this.x, this.y + 4, this.W * 0.38, 9, 0, 0, 7); ctx.fill();
      B.Art.drawCharacter(ctx, "baker", r[0], r[1], r[2], r[3], { facing: this.facing, talking, t: this.t, moving: this.moving });
    }
  }
  B.Player = Player;
})(window.BUA);

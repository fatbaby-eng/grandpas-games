// Shared helpers: constants, the condition language, text wrapping, maths.
window.BUA = window.BUA || {};
(function (B) {
  B.W = 1280; B.H = 720; B.BAR_H = 80; B.PLAY_H = 640;
  B.HINT_DELAY = 180; B.SKIP_AFTER = 30; B.SKIP_FAILS = 3; B.PLAYER_SPEED = 260;
  B.FONT = "'Fredoka', 'Trebuchet MS', 'Segoe UI', sans-serif";

  B.clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  B.lerp = (a, b, t) => a + (b - a) * t;
  B.rand = (a, b) => a + Math.random() * (b - a);
  B.choice = arr => arr[Math.floor(Math.random() * arr.length)];
  B.hash = s => { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return Math.abs(h); };

  // Seeded RNG for deterministic background painting
  B.seeded = function (seed) {
    let s = (B.hash(String(seed)) || 1) >>> 0;
    return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  };

  B.rectHit = (r, x, y) => x >= r[0] && y >= r[1] && x <= r[0] + r[2] && y <= r[1] + r[3];

  // ---- Conditions (same language as the Python game) -------------------------
  B.check = function (cond, state) {
    if (cond == null) return true;
    if (Array.isArray(cond)) return cond.every(c => B.check(c, state));
    for (const key of Object.keys(cond)) {
      const v = cond[key];
      switch (key) {
        case "flag": if (!state.hasFlag(v)) return false; break;
        case "not_flag": if (state.hasFlag(v)) return false; break;
        case "has": if (!state.inventory.has(v)) return false; break;
        case "not_has": if (state.inventory.has(v)) return false; break;
        case "counter_gte": if ((state.counters[v[0]] || 0) < v[1]) return false; break;
        case "counter_lt": if ((state.counters[v[0]] || 0) >= v[1]) return false; break;
        case "all": if (!v.every(c => B.check(c, state))) return false; break;
        case "any": if (!v.some(c => B.check(c, state))) return false; break;
        case "not": if (B.check(v, state)) return false; break;
        default: throw new Error("Unknown condition key " + key);
      }
    }
    return true;
  };
  B.pick = function (options, state) {
    if (!Array.isArray(options)) return options;
    for (const o of options) if (o && typeof o === "object" && B.check(o.if, state)) return o;
    return null;
  };

  // ---- Point in polygon / clamp to polygon -------------------------------------
  B.pointInPoly = function (x, y, poly) {
    let inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const [x1, y1] = poly[i], [x2, y2] = poly[j];
      if ((y1 > y) !== (y2 > y) && x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1) inside = !inside;
    }
    return inside;
  };
  B.clampToPoly = function (x, y, poly) {
    if (B.pointInPoly(x, y, poly)) return [x, y];
    let best = [x, y], bd = Infinity;
    for (let i = 0; i < poly.length; i++) {
      const [ax, ay] = poly[i], [bx, by] = poly[(i + 1) % poly.length];
      const dx = bx - ax, dy = by - ay, len = dx * dx + dy * dy || 1;
      const t = B.clamp(((x - ax) * dx + (y - ay) * dy) / len, 0, 1);
      const cx = ax + t * dx, cy = ay + t * dy, d = (cx - x) ** 2 + (cy - y) ** 2;
      if (d < bd) { bd = d; best = [cx, cy]; }
    }
    return best;
  };

  // ---- Text ----------------------------------------------------------------------
  B.font = (size, weight) => `${weight || 500} ${size}px ${B.FONT}`;
  B.wrap = function (ctx, text, maxWidth) {
    const lines = [];
    for (const para of String(text).split("\n")) {
      let cur = "";
      for (const word of para.split(" ")) {
        const trial = (cur + " " + word).trim();
        if (ctx.measureText(trial).width <= maxWidth || !cur) cur = trial;
        else { lines.push(cur); cur = word; }
      }
      lines.push(cur);
    }
    return lines;
  };
  B.text = function (ctx, text, x, y, opts) {
    opts = opts || {};
    ctx.save();
    ctx.font = B.font(opts.size || 24, opts.weight);
    ctx.textAlign = opts.align || "left";
    ctx.textBaseline = "top";
    const lines = opts.maxWidth ? B.wrap(ctx, text, opts.maxWidth) : [String(text)];
    const lh = (opts.size || 24) * 1.25;
    lines.forEach((line, i) => {
      if (opts.stroke) { ctx.lineWidth = opts.strokeWidth || 5; ctx.strokeStyle = opts.stroke; ctx.lineJoin = "round"; ctx.strokeText(line, x, y + i * lh); }
      ctx.fillStyle = opts.color || "#1d2b4a";
      ctx.fillText(line, x, y + i * lh);
    });
    ctx.restore();
    return y + lines.length * lh;
  };
  B.roundRect = function (ctx, x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  };
  B.rgb = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a == null ? 1 : a})`;
  B.shade = (c, k) => c.map(v => Math.round(B.clamp(v * k, 0, 255)));
  B.tint = (c, k) => c.map(v => Math.round(B.clamp(v + (255 - v) * k, 0, 255)));
})(window.BUA);

// Vector "painted cartoon" art: thick outlines, big eyes, saturated reef colours.
// Everything here is drawn with canvas paths so it scales and animates; real
// bitmap art can replace any piece later by hooking the same function names.
(function (B) {
  const OUT = "#1f2a4d";
  const C = B.BUA_CONTENT || window.BUA_CONTENT;

  function path(ctx, pts, close) {
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    if (close !== false) ctx.closePath();
  }
  function fillStroke(ctx, fill, lw) {
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    ctx.lineWidth = lw == null ? 3 : lw; ctx.strokeStyle = OUT; ctx.lineJoin = "round"; ctx.lineCap = "round"; ctx.stroke();
  }
  function ellipse(ctx, x, y, rx, ry, fill, lw, rot) {
    ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot || 0, 0, Math.PI * 2); fillStroke(ctx, fill, lw);
  }
  function circle(ctx, x, y, r, fill, lw) { ellipse(ctx, x, y, r, r, fill, lw); }
  function eye(ctx, x, y, r, blink, px, py) {
    if (blink) { ctx.beginPath(); ctx.moveTo(x - r, y); ctx.lineTo(x + r, y); fillStroke(ctx, null, 3); return; }
    circle(ctx, x, y, r, "#fff", 2.5);
    ctx.fillStyle = "#1d2b4a"; ctx.beginPath(); ctx.arc(x + (px || 0) * r * 0.3, y + (py || 0) * r * 0.3, r * 0.5, 0, 7); ctx.fill();
    ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(x + r * 0.25, y - r * 0.3, r * 0.18, 0, 7); ctx.fill();
  }
  function mouth(ctx, x, y, w, talking, t) {
    ctx.beginPath();
    if (talking && Math.floor(t * 9) % 2 === 0) { ctx.ellipse(x, y + 3, w * 0.35, w * 0.3, 0, 0, 7); fillStroke(ctx, "#5a2a3a", 2.5); }
    else { ctx.moveTo(x - w / 2, y); ctx.quadraticCurveTo(x, y + w * 0.5, x + w / 2, y); fillStroke(ctx, null, 2.5); }
  }
  function grad(ctx, x0, y0, x1, y1, stops) {
    const g = ctx.createLinearGradient(x0, y0, x1, y1); stops.forEach(s => g.addColorStop(s[0], s[1])); return g;
  }
  const rgb = B.rgb, shade = B.shade, tint = B.tint;

  // ---------------------------------------------------------------- characters
  // Each draws into a 100 x 100 box facing right; the caller scales to the hotspot.
  const CHARS = {
    fish(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.7)), l = rgb(tint(col, 0.45));
      // tail
      path(ctx, [[22, 50], [2, 28], [8, 50], [2, 72]]); fillStroke(ctx, d);
      // body
      ctx.beginPath(); ctx.ellipse(55, 52, 36, 26, 0, 0, 7); fillStroke(ctx, c);
      // belly
      ctx.save(); ctx.beginPath(); ctx.ellipse(55, 52, 36, 26, 0, 0, 7); ctx.clip();
      ctx.fillStyle = l; ctx.beginPath(); ctx.ellipse(58, 66, 30, 14, 0, 0, 7); ctx.fill(); ctx.restore();
      // dorsal + side fin
      path(ctx, [[42, 28], [52, 10], [66, 28]]); fillStroke(ctx, d);
      ctx.beginPath(); ctx.ellipse(48, 58, 10, 6, -0.6, 0, 7); fillStroke(ctx, d);
      // stripes
      ctx.strokeStyle = d; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(40, 32); ctx.quadraticCurveTo(36, 50, 42, 72); ctx.stroke();
      // lips / mouth, cheek, eye
      ctx.fillStyle = "rgba(255,120,120,0.35)"; ctx.beginPath(); ctx.arc(80, 58, 6, 0, 7); ctx.fill();
      mouth(ctx, 86, 58, 10, o.talking, o.t);
      eye(ctx, 74, 44, 8, o.blink, 0.5, 0);
    },
    seahorse(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.7)), l = rgb(tint(col, 0.4));
      // curled tail + body
      ctx.beginPath(); ctx.moveTo(50, 30); ctx.bezierCurveTo(70, 40, 70, 70, 52, 82); ctx.bezierCurveTo(40, 90, 30, 84, 36, 76);
      ctx.bezierCurveTo(42, 70, 52, 76, 46, 80); ctx.lineTo(40, 70); ctx.bezierCurveTo(32, 50, 36, 34, 50, 30); fillStroke(ctx, c);
      // belly ridges
      ctx.strokeStyle = d; ctx.lineWidth = 2; for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(42 + i, 44 + i * 9); ctx.lineTo(56 + i, 46 + i * 9); ctx.stroke(); }
      // head + snout
      ctx.beginPath(); ctx.ellipse(50, 24, 16, 13, 0, 0, 7); fillStroke(ctx, c);
      ctx.beginPath(); ctx.moveTo(62, 24); ctx.lineTo(84, 22); ctx.lineTo(84, 29); ctx.lineTo(62, 31); ctx.closePath(); fillStroke(ctx, c);
      // crown fin + back fin
      path(ctx, [[36, 14], [42, 2], [48, 12], [54, 1], [58, 13]]); fillStroke(ctx, l);
      path(ctx, [[36, 44], [22, 40], [26, 54], [20, 60], [34, 62]]); fillStroke(ctx, l);
      ctx.fillStyle = "rgba(255,120,150,0.35)"; ctx.beginPath(); ctx.arc(58, 30, 4, 0, 7); ctx.fill();
      eye(ctx, 52, 22, 6, o.blink, 0.4, 0);
    },
    grouper(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.7)), l = rgb(tint(col, 0.4));
      path(ctx, [[18, 50], [0, 26], [8, 50], [0, 74]]); fillStroke(ctx, d);
      ctx.beginPath(); ctx.ellipse(54, 52, 42, 32, 0, 0, 7); fillStroke(ctx, c);
      ctx.save(); ctx.beginPath(); ctx.ellipse(54, 52, 42, 32, 0, 0, 7); ctx.clip();
      ctx.fillStyle = l; ctx.beginPath(); ctx.ellipse(60, 70, 34, 16, 0, 0, 7); ctx.fill();
      ctx.fillStyle = d; [[30, 40], [44, 32], [40, 58], [58, 36]].forEach(p => { ctx.beginPath(); ctx.arc(p[0], p[1], 4, 0, 7); ctx.fill(); });
      ctx.restore();
      path(ctx, [[40, 22], [56, 6], [70, 24]]); fillStroke(ctx, d);
      ctx.beginPath(); ctx.ellipse(46, 62, 12, 7, -0.5, 0, 7); fillStroke(ctx, d);
      mouth(ctx, 88, 60, 14, o.talking, o.t);
      ctx.fillStyle = "rgba(255,120,120,0.35)"; ctx.beginPath(); ctx.arc(80, 62, 6, 0, 7); ctx.fill();
      // spectacles
      eye(ctx, 76, 44, 8, o.blink, 0.4, 0);
      ctx.beginPath(); ctx.arc(76, 44, 12, 0, 7); fillStroke(ctx, null, 2.5);
      ctx.beginPath(); ctx.moveTo(64, 44); ctx.lineTo(50, 40); fillStroke(ctx, null, 2.5);
      // little bun hairdo
      ctx.beginPath(); ctx.arc(60, 18, 7, 0, 7); fillStroke(ctx, "#e9e4f5");
    },
    puffer(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.7)), l = rgb(tint(col, 0.45));
      const r = 34, cx = 54, cy = 52;
      for (let a = 0; a < 360; a += 24) {
        const rad = a * Math.PI / 180, x = cx + Math.cos(rad) * r, y = cy + Math.sin(rad) * r;
        path(ctx, [[x - Math.sin(rad) * 4, y + Math.cos(rad) * 4], [x + Math.cos(rad) * 12, y + Math.sin(rad) * 12], [x + Math.sin(rad) * 4, y - Math.cos(rad) * 4]]); fillStroke(ctx, d, 2.5);
      }
      path(ctx, [[22, 52], [6, 38], [10, 52], [6, 66]]); fillStroke(ctx, d);
      circle(ctx, cx, cy, r, c);
      ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.clip(); ctx.fillStyle = l; ctx.beginPath(); ctx.ellipse(cx + 4, cy + 18, 28, 14, 0, 0, 7); ctx.fill(); ctx.restore();
      ctx.beginPath(); ctx.ellipse(44, 60, 9, 6, -0.4, 0, 7); fillStroke(ctx, d);
      // grumpy brows
      ctx.beginPath(); ctx.moveTo(62, 34); ctx.lineTo(78, 40); fillStroke(ctx, null, 3);
      eye(ctx, 72, 46, 7, o.blink, 0.3, 0.2);
      ctx.beginPath(); ctx.moveTo(78, 64); ctx.quadraticCurveTo(84, 60, 90, 64); fillStroke(ctx, null, 2.5);
    },
    turtle(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.65)), s = rgb(shade(col, 0.5)), l = rgb(tint(col, 0.4));
      // flippers
      ctx.beginPath(); ctx.ellipse(26, 74, 14, 7, 0.4, 0, 7); fillStroke(ctx, c);
      ctx.beginPath(); ctx.ellipse(66, 76, 14, 7, -0.3, 0, 7); fillStroke(ctx, c);
      ctx.beginPath(); ctx.ellipse(20, 58, 10, 6, -0.6, 0, 7); fillStroke(ctx, c);
      // shell
      ctx.beginPath(); ctx.ellipse(46, 54, 36, 24, 0, Math.PI, 0); ctx.lineTo(82, 60); ctx.lineTo(10, 60); ctx.closePath(); fillStroke(ctx, s);
      ctx.save(); ctx.beginPath(); ctx.ellipse(46, 54, 36, 24, 0, Math.PI, 0); ctx.clip();
      [[30, 44], [48, 36], [64, 46], [46, 52]].forEach(p => { ctx.beginPath(); ctx.ellipse(p[0], p[1], 9, 7, 0, 0, 7); fillStroke(ctx, d, 2); });
      ctx.restore();
      // head
      ctx.beginPath(); ctx.ellipse(84, 50, 14, 11, 0, 0, 7); fillStroke(ctx, c);
      ctx.fillStyle = l; ctx.beginPath(); ctx.ellipse(86, 55, 9, 4, 0, 0, 7); ctx.fill();
      eye(ctx, 88, 46, 5, o.blink, 0.3, 0);
      // squint lines (near-sighted)
      ctx.beginPath(); ctx.moveTo(80, 40); ctx.lineTo(84, 42); fillStroke(ctx, null, 2);
      mouth(ctx, 92, 54, 8, o.talking, o.t);
    },
    clam(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.75)), l = rgb(tint(col, 0.5));
      const open = o.talking ? 10 + Math.sin(o.t * 12) * 4 : 6;
      // bottom shell
      ctx.beginPath(); ctx.moveTo(10, 62); ctx.quadraticCurveTo(50, 96, 90, 62); ctx.closePath(); fillStroke(ctx, d);
      // pearl-ish inner glow / tongue
      ctx.fillStyle = "#ffd6e0"; ctx.beginPath(); ctx.ellipse(50, 60, 30, 5, 0, 0, 7); ctx.fill();
      // top shell (hinged at back)
      ctx.save(); ctx.translate(10, 62); ctx.rotate(-open * Math.PI / 180); ctx.translate(-10, -62);
      ctx.beginPath(); ctx.moveTo(10, 62); ctx.quadraticCurveTo(50, 20, 90, 62); ctx.closePath(); fillStroke(ctx, c);
      ctx.strokeStyle = l; ctx.lineWidth = 2.5; for (let i = 1; i < 6; i++) { ctx.beginPath(); ctx.moveTo(10, 62); ctx.quadraticCurveTo(30 + i * 7, 40 - (i % 2) * 6, 18 + i * 13, 56 - Math.sin(i) * 10); ctx.stroke(); }
      // captain's hat
      ctx.beginPath(); ctx.moveTo(34, 36); ctx.lineTo(42, 18); ctx.lineTo(70, 18); ctx.lineTo(74, 36); ctx.closePath(); fillStroke(ctx, "#2b3a6b");
      ctx.beginPath(); ctx.rect(28, 34, 50, 7); fillStroke(ctx, "#2b3a6b");
      ctx.fillStyle = "#ffd75e"; ctx.beginPath(); ctx.arc(55, 27, 4, 0, 7); ctx.fill();
      ctx.restore();
      eye(ctx, 62, 56, 6, o.blink, 0.3, -0.2); eye(ctx, 42, 56, 6, o.blink, 0.3, -0.2);
      // moustache
      ctx.beginPath(); ctx.moveTo(40, 64); ctx.quadraticCurveTo(50, 58, 60, 64); fillStroke(ctx, null, 3);
    },
    whale(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.72)), l = rgb(tint(col, 0.5));
      // tail (left) and body
      path(ctx, [[14, 50], [0, 34], [6, 50], [0, 66]]); fillStroke(ctx, d);
      ctx.beginPath(); ctx.moveTo(12, 50); ctx.bezierCurveTo(16, 18, 70, 14, 92, 42); ctx.bezierCurveTo(100, 54, 92, 76, 70, 78);
      ctx.bezierCurveTo(44, 82, 20, 72, 12, 50); ctx.closePath(); fillStroke(ctx, c);
      // belly grooves
      ctx.save(); ctx.beginPath(); ctx.moveTo(12, 50); ctx.bezierCurveTo(16, 18, 70, 14, 92, 42); ctx.bezierCurveTo(100, 54, 92, 76, 70, 78); ctx.bezierCurveTo(44, 82, 20, 72, 12, 50); ctx.clip();
      ctx.fillStyle = l; ctx.beginPath(); ctx.ellipse(60, 74, 40, 14, 0, 0, 7); ctx.fill();
      ctx.strokeStyle = rgb(shade(col, 0.85)); ctx.lineWidth = 1.5; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(30, 66 + i * 3); ctx.lineTo(90, 62 + i * 3); ctx.stroke(); }
      // a few barnacles on the back
      [[34, 30], [46, 24], [40, 40]].forEach(p => { circle(ctx, p[0], p[1], 3, "#cfd6e6", 1.5); });
      ctx.restore();
      ctx.beginPath(); ctx.ellipse(44, 64, 12, 6, 0.3, 0, 7); fillStroke(ctx, d);
      // spout
      ctx.strokeStyle = "#bfe8ff"; ctx.lineWidth = 2; [[-6, -10], [0, -14], [6, -10]].forEach(v => { ctx.beginPath(); ctx.moveTo(56, 20); ctx.lineTo(56 + v[0], 20 + v[1]); ctx.stroke(); });
      // big gentle eye + cheek + apologetic brow + smile
      ctx.fillStyle = "rgba(255,140,140,0.3)"; ctx.beginPath(); ctx.arc(84, 58, 5, 0, 7); ctx.fill();
      eye(ctx, 76, 44, 8, o.blink, 0.3, 0.2);
      ctx.beginPath(); ctx.moveTo(66, 32); ctx.quadraticCurveTo(76, 30, 86, 36); fillStroke(ctx, null, 2.5);
      mouth(ctx, 86, 60, 12, o.talking, o.t);
    },
    dolphin(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.72)), l = rgb(tint(col, 0.5));
      path(ctx, [[12, 52], [0, 38], [8, 52], [0, 66]]); fillStroke(ctx, d);
      ctx.beginPath(); ctx.moveTo(10, 52); ctx.bezierCurveTo(20, 26, 70, 22, 84, 46); ctx.lineTo(98, 50); ctx.lineTo(84, 56);
      ctx.bezierCurveTo(70, 76, 24, 74, 10, 52); ctx.closePath(); fillStroke(ctx, c);
      path(ctx, [[46, 30], [52, 10], [66, 30]]); fillStroke(ctx, d);
      ctx.beginPath(); ctx.ellipse(50, 60, 11, 6, 0.5, 0, 7); fillStroke(ctx, d);
      ctx.save(); ctx.beginPath(); ctx.moveTo(10, 52); ctx.bezierCurveTo(20, 26, 70, 22, 84, 46); ctx.lineTo(98, 50); ctx.lineTo(84, 56); ctx.bezierCurveTo(70, 76, 24, 74, 10, 52); ctx.clip();
      ctx.fillStyle = l; ctx.beginPath(); ctx.ellipse(56, 66, 36, 12, 0, 0, 7); ctx.fill(); ctx.restore();
      // headphones
      ctx.beginPath(); ctx.arc(70, 40, 16, Math.PI * 1.05, Math.PI * 1.95); fillStroke(ctx, null, 4);
      circle(ctx, 56, 44, 6, "#ff5a7a", 2.5); circle(ctx, 84, 42, 6, "#ff5a7a", 2.5);
      eye(ctx, 74, 46, 6, o.blink, 0.4, 0);
      ctx.beginPath(); ctx.moveTo(80, 56); ctx.quadraticCurveTo(88, 62, 96, 54); fillStroke(ctx, null, 2.5);
    },
    crab(ctx, col, o) {
      const c = rgb(col), d = rgb(shade(col, 0.7));
      const wig = Math.sin(o.t * 6) * 2;
      // legs
      for (const s of [-1, 1]) for (let i = 0; i < 3; i++) {
        const x0 = 50 + s * 26, y0 = 58 + i * 8;
        ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + s * 14, y0 + 6 + wig * (i % 2 ? 1 : -1)); ctx.lineTo(x0 + s * 18, y0 + 16); fillStroke(ctx, null, 4);
      }
      // claws
      for (const s of [-1, 1]) { ctx.beginPath(); ctx.moveTo(50 + s * 24, 50); ctx.lineTo(50 + s * 38, 36 + wig * s); fillStroke(ctx, null, 4);
        ctx.beginPath(); ctx.ellipse(50 + s * 42, 32 + wig * s, 9, 7, s * 0.5, 0, 7); fillStroke(ctx, c);
        ctx.beginPath(); ctx.moveTo(50 + s * 46, 28 + wig * s); ctx.lineTo(50 + s * 50, 34 + wig * s); fillStroke(ctx, null, 2); }
      ctx.beginPath(); ctx.ellipse(50, 58, 28, 18, 0, 0, 7); fillStroke(ctx, c);
      ctx.fillStyle = d; ctx.beginPath(); ctx.ellipse(50, 66, 20, 7, 0, 0, 7); ctx.fill();
      // eye stalks
      for (const s of [-1, 1]) { ctx.beginPath(); ctx.moveTo(50 + s * 8, 44); ctx.lineTo(50 + s * 10, 32); fillStroke(ctx, null, 3); eye(ctx, 50 + s * 10, 30, 5, o.blink, 0, 0.3); }
      mouth(ctx, 50, 56, 10, o.talking, o.t);
    },
    blob(ctx, col, o) { circle(ctx, 50, 50, 36, rgb(col)); eye(ctx, 62, 44, 6, o.blink, 0.3, 0); mouth(ctx, 64, 60, 10, o.talking, o.t); },
  };

  // ---- painted bitmap assets (optional). Anything listed in image_index.js wins over the vector art.
  const Images = {
    cache: {},
    has(name) { return !!(window.BUA_IMAGES && window.BUA_IMAGES.includes(name)); },
    get(name) {
      if (!this.has(name)) return null;
      if (!this.cache[name]) { const im = new Image(); im.src = "assets/images/" + name; this.cache[name] = im; }
      const im = this.cache[name]; return im.complete && im.naturalWidth ? im : null;
    },
    find(...names) { for (const n of names) if (this.has(n)) return n; return null; },
  };

  // Draw an image to fit inside (x,y,w,h), bottom-aligned, keeping its aspect ratio.
  function fitImage(ctx, im, x, y, w, h, facing) {
    const s = Math.min(w / im.naturalWidth, h / im.naturalHeight), dw = im.naturalWidth * s, dh = im.naturalHeight * s;
    ctx.save(); ctx.translate(x + w / 2, y + h);
    if (facing === "left") ctx.scale(-1, 1);
    ctx.drawImage(im, -dw / 2, -dh, dw, dh); ctx.restore();
  }

  function drawCharacter(ctx, charId, x, y, w, h, o) {
    const ch = C.characters[charId] || { color: [200, 200, 200], shape: "blob" };
    o = o || {}; const t = o.t || 0;
    const base = Images.find(`characters/${charId}.png`, `characters/${charId}.webp`);
    if (base) {
      const talkName = Images.find(`characters/${charId}_talk.png`, `characters/${charId}_talk.webp`);
      const useTalk = o.talking && talkName && Math.floor(t * 7) % 2 === 0;
      const im = Images.get(useTalk ? talkName : base) || Images.get(base);
      if (im) {
        const bob = Math.sin(t * (o.moving ? 10 : 1.6) + B.hash(charId) % 10) * (o.moving ? 4 : 2.5);
        const sway = o.moving ? Math.sin(t * 10) * 0.04 : Math.sin(t * 1.2) * 0.015;
        ctx.save(); ctx.translate(x + w / 2, y + h / 2 + bob); ctx.rotate(sway); ctx.translate(-(x + w / 2), -(y + h / 2 + bob));
        // painted sprites face RIGHT in their files, like the vector ones
        fitImage(ctx, im, x, y, w, h, o.facing);
        ctx.restore(); return;
      }
    }
    const blink = ((Math.floor(t * 2 + B.hash(charId) % 7) % 11) === 0) && (t * 2 % 1) < 0.25;
    const bob = Math.sin(t * (o.moving ? 10 : 1.6) + B.hash(charId) % 10) * (o.moving ? 4 : 2.5);
    ctx.save();
    ctx.translate(x + w / 2, y + h / 2 + bob);
    if (o.facing === "left") ctx.scale(-1, 1);
    ctx.scale(w / 100, h / 100);
    ctx.translate(-50, -50);
    ctx.lineWidth = 3;
    (CHARS[ch.shape] || CHARS.blob)(ctx, ch.color, { talking: !!o.talking, blink, t });
    ctx.restore();
  }

  function drawPortrait(ctx, charId, x, y, size) {
    const ch = C.characters[charId] || { color: [200, 200, 200] };
    ctx.save();
    circle(ctx, x + size / 2, y + size / 2, size / 2, rgb(tint(ch.color, 0.65)), 4);
    ctx.beginPath(); ctx.arc(x + size / 2, y + size / 2, size / 2 - 3, 0, 7); ctx.clip();
    const name = Images.find(`characters/${charId}.png`, `characters/${charId}.webp`);
    const im = name && Images.get(name);
    if (im) { const s = Math.max((size * 0.92) / im.naturalWidth, (size * 0.92) / im.naturalHeight); const dw = im.naturalWidth * s, dh = im.naturalHeight * s; ctx.drawImage(im, x + size / 2 - dw / 2, y + size * 0.54 - dh / 2, dw, dh); }
    else drawCharacter(ctx, charId, x + size * 0.05, y + size * 0.15, size * 0.9, size * 0.75, { t: 1.3 });
    ctx.restore();
  }

  // ---------------------------------------------------------------- items
  const ICONS = {
    gear(ctx) { for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; ctx.beginPath(); ctx.rect(-6, -46, 12, 14); ctx.save(); ctx.rotate(a); ctx.fillStyle = "#c9a24a"; ctx.fillRect(-7, -44, 14, 16); ctx.strokeRect(-7, -44, 14, 16); ctx.restore(); }
      circle(ctx, 0, 0, 34, "#e3bd5f"); circle(ctx, 0, 0, 12, "#7a5a1a"); },
    bubble_helmet(ctx) { circle(ctx, 0, 0, 40, "rgba(170,225,255,0.85)"); ctx.fillStyle = "rgba(255,255,255,0.8)"; ctx.beginPath(); ctx.ellipse(-14, -16, 10, 6, -0.7, 0, 7); ctx.fill(); ctx.beginPath(); ctx.rect(-26, 26, 52, 14); fillStroke(ctx, "#8fb7d9"); },
    glasses(ctx) { circle(ctx, -20, 0, 18, "rgba(255,210,230,0.7)"); circle(ctx, 20, 0, 18, "rgba(255,210,230,0.7)"); ctx.beginPath(); ctx.moveTo(-2, 0); ctx.lineTo(2, 0); fillStroke(ctx, null, 4); ctx.beginPath(); ctx.moveTo(-38, -4); ctx.lineTo(-46, -12); ctx.moveTo(38, -4); ctx.lineTo(46, -12); fillStroke(ctx, null, 4); },
    shell_polish(ctx) { ctx.beginPath(); B.roundRect(ctx, -22, -18, 44, 56, 10); fillStroke(ctx, "#ffd84d"); ctx.beginPath(); ctx.rect(-12, -40, 24, 22); fillStroke(ctx, "#ff8d5a"); ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.ellipse(-8, 4, 6, 14, 0, 0, 7); ctx.fill(); },
    ship_key(ctx) { circle(ctx, -18, -14, 18, "#d8b04a"); circle(ctx, -18, -14, 7, "#7a5a1a"); ctx.beginPath(); ctx.moveTo(-6, -2); ctx.lineTo(34, 34); ctx.lineTo(26, 42); ctx.lineTo(-14, 6); ctx.closePath(); fillStroke(ctx, "#d8b04a"); ctx.beginPath(); ctx.rect(14, 26, 8, 12); fillStroke(ctx, "#d8b04a", 2); },
    lantern(ctx) { ctx.beginPath(); ctx.rect(-18, -40, 36, 8); fillStroke(ctx, "#6b5030"); ctx.beginPath(); ctx.rect(-22, -32, 44, 52); fillStroke(ctx, "rgba(255,225,150,0.9)"); ctx.fillStyle = "#ffb84a"; ctx.beginPath(); ctx.ellipse(0, -4, 10, 16, 0, 0, 7); ctx.fill(); ctx.beginPath(); ctx.rect(-22, 20, 44, 10); fillStroke(ctx, "#6b5030"); ctx.beginPath(); ctx.arc(0, -40, 10, Math.PI, 0); fillStroke(ctx, null, 3); },
    crowbar(ctx) { ctx.beginPath(); ctx.moveTo(-34, 36); ctx.lineTo(24, -24); ctx.quadraticCurveTo(40, -40, 24, -40); ctx.lineTo(14, -34); ctx.quadraticCurveTo(26, -32, 16, -18); ctx.lineTo(-26, 42); ctx.closePath(); fillStroke(ctx, "#8a93a8"); },
    pearl(ctx) { circle(ctx, 0, 0, 34, "#f4f1ff"); ctx.fillStyle = "rgba(200,220,255,0.6)"; ctx.beginPath(); ctx.arc(8, 10, 22, 0, 7); ctx.fill(); ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.ellipse(-12, -12, 9, 6, -0.7, 0, 7); ctx.fill(); },
    recipe_page(ctx) { ctx.beginPath(); ctx.moveTo(-28, -36); ctx.lineTo(28, -32); ctx.lineTo(24, 38); ctx.lineTo(-30, 34); ctx.closePath(); fillStroke(ctx, "#fff7dc"); ctx.strokeStyle = "#8a7a5a"; ctx.lineWidth = 2; for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(-18, -18 + i * 13); ctx.lineTo(14, -16 + i * 13); ctx.stroke(); } },
    cookie(ctx) { circle(ctx, 0, 0, 36, "#c98a4b"); ctx.fillStyle = "#5a8a3a"; [[-12, -10], [10, -14], [4, 10], [-14, 14], [16, 8]].forEach(p => { ctx.beginPath(); ctx.arc(p[0], p[1], 5, 0, 7); ctx.fill(); }); },
    dance_shoes(ctx) { for (const s of [-1, 1]) { ctx.beginPath(); ctx.moveTo(s * 4, -20); ctx.lineTo(s * 36, 10); ctx.lineTo(s * 30, 26); ctx.lineTo(s * 4, 18); ctx.closePath(); fillStroke(ctx, "#ff6fc8"); } ctx.fillStyle = "#fff"; [[-20, 2], [22, 0], [-10, 14], [30, 14]].forEach(p => { ctx.beginPath(); ctx.arc(p[0], p[1], 2.5, 0, 7); ctx.fill(); }); },
    conch_shell(ctx) { ctx.beginPath(); ctx.moveTo(-40, 10); ctx.bezierCurveTo(-30, -40, 40, -40, 40, 0); ctx.bezierCurveTo(40, 30, 0, 40, -40, 10); ctx.closePath(); fillStroke(ctx, "#ffc7b0"); ctx.beginPath(); ctx.moveTo(-30, 10); ctx.quadraticCurveTo(0, 0, 28, 6); fillStroke(ctx, null, 2.5); ctx.beginPath(); ctx.moveTo(-10, -26); ctx.quadraticCurveTo(10, -10, 4, 18); fillStroke(ctx, null, 2.5); ctx.fillStyle = "#ff8fa8"; ctx.beginPath(); ctx.ellipse(-10, 16, 18, 7, 0.3, 0, 7); ctx.fill(); },
  };
  function drawIcon(ctx, itemId, x, y, size) {
    ctx.save(); ctx.translate(x + size / 2, y + size / 2); ctx.scale(size / 100, size / 100); ctx.lineWidth = 3; ctx.strokeStyle = OUT; ctx.lineJoin = "round";
    (ICONS[itemId] || (c => circle(c, 0, 0, 36, "#ddd")))(ctx); ctx.restore();
  }

  // ---------------------------------------------------------------- props
  // Drawn in the hotspot's own rect (0,0,w,h). Keyed by hotspot id.
  function sign(ctx, w, h, label, color) {
    ctx.beginPath(); B.roundRect(ctx, 4, 4, w - 8, h - 8, 14); fillStroke(ctx, color || "rgba(255,255,255,0.35)", 3);
    if (label) B.text(ctx, label, w / 2, h / 2 - 11, { size: 20, weight: 600, align: "center", color: "#fff", stroke: OUT, strokeWidth: 4 });
  }
  function exitSign(ctx, w, h, hs) {
    const dir = hs.rect[0] < 200 ? -1 : hs.rect[0] > 1000 ? 1 : 0;
    // post
    ctx.beginPath(); ctx.rect(w / 2 - 6, h * 0.35, 12, h * 0.65); fillStroke(ctx, "#8b5a2b");
    // arrow board
    const bw = Math.min(w - 10, 150), bh = 44, bx = w / 2 - bw / 2, by = h * 0.3;
    ctx.beginPath();
    if (dir >= 0) { ctx.moveTo(bx, by); ctx.lineTo(bx + bw - 18, by); ctx.lineTo(bx + bw, by + bh / 2); ctx.lineTo(bx + bw - 18, by + bh); ctx.lineTo(bx, by + bh); }
    else { ctx.moveTo(bx + 18, by); ctx.lineTo(bx + bw, by); ctx.lineTo(bx + bw, by + bh); ctx.lineTo(bx + 18, by + bh); ctx.lineTo(bx, by + bh / 2); }
    ctx.closePath(); fillStroke(ctx, "#f4c76a");
    B.text(ctx, hs.label || "", w / 2 + (dir >= 0 ? -6 : 6), by + 10, { size: 18, weight: 600, align: "center", color: "#3a2a10" });
  }
  const PROPS = {
    to_festival(ctx, w, h) {
      ctx.beginPath(); ctx.moveTo(10, h); ctx.lineTo(10, 50); ctx.quadraticCurveTo(w / 2, -20, w - 10, 50); ctx.lineTo(w - 10, h); ctx.lineTo(w - 40, h); ctx.lineTo(w - 40, 60); ctx.quadraticCurveTo(w / 2, 14, 40, 60); ctx.lineTo(40, h); ctx.closePath(); fillStroke(ctx, "#ff9ab8");
      for (let i = 0; i < 7; i++) { const x = 30 + i * (w - 60) / 6; ctx.beginPath(); ctx.moveTo(x, 44 - Math.sin(i / 6 * Math.PI) * 24); ctx.lineTo(x + 10, 66 - Math.sin(i / 6 * Math.PI) * 24); ctx.lineTo(x - 10, 66 - Math.sin(i / 6 * Math.PI) * 24); ctx.closePath(); fillStroke(ctx, ["#ffd84d", "#6fd1ff", "#8dff9a"][i % 3], 2); }
      ctx.beginPath(); B.roundRect(ctx, w / 2 - 70, 70, 140, 34, 10); fillStroke(ctx, "#fff5d6");
      B.text(ctx, "FESTIVAL", w / 2, 76, { size: 20, weight: 700, align: "center", color: "#b84c6a" });
    },
    sandcastle(ctx, w, h) {
      const c = "#f1d9a6";
      ctx.beginPath(); ctx.rect(10, h * 0.45, w - 20, h * 0.55); fillStroke(ctx, c);
      [[18, 0.1], [w / 2 - 12, -0.05], [w - 42, 0.1]].forEach(t => { ctx.beginPath(); ctx.rect(t[0], h * (0.2 + t[1]), 24, h * 0.3); fillStroke(ctx, c); for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.rect(t[0] + i * 9, h * (0.12 + t[1]), 6, 7); fillStroke(ctx, c, 2); } });
      ctx.beginPath(); ctx.moveTo(w / 2, h * 0.15); ctx.lineTo(w / 2, -2); ctx.lineTo(w / 2 + 16, 4); ctx.lineTo(w / 2, 10); fillStroke(ctx, "#ff5a5a", 2);
      ctx.beginPath(); ctx.arc(w / 2, h * 0.8, 10, Math.PI, 0); fillStroke(ctx, "#6b4a2b", 2);
    },
    anemone(ctx, w, h, t) {
      for (let i = 0; i < 9; i++) { const x = 10 + i * (w - 20) / 8, s = Math.sin(t * 2 + i) * 6; ctx.beginPath(); ctx.moveTo(x, h); ctx.quadraticCurveTo(x + s, h * 0.5, x + s * 1.5, h * 0.12); fillStroke(ctx, null, 7); ctx.strokeStyle = "#ff8fb0"; ctx.lineWidth = 4; ctx.stroke(); circle(ctx, x + s * 1.5, h * 0.12, 5, "#ffd1e0", 2); }
    },
    starfish(ctx, w, h, t) {
      ctx.save(); ctx.translate(w / 2, h / 2); ctx.rotate(Math.sin(t) * 0.1); ctx.beginPath();
      for (let i = 0; i < 10; i++) { const r = i % 2 ? w * 0.2 : w * 0.48, a = i * Math.PI / 5 - Math.PI / 2; ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); }
      ctx.closePath(); fillStroke(ctx, "#ff9a4a"); ctx.fillStyle = "#ffd08a"; for (let i = 0; i < 5; i++) { const a = i * Math.PI * 2 / 5 - Math.PI / 2; ctx.beginPath(); ctx.arc(Math.cos(a) * w * 0.26, Math.sin(a) * w * 0.26, 3, 0, 7); ctx.fill(); }
      eye(ctx, -6, -4, 4, false, 0.3, 0); eye(ctx, 6, -4, 4, false, 0.3, 0); ctx.restore();
    },
    chatty_clam(ctx, w, h, t) { ctx.save(); ctx.translate(0, 0); ctx.scale(w / 100, h / 100 * 1.4); ctx.translate(0, -20); CHARS.clam(ctx, [210, 200, 230], { talking: false, t }); ctx.restore(); },
    bubble_machine(ctx, w, h, t) {
      ctx.beginPath(); B.roundRect(ctx, 10, 40, w - 20, h - 50, 16); fillStroke(ctx, "#9aa4c0");
      ctx.beginPath(); ctx.rect(w / 2 - 20, 8, 40, 36); fillStroke(ctx, "#7c86a3");
      ctx.beginPath(); ctx.arc(w / 2, 8, 22, Math.PI, 0); fillStroke(ctx, "#7c86a3");
      circle(ctx, w / 2, h * 0.5, 26, "#d7e9ff"); circle(ctx, w / 2, h * 0.5, 10, "#5a6a90");
      [[28, h - 40], [w - 28, h - 40]].forEach(p => circle(ctx, p[0], p[1], 9, ["#ff5a5a", "#6fd16f"][p[0] > 50 ? 1 : 0], 2));
      ctx.beginPath(); ctx.rect(24, h * 0.22, w - 48, 14); fillStroke(ctx, "#5a6a90");
      for (let i = 0; i < 3; i++) { const y = -10 - ((t * 40 + i * 30) % 90); circle(ctx, w / 2 + Math.sin(t + i) * 12, y + 10, 6 + i * 2, "rgba(200,235,255,0.7)", 2); }
    },
    snail(ctx, w, h) { ctx.beginPath(); ctx.ellipse(w * 0.35, h * 0.75, w * 0.32, h * 0.22, 0, 0, 7); fillStroke(ctx, "#d9b382"); circle(ctx, w * 0.62, h * 0.48, h * 0.42, "#c47a4a"); ctx.beginPath(); ctx.arc(w * 0.62, h * 0.48, h * 0.22, 0, 5); fillStroke(ctx, null, 2); eye(ctx, w * 0.18, h * 0.4, 4, false, 0, 0); ctx.beginPath(); ctx.moveTo(w * 0.2, h * 0.55); ctx.lineTo(w * 0.18, h * 0.44); fillStroke(ctx, null, 2); },
    old_boot(ctx, w, h) { ctx.beginPath(); ctx.moveTo(14, 4); ctx.lineTo(w * 0.5, 4); ctx.lineTo(w * 0.5, h * 0.55); ctx.lineTo(w - 6, h * 0.7); ctx.lineTo(w - 6, h - 4); ctx.lineTo(8, h - 4); ctx.closePath(); fillStroke(ctx, "#8a5a3a"); ctx.beginPath(); ctx.rect(8, h - 14, w - 14, 10); fillStroke(ctx, "#4a3222"); circle(ctx, w * 0.32, h * 0.5, 7, "#ffd84d", 2); eye(ctx, w * 0.32, h * 0.5, 4, false, 0, 0); },
    sleepy_fish(ctx, w, h, t) { ctx.beginPath(); ctx.moveTo(4, 4); ctx.quadraticCurveTo(w / 2, h + 10, w - 4, 4); fillStroke(ctx, null, 3); ctx.strokeStyle = "#caa36a"; ctx.lineWidth = 2; for (let i = 1; i < 6; i++) { ctx.beginPath(); ctx.moveTo(4 + i * (w - 8) / 6, 4); ctx.lineTo(w / 2 + (i - 3) * 6, h); ctx.stroke(); }
      ctx.save(); ctx.translate(w * 0.2, h * 0.1); ctx.scale(w * 0.6 / 100, h * 0.8 / 100); CHARS.fish(ctx, [150, 190, 240], { blink: true, t }); ctx.restore();
      B.text(ctx, "z", w - 16, -8 - (t * 10 % 16), { size: 16, weight: 700, color: "#fff", stroke: OUT, strokeWidth: 3 }); },
    tickly_kelp(ctx, w, h, t) { for (let k = 0; k < 2; k++) { ctx.beginPath(); ctx.moveTo(w / 2 + k * 10 - 5, h); for (let i = 1; i <= 6; i++) ctx.lineTo(w / 2 + k * 10 - 5 + Math.sin(t * 2 + i + k) * 8, h - i * h / 6); fillStroke(ctx, null, 9); ctx.strokeStyle = "#5ad66f"; ctx.lineWidth = 6; ctx.stroke(); } },
    chest(ctx, w, h) { ctx.beginPath(); B.roundRect(ctx, 6, h * 0.4, w - 12, h * 0.58, 6); fillStroke(ctx, "#8b5a2b"); ctx.beginPath(); ctx.moveTo(6, h * 0.42); ctx.quadraticCurveTo(w / 2, -h * 0.2, w - 6, h * 0.42); ctx.closePath(); fillStroke(ctx, "#a66d35");
      ctx.strokeStyle = "#d8b04a"; ctx.lineWidth = 4; [0.25, 0.75].forEach(f => { ctx.beginPath(); ctx.moveTo(w * f, h * 0.1); ctx.lineTo(w * f, h * 0.96); ctx.stroke(); });
      [["#ff6f6f", 0.32], ["#6fb6ff", 0.5], ["#ffd84d", 0.68]].forEach(s => { ctx.beginPath(); ctx.arc(w * s[1], h * 0.3, 7, Math.PI, 0); fillStroke(ctx, s[0], 2); });
      circle(ctx, w / 2, h * 0.6, 7, "#d8b04a"); },
    chest_open(ctx, w, h) { ctx.beginPath(); B.roundRect(ctx, 6, h * 0.4, w - 12, h * 0.58, 6); fillStroke(ctx, "#8b5a2b"); ctx.beginPath(); ctx.moveTo(6, h * 0.4); ctx.lineTo(10, -h * 0.3); ctx.quadraticCurveTo(w / 2, -h * 0.7, w - 10, -h * 0.3); ctx.lineTo(w - 6, h * 0.4); ctx.closePath(); fillStroke(ctx, "#a66d35"); ctx.fillStyle = "rgba(255,240,170,0.5)"; ctx.beginPath(); ctx.ellipse(w / 2, h * 0.42, w * 0.4, h * 0.1, 0, 0, 7); ctx.fill(); },
    treasure_door(ctx, w, h) { ctx.beginPath(); ctx.moveTo(6, h); ctx.lineTo(6, 50); ctx.quadraticCurveTo(w / 2, -20, w - 6, 50); ctx.lineTo(w - 6, h); ctx.closePath(); fillStroke(ctx, "#7a4a22"); ctx.strokeStyle = "#4a2c12"; ctx.lineWidth = 2; for (let i = 1; i < 4; i++) { ctx.beginPath(); ctx.moveTo(6 + i * (w - 12) / 4, 20 + i % 2 * 10); ctx.lineTo(6 + i * (w - 12) / 4, h); ctx.stroke(); }
      ctx.beginPath(); ctx.rect(10, h * 0.35, w - 20, 10); fillStroke(ctx, "#3a3a4a", 2); ctx.beginPath(); ctx.rect(10, h * 0.7, w - 20, 10); fillStroke(ctx, "#3a3a4a", 2); circle(ctx, w - 26, h * 0.55, 8, "#d8b04a"); ctx.beginPath(); ctx.rect(w - 29, h * 0.55, 6, 12); fillStroke(ctx, "#5a4a1a", 2); },
    treasure_room(ctx, w, h) { ctx.beginPath(); ctx.moveTo(6, h); ctx.lineTo(6, 50); ctx.quadraticCurveTo(w / 2, -20, w - 6, 50); ctx.lineTo(w - 6, h); ctx.closePath(); fillStroke(ctx, "#2a1a10"); ctx.fillStyle = "rgba(255,220,120,0.35)"; ctx.beginPath(); ctx.moveTo(14, h); ctx.lineTo(14, 56); ctx.quadraticCurveTo(w / 2, 0, w - 14, 56); ctx.lineTo(w - 14, h); ctx.fill(); for (let i = 0; i < 12; i++) circle(ctx, 24 + (i * 37) % (w - 48), h - 20 - (i * 23) % 60, 7, "#ffd84d", 2); },
    wheel(ctx, w, h, t) { ctx.save(); ctx.translate(w / 2, h / 2); ctx.rotate(Math.sin(t * 0.5) * 0.2); for (let i = 0; i < 8; i++) { ctx.beginPath(); ctx.moveTo(0, 0); const a = i * Math.PI / 4; ctx.lineTo(Math.cos(a) * w * 0.48, Math.sin(a) * w * 0.48); fillStroke(ctx, null, 7); ctx.strokeStyle = "#a66d35"; ctx.lineWidth = 4; ctx.stroke(); } ctx.beginPath(); ctx.arc(0, 0, w * 0.36, 0, 7); fillStroke(ctx, null, 12); ctx.strokeStyle = "#8b5a2b"; ctx.lineWidth = 8; ctx.stroke(); circle(ctx, 0, 0, 10, "#d8b04a"); ctx.restore(); },
    porthole(ctx, w, h, t) { circle(ctx, w / 2, h / 2, w / 2 - 4, "#9fb3c8", 4); circle(ctx, w / 2, h / 2, w / 2 - 14, "#5fb8e6", 3); ctx.save(); ctx.beginPath(); ctx.arc(w / 2, h / 2, w / 2 - 15, 0, 7); ctx.clip(); ctx.translate(w / 2 + Math.sin(t) * 10, h / 2); ctx.scale(0.4, 0.4); ctx.translate(-50, -50); CHARS.fish(ctx, [255, 200, 90], { t }); ctx.restore(); for (let i = 0; i < 4; i++) circle(ctx, w / 2 + Math.cos(i * Math.PI / 2) * (w / 2 - 9), h / 2 + Math.sin(i * Math.PI / 2) * (w / 2 - 9), 3, "#5a6a80", 1.5); },
    barrel(ctx, w, h) { ctx.beginPath(); ctx.moveTo(8, 6); ctx.quadraticCurveTo(-6, h / 2, 8, h - 6); ctx.lineTo(w - 8, h - 6); ctx.quadraticCurveTo(w + 6, h / 2, w - 8, 6); ctx.closePath(); fillStroke(ctx, "#a66d35"); ctx.strokeStyle = "#3a3a4a"; ctx.lineWidth = 4; [0.22, 0.78].forEach(f => { ctx.beginPath(); ctx.moveTo(4, h * f); ctx.quadraticCurveTo(w / 2, h * f + (f < 0.5 ? -4 : 4), w - 4, h * f); ctx.stroke(); }); B.text(ctx, "PICKLES", w / 2, h / 2 - 8, { size: 13, weight: 700, align: "center", color: "#3a2a10" }); },
    pip(ctx, w, h, t) { ctx.save(); ctx.scale(w / 100, h / 100); CHARS.crab(ctx, [235, 150, 90], { t }); ctx.restore(); },
    stuck_shell(ctx, w, h, t) { ctx.save(); ctx.translate(w / 2, h / 2); ctx.rotate(-0.4 + Math.sin(t * 3) * 0.05); ctx.scale(w / 100, h / 100); drawIcon(ctx, "conch_shell", -50, -50, 100); ctx.restore(); },
    glow_mushrooms(ctx, w, h, t) { [[0.25, 1], [0.55, 0.8], [0.8, 0.6]].forEach((m, i) => { const x = w * m[0], mh = h * m[1], g = 0.6 + 0.4 * Math.sin(t * 2 + i); ctx.fillStyle = `rgba(120,255,220,${g * 0.35})`; ctx.beginPath(); ctx.arc(x, h - mh * 0.7, mh * 0.6, 0, 7); ctx.fill(); ctx.beginPath(); ctx.rect(x - 5, h - mh * 0.6, 10, mh * 0.6); fillStroke(ctx, "#d6f5ff", 2); ctx.beginPath(); ctx.ellipse(x, h - mh * 0.6, mh * 0.42, mh * 0.3, 0, Math.PI, 0); ctx.closePath(); fillStroke(ctx, `rgba(120,255,220,${0.6 + g * 0.4})`, 2.5); }); },
    echo_spot(ctx, w, h) { ctx.beginPath(); ctx.moveTo(w * 0.3, 4); ctx.lineTo(w * 0.55, h * 0.3); ctx.lineTo(w * 0.4, h * 0.55); ctx.lineTo(w * 0.7, h - 4); ctx.lineTo(w * 0.5, h - 4); ctx.lineTo(w * 0.25, h * 0.6); ctx.lineTo(w * 0.42, h * 0.3); ctx.closePath(); fillStroke(ctx, "#05050f"); B.text(ctx, "))", w * 0.72, h * 0.3, { size: 22, weight: 700, color: "#9fe8ff" }); },
    suspicious_rock(ctx, w, h, t) { ctx.beginPath(); ctx.moveTo(6, h - 4); ctx.quadraticCurveTo(0, h * 0.3, w * 0.3, 8); ctx.quadraticCurveTo(w * 0.7, -4, w - 6, h * 0.4); ctx.quadraticCurveTo(w, h, w * 0.6, h - 4); ctx.closePath(); fillStroke(ctx, "#6a6a8a"); if (Math.floor(t) % 5 === 0) { eye(ctx, w * 0.4, h * 0.45, 5, false, 0.3, 0); eye(ctx, w * 0.6, h * 0.45, 5, (t % 1) < 0.3, 0.3, 0); } },
    krill(ctx, w, h, t) { for (let i = 0; i < 9; i++) { const x = (i * 29 + t * 40) % w, y = h / 2 + Math.sin(t * 4 + i) * h * 0.3; ctx.beginPath(); ctx.ellipse(x, y, 7, 3, 0.2, 0, 7); fillStroke(ctx, "#ffb0a0", 1.5); ctx.fillStyle = "#1d2b4a"; ctx.beginPath(); ctx.arc(x + 4, y - 1, 1.2, 0, 7); ctx.fill(); } },
    stage(ctx, w, h) { ctx.beginPath(); ctx.rect(0, 0, w, h); fillStroke(ctx, "#b84c6a"); ctx.fillStyle = "#ffd84d"; for (let i = 0; i < w; i += 40) { ctx.beginPath(); ctx.arc(i + 20, h / 2, 4, 0, 7); ctx.fill(); } },
    dance_floor(ctx, w, h, t) { const cols = ["#ff6fc8", "#6fd1ff", "#ffd84d", "#8dff9a"]; const n = 6, m = 2; for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) { ctx.beginPath(); ctx.rect(i * w / n, j * h / m, w / n, h / m); fillStroke(ctx, cols[(i + j + Math.floor(t * 2)) % 4], 2); } },
    cookie_table(ctx, w, h) { ctx.beginPath(); ctx.rect(4, h * 0.45, w - 8, 12); fillStroke(ctx, "#8b5a2b"); [[16, h * 0.57], [w - 24, h * 0.57]].forEach(p => { ctx.beginPath(); ctx.rect(p[0], p[1], 8, h * 0.43); fillStroke(ctx, "#6b4a2b"); }); for (let i = 0; i < 4; i++) for (let j = 0; j < 3 - (i % 2); j++) drawIcon(ctx, "cookie", 10 + i * 28 + (i % 2) * 6, h * 0.42 - 16 - j * 10, 24); },
    balloon(ctx, w, h, t) { ctx.beginPath(); ctx.moveTo(w / 2, h - 4); ctx.quadraticCurveTo(w / 2 + Math.sin(t * 2) * 6, h * 0.8, w / 2, h * 0.68); fillStroke(ctx, null, 2); ctx.beginPath(); ctx.ellipse(w / 2, h * 0.36, w * 0.4, h * 0.34, 0, 0, 7); fillStroke(ctx, "#ff5a5a"); ctx.fillStyle = "rgba(255,255,255,0.6)"; ctx.beginPath(); ctx.ellipse(w * 0.36, h * 0.22, 6, 10, -0.5, 0, 7); ctx.fill(); path(ctx, [[w / 2 - 6, h * 0.7], [w / 2 + 6, h * 0.7], [w / 2, h * 0.64]]); fillStroke(ctx, "#ff5a5a", 2); },
    snack_stall(ctx, w, h) { ctx.beginPath(); ctx.rect(8, h * 0.45, w - 16, h * 0.55); fillStroke(ctx, "#f4c76a"); ctx.beginPath(); ctx.moveTo(0, h * 0.45); ctx.lineTo(w / 2, 4); ctx.lineTo(w, h * 0.45); ctx.closePath(); fillStroke(ctx, "#ff8fa8"); for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(i * w / 5, h * 0.45); ctx.lineTo(i * w / 5 + w / 10, h * 0.52); ctx.lineTo((i + 1) * w / 5, h * 0.45); fillStroke(ctx, i % 2 ? "#fff" : "#ff8fa8", 2); } B.text(ctx, "SNACKS", w / 2, h * 0.6, { size: 20, weight: 700, align: "center", color: "#7a3a1a" }); drawIcon(ctx, "cookie", w * 0.2, h * 0.75, 20); drawIcon(ctx, "cookie", w * 0.6, h * 0.75, 20); },
    speakers(ctx, w, h, t) { ctx.beginPath(); B.roundRect(ctx, 6, 6, w - 12, h - 12, 10); fillStroke(ctx, "#3a3a4a"); const p = 1 + Math.sin(t * 8) * 0.06; [0.32, 0.72].forEach(f => { circle(ctx, w / 2, h * f, w * 0.3 * p, "#1f1f2a", 3); circle(ctx, w / 2, h * f, w * 0.12, "#8a8aa0", 2); }); },
    confetti_cannon(ctx, w, h) { ctx.beginPath(); ctx.moveTo(10, h - 6); ctx.lineTo(w * 0.7, h * 0.2); ctx.lineTo(w * 0.85, h * 0.4); ctx.lineTo(w * 0.3, h - 6); ctx.closePath(); fillStroke(ctx, "#6fd1ff"); ctx.beginPath(); ctx.rect(4, h - 14, w * 0.4, 10); fillStroke(ctx, "#3a3a4a"); ["#ff6fc8", "#ffd84d", "#8dff9a"].forEach((c, i) => { ctx.fillStyle = c; ctx.fillRect(w * 0.8 + i * 6, h * 0.1 - i * 8, 6, 9); }); },
  };
  function drawProp(ctx, scene, hs, t) {
    const [x, y, w, h] = hs.rect;
    ctx.save(); ctx.translate(x, y); ctx.lineWidth = 3; ctx.strokeStyle = OUT; ctx.lineJoin = "round";
    const fn = PROPS[hs.id];
    if (fn) fn(ctx, w, h, t, hs);
    else if (hs.type === "exit") exitSign(ctx, w, h, hs);
    else sign(ctx, w, h, hs.label, hs.color ? rgb(hs.color, 0.8) : null);
    ctx.restore();
  }

  // ---------------------------------------------------------------- backgrounds
  function paintBackground(scene) {
    const cv = document.createElement("canvas"); cv.width = B.W; cv.height = B.PLAY_H;
    const ctx = cv.getContext("2d"); const R = B.seeded(scene.id);
    const painted = Images.find(`backgrounds/${scene.id}.jpg`, `backgrounds/${scene.id}.png`, `backgrounds/${scene.id}.webp`);
    if (painted) {
      // draw once the image is ready; until then the procedural background shows
      const im = new Image(); im.onload = () => { const s = Math.max(B.W / im.naturalWidth, B.PLAY_H / im.naturalHeight); const dw = im.naturalWidth * s, dh = im.naturalHeight * s; ctx.clearRect(0, 0, B.W, B.PLAY_H); ctx.drawImage(im, (B.W - dw) / 2, (B.PLAY_H - dh) / 2, dw, dh); };
      im.src = "assets/images/" + painted;
    }
    const pal = scene.palette || {}; const top = pal.top || [40, 150, 210], bottom = pal.bottom || [10, 70, 130], floor = pal.floor || [230, 200, 150];
    const floorY = scene.floor_y || 400, style = scene.style || "reef";
    ctx.fillStyle = grad(ctx, 0, 0, 0, B.PLAY_H, [[0, rgb(top)], [1, rgb(bottom)]]); ctx.fillRect(0, 0, B.W, B.PLAY_H);
    // light rays
    for (let i = 0; i < 7; i++) { const x = R() * B.W; ctx.fillStyle = "rgba(255,255,255,0.07)"; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + 70, 0); ctx.lineTo(x + 260, B.PLAY_H); ctx.lineTo(x + 60, B.PLAY_H); ctx.fill(); }
    // far silhouettes
    ctx.fillStyle = rgb(shade(bottom, 1.25), 0.5);
    for (let i = 0; i < 10; i++) { const x = R() * B.W, r = 40 + R() * 90; ctx.beginPath(); ctx.ellipse(x, floorY + 20, r, r * 0.9, 0, Math.PI, 0); ctx.fill(); }
    if (style === "kelp") for (let i = 0; i < 14; i++) { const x = R() * B.W; ctx.strokeStyle = rgb([40 + R() * 30, 120 + R() * 60, 70], 0.6); ctx.lineWidth = 10 + R() * 10; ctx.beginPath(); ctx.moveTo(x, floorY + 30); for (let k = 1; k < 8; k++) ctx.lineTo(x + Math.sin(k + i) * 20, floorY + 30 - k * 70); ctx.stroke(); }
    if (style === "ship") {
      ctx.fillStyle = "#4a2f1a"; ctx.beginPath(); ctx.moveTo(140, floorY + 40); ctx.quadraticCurveTo(120, 120, 300, 80); ctx.lineTo(1000, 80); ctx.quadraticCurveTo(1180, 100, 1160, floorY + 40); ctx.closePath(); ctx.fill(); ctx.strokeStyle = OUT; ctx.lineWidth = 4; ctx.stroke();
      ctx.strokeStyle = "rgba(0,0,0,0.25)"; ctx.lineWidth = 3; for (let y = 120; y < floorY + 30; y += 36) { ctx.beginPath(); ctx.moveTo(150, y); ctx.lineTo(1150, y); ctx.stroke(); }
      ctx.fillStyle = "#6b4a2b"; ctx.fillRect(620, 0, 24, 100); ctx.strokeRect(620, 0, 24, 100);
    }
    if (style === "cave") { ctx.fillStyle = "#0a0f2a"; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 300); ctx.quadraticCurveTo(120, 220, 160, 0); ctx.fill(); ctx.beginPath(); ctx.moveTo(B.W, 0); ctx.lineTo(B.W, 340); ctx.quadraticCurveTo(1140, 240, 1100, 0); ctx.fill(); for (let i = 0; i < 9; i++) { const x = 200 + i * 110; ctx.beginPath(); ctx.moveTo(x - 30, 0); ctx.lineTo(x, 60 + R() * 80); ctx.lineTo(x + 30, 0); ctx.fill(); } }
    if (style === "festival") { for (let i = 0; i < 26; i++) { const x = i * 52; ctx.beginPath(); ctx.moveTo(x, 50 + Math.sin(i * 0.5) * 20); ctx.lineTo(x + 26, 50 + Math.sin(i * 0.5) * 20); ctx.lineTo(x + 13, 84 + Math.sin(i * 0.5) * 20); ctx.closePath(); fillStroke(ctx, ["#ff6fc8", "#6fd1ff", "#ffd84d", "#8dff9a"][i % 4], 2); } for (let i = 0; i < 14; i++) circle(ctx, 40 + i * 92, 120 + (i % 2) * 14, 7, "#fff3b0", 2); }
    // floor
    ctx.fillStyle = rgb(floor); ctx.beginPath(); ctx.moveTo(0, B.PLAY_H); ctx.lineTo(0, floorY + 30);
    for (let x = 0; x <= B.W + 80; x += 80) ctx.quadraticCurveTo(x + 40, floorY + (R() * 30 - 15), x + 80, floorY + 10 + (R() * 20 - 10));
    ctx.lineTo(B.W, B.PLAY_H); ctx.closePath(); ctx.fill(); ctx.strokeStyle = OUT; ctx.lineWidth = 4; ctx.stroke();
    ctx.fillStyle = rgb(tint(floor, 0.3), 0.5); for (let i = 0; i < 30; i++) { ctx.beginPath(); ctx.ellipse(R() * B.W, floorY + 60 + R() * 180, 14 + R() * 30, 4 + R() * 6, 0, 0, 7); ctx.fill(); }
    // corals / rocks near floor
    if (style === "reef") for (let i = 0; i < 16; i++) { const x = R() * B.W, y = floorY + 10 + R() * 200, r = 14 + R() * 30, col = [[255, 120, 160], [255, 150, 80], [200, 120, 230], [255, 200, 90]][Math.floor(R() * 4)];
      ctx.beginPath(); ctx.arc(x, y, r, Math.PI, 0); ctx.closePath(); fillStroke(ctx, rgb(col)); ctx.fillStyle = rgb(tint(col, 0.5)); for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.arc(x - r * 0.6 + k * r * 0.4, y - r * 0.5, 3, 0, 7); ctx.fill(); } }
    if (style === "cave") for (let i = 0; i < 12; i++) { const x = R() * B.W, y = floorY + 20 + R() * 200, r = 20 + R() * 40; ctx.beginPath(); ctx.ellipse(x, y, r, r * 0.6, 0, 0, 7); fillStroke(ctx, "#1a1a3a"); }
    if (style === "ship") for (let i = 0; i < 10; i++) { const x = R() * B.W, y = floorY + 40 + R() * 180; ctx.beginPath(); ctx.rect(x, y, 40 + R() * 90, 12); fillStroke(ctx, "#5a3a20", 2); }
    return cv;
  }

  // ---------------------------------------------------------------- cursors
  function drawCursor(ctx, kind, x, y, iconId) {
    ctx.save(); ctx.translate(x, y); ctx.lineWidth = 3; ctx.strokeStyle = OUT; ctx.lineJoin = "round";
    if (kind === "item" && iconId) { drawIcon(ctx, iconId, -22, -22, 44); ctx.restore(); return; }
    switch (kind) {
      case "hand": ctx.beginPath(); B.roundRect(ctx, -10, -2, 22, 20, 7); fillStroke(ctx, "#fff"); for (let i = 0; i < 4; i++) { ctx.beginPath(); B.roundRect(ctx, -9 + i * 6, -16 + (i ? 0 : 6), 5, 16, 2.5); fillStroke(ctx, "#fff", 2); } break;
      case "eye": ctx.beginPath(); ctx.moveTo(-18, 0); ctx.quadraticCurveTo(0, -16, 18, 0); ctx.quadraticCurveTo(0, 16, -18, 0); fillStroke(ctx, "#fff"); circle(ctx, 0, 0, 6, "#4a9ee0", 2); circle(ctx, 0, 0, 2.5, OUT, 1); break;
      case "talk": ctx.beginPath(); ctx.ellipse(6, -10, 18, 12, 0, 0, 7); fillStroke(ctx, "#fff"); path(ctx, [[-4, -2], [-8, 10], [4, 1]]); fillStroke(ctx, "#fff", 2); ctx.fillStyle = OUT; [-2, 6, 14].forEach(dx => { ctx.beginPath(); ctx.arc(dx, -10, 2, 0, 7); ctx.fill(); }); break;
      case "exit": path(ctx, [[-16, -6], [4, -6], [4, -14], [18, 0], [4, 14], [4, 6], [-16, 6]]); fillStroke(ctx, "#8dff9a"); break;
      default: path(ctx, [[0, 0], [0, 24], [7, 18], [12, 28], [17, 26], [12, 16], [22, 16]]); fillStroke(ctx, "#fff");
    }
    ctx.restore();
  }

  B.Art = { OUT, Images, fitImage, drawCharacter, drawPortrait, drawIcon, drawProp, paintBackground, drawCursor, ellipse, circle, fillStroke, path, eye };
})(window.BUA);

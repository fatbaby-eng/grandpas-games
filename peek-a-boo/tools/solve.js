// Drives every level of index.html to its celebration in headless Chromium and reports page errors.
// Usage: node tools/solve.js /abs/path/to/index.html /abs/path/to/screenshot-dir   (needs: npm i playwright)
const { chromium } = require('playwright');
const fs = require('fs');
const file = process.argv[2], out = process.argv[3]; fs.mkdirSync(out, { recursive: true });
const BANDS = { 1: ["discovery","explorer","hideaway","sayhi"], 2: ["detective","safari","matchme","dressup"], 3: ["biglittle","colors","memory","shadow","different","counting"], 4: ["howmany","pattern","letters","sort"] };
async function box(page, sel) { const el = await page.$(sel); if (!el) throw new Error('missing ' + sel); const b = await el.boundingBox(); if (!b) throw new Error('nobox ' + sel); return b; }
async function clickSel(page, sel) { const b = await box(page, sel); await page.mouse.click(b.x + b.width/2, b.y + b.height/2); }
async function holdGear(page) { const all = await page.$$('button'); for (const b of all) { const bb = await b.boundingBox(); if (bb && bb.width < 60 && bb.height < 60 && bb.y < 80) { await page.mouse.move(bb.x+bb.width/2, bb.y+bb.height/2); await page.mouse.down(); await page.waitForTimeout(1450); await page.mouse.up(); await page.waitForTimeout(350); return; } } throw new Error('no gear'); }
async function state(page) { return page.evaluate(() => { const p = window.__peek; return { round: p.round, revealed: Array.from(p.revealed), screen: p.screen, band: p.band, streak: p.streak, previewing: p.previewing, locked: p.locked }; }); }
async function tap(page, i) { await clickSel(page, `[data-card="${i}"]`); await page.waitForTimeout(260); }
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error' && !/ERR_FAILED/.test(m.text())) errs.push(m.text()); });
  await page.route('**/fonts.googleapis.com/**', r => r.abort());
  await page.goto('file://' + file + '#debug'); await page.waitForTimeout(500);
  await page.mouse.click(195, 500); await page.waitForTimeout(700); // welcome -> round 1
  let acceptedOnce = false; const results = [];
  for (const band of [1,2,3,4]) {
    await holdGear(page); await clickSel(page, `[data-band="${band}"]`); await page.waitForTimeout(700);
    for (const lvl of BANDS[band]) {
      if (!(await page.$('[data-level]'))) await holdGear(page); await clickSel(page, `[data-level="${lvl}"]`); await page.waitForTimeout(800);
      let st = await state(page);
      if (st.round.level !== lvl) throw new Error('level not started: ' + lvl + ' got ' + st.round.level);
      if (st.previewing) { await page.screenshot({ path: `${out}/${band}-${lvl}-0-preview.png` }); await page.waitForTimeout(2600); st = await state(page); }
      await page.screenshot({ path: `${out}/${band}-${lvl}-1-start.png` });
      const r = st.round; const cards = r.cards;
      if (["discovery","explorer","dressup","counting","sayhi"].includes(lvl)) {
        const idx = cards.map((c,i)=>i).filter(i => !cards[i].isEmpty || lvl === 'explorer');
        for (let k = 0; k < idx.length; k++) { await tap(page, idx[k]); if (k === 1) await page.screenshot({ path: `${out}/${band}-${lvl}-2-mid.png` }); }
      } else if (lvl === 'memory') {
        const byId = {}; cards.forEach((c,i) => { (byId[c.animal.id] = byId[c.animal.id] || []).push(i); });
        // one deliberate miss first
        const ids = Object.keys(byId); await tap(page, byId[ids[0]][0]); await tap(page, byId[ids[1]][0]);
        await page.screenshot({ path: `${out}/${band}-${lvl}-2-mid.png` }); await page.waitForTimeout(1300);
        for (const id of ids) { await tap(page, byId[id][0]); await tap(page, byId[id][1]); await page.waitForTimeout(200); }
      } else if (lvl === 'sort') {
        // first by tap-then-bin, then by dragging
        for (let i = 0; i < cards.length; i++) {
          if (i < 3) { await tap(page, i); await clickSel(page, `[data-bin="${cards[i].bin}"]`); }
          else { const from = await box(page, `[data-card="${i}"]`); const to = await box(page, `[data-bin="${cards[i].bin}"]`);
            await page.mouse.move(from.x+from.width/2, from.y+from.height/2); await page.mouse.down(); await page.mouse.move(from.x+40, from.y, { steps: 4 });
            await page.mouse.move(to.x+to.width/2, to.y+to.height/2, { steps: 8 }); if (i === 3) await page.screenshot({ path: `${out}/${band}-${lvl}-2-mid.png` }); await page.mouse.up(); }
          await page.waitForTimeout(300);
        }
      } else {
        // one wrong tap, then the answer
        const wrongIdx = cards.findIndex((c,i) => i !== r.answer && !c.isEmpty && lvl !== 'hideaway') ;
        const w = lvl === 'hideaway' ? cards.findIndex((c,i) => i !== r.answer) : wrongIdx;
        if (w >= 0) { await tap(page, w); await page.screenshot({ path: `${out}/${band}-${lvl}-2-mid.png` }); await page.waitForTimeout(400); }
        await tap(page, r.answer);
      }
      await page.waitForTimeout(1600);
      st = await state(page);
      results.push({ band, lvl, screen: st.screen, streak: st.streak });
      if (st.screen !== 'celebration') { await page.screenshot({ path: `${out}/${band}-${lvl}-FAIL.png` }); console.log('FAIL', band, lvl, JSON.stringify(st.revealed)); await page.mouse.click(195, 700); continue; }
      await page.screenshot({ path: `${out}/${band}-${lvl}-3-celebration.png` });
      const accept = await page.$('[data-accept-band]');
      if (accept && !acceptedOnce) { acceptedOnce = true; await clickSel(page, '[data-accept-band]'); await page.waitForTimeout(800); const s2 = await state(page); results.push({ accepted: true, bandNow: s2.band, level: s2.round.level }); await page.screenshot({ path: `${out}/accepted-band.png` }); await holdGear(page); await clickSel(page, `[data-band="${band}"]`); await page.waitForTimeout(700); }
      else { const pa = await page.getByText(/Play Again|Keep playing/).first().boundingBox(); await page.mouse.click(pa.x+pa.width/2, pa.y+pa.height/2); await page.waitForTimeout(700); }
    }
  }
  console.log(JSON.stringify(results)); console.log('errors', JSON.stringify(errs));
  await browser.close();
})().catch(e => { console.error('CRASH', e); process.exit(1); });

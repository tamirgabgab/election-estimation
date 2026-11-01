// Election-night rehearsal of reports/knesset_27_panels.html (Next steps B7).
//
// Replays the base election's per-box committee file in the calculator of the
// default panel, in four cumulative stages (25%, 50%, 75%, 100% of the panel's
// boxes; each stage is a new file with the boxes reported since the last one),
// for two reporting orders: random (seeded), and the Arab-majority sectors last.
// At every stage it records the areas found, the warnings, the bloc seats with
// P(61) and the seats moved against the final (100%) forecast. The base election
// is the model's own base, so this checks the procedure and how the forecast
// settles, not its accuracy (see reports/sector_partial.md for that).
//
// Usage: node scripts/rehearse_election_night.js <ballots raw file> <work dir> <out.json>
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

function mulberry(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

(async () => {
  const [rawFile, workDir, outFile] = process.argv.slice(2);
  fs.mkdirSync(workDir, { recursive: true });
  const text = fs.readFileSync(rawFile, "utf8").replace(/^﻿/, "");
  const lines = text.split(/\r?\n/).filter((l) => l.trim());
  const head = lines[0].split(",").map((c) => c.trim());
  const iS = head.indexOf("סמל ישוב"), iB = head.indexOf("קלפי");
  const byKey = new Map(lines.slice(1).map((l) => { const c = l.split(","); return [c[iS].trim() + "|" + c[iB].trim(), l]; }));

  const file = "file://" + path.resolve(__dirname, "..", "reports", "knesset_27_panels.html");
  const browser = await chromium.launch();
  const out = { stages: [0.25, 0.5, 0.75, 1], scenarios: {} };
  for (const scenario of ["random", "arab_last"]) {
    const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
    const errors = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.goto(file);
    await page.waitForSelector("#forecast");
    const units = await page.evaluate(() => {
      const bloc = Object.fromEntries(DATA.base_lists.map((l) => [l.letter, l.bloc]));
      const arab = Object.fromEntries(DATA.sectors.map((s) => [s.id,
        Object.entries(s.prev_shares).reduce((a, [l, v]) => a + (bloc[l] === "arab" ? v : 0), 0) > 0.5]));
      return DATA.panels[defaultPanel()].units.map((u) => ({ key: u.recommended[0].settlement_code + "|" + u.recommended[0].ballot, arab: arab[u.sector] }));
    });
    const rng = mulberry(27);
    const order = units.map((u) => [u, rng()]).sort((a, b) => a[1] - b[1]).map((x) => x[0]);
    if (scenario === "arab_last") order.sort((a, b) => a.arab - b.arab);
    const rows = [];
    let done = 0;
    for (let k = 0; k < out.stages.length; k++) {
      const upto = Math.round(out.stages[k] * order.length);
      const part = order.slice(done, upto).map((u) => byKey.get(u.key)).filter(Boolean);
      done = upto;
      const f = path.join(workDir, `${scenario}_stage${k + 1}.csv`);
      fs.writeFileSync(f, [lines[0], ...part].join("\n"));
      await page.setInputFiles("#cec-file", f);
      await page.waitForFunction((n) => document.getElementById("import-msg").textContent.includes(`נטענו ${n} קבצים`), k + 1);
      await page.waitForSelector("#forecast");
      rows.push(await page.evaluate(() => ({
        message: document.getElementById("import-msg").textContent,
        warnings: [...document.querySelectorAll("#result > p.msg")].map((p) => p.textContent),
        seats: Object.fromEntries([...document.querySelectorAll("#forecast tbody tr")].map((r) => [r.dataset.letter, +r.cells[1].textContent])),
        majority: [...document.querySelectorAll("#majority tbody tr")].map((r) => ({ name: r.cells[0].textContent, seats: +r.cells[1].textContent, range: r.cells[2].textContent, p: r.cells[3].textContent })),
      })));
    }
    const final = rows[rows.length - 1].seats;
    rows.forEach((r) => {
      r.moved_vs_final = Object.keys({ ...final, ...r.seats }).reduce((a, l) => a + Math.abs((r.seats[l] || 0) - (final[l] || 0)), 0) / 2;
    });
    out.scenarios[scenario] = { rows, errors, arab_units: units.filter((u) => u.arab).length, units: units.length };
    await page.close();
  }
  await browser.close();
  fs.writeFileSync(outFile, JSON.stringify(out, null, 1));
  console.log("ok");
})();

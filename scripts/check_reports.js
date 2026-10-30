// Open every HTML report in a headless browser, fail on JavaScript errors, check that
// the seats shown add up to the total, and save screenshots for a visual check.
//
// Usage:
//   node scripts/check_reports.js [screenshot_dir]
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const reports = path.resolve(__dirname, "..", "reports");
const outDir = process.argv[2] || fs.mkdtempSync(path.join(require("os").tmpdir(), "reports-"));

(async () => {
  const browser = await chromium.launch();
  let failed = false;
  const files = fs.readdirSync(reports).filter(f => f.endsWith(".html")).sort();
  for (const file of files) {
    for (const [mode, viewport] of [["desktop", { width: 1200, height: 900 }], ["mobile", { width: 390, height: 800 }]]) {
      const page = await browser.newPage({ viewport });
      const errors = [];
      page.on("pageerror", e => errors.push(e.message));
      page.on("console", m => m.type() === "error" && errors.push(m.text()));
      await page.goto("file://" + path.join(reports, file));

      // Seats in the per-list bar chart must add up to the total row of the table.
      const seats = await page.$$eval(".bars .num", els => els.reduce((s, e) => s + Number(e.textContent), 0));
      const total = await page.$eval("tr.total td:last-child", e => Number(e.textContent));
      if (seats !== total) errors.push(`seat bars sum to ${seats}, total is ${total}`);

      if (file === "index.html") {
        await page.click("button[data-view=compare]");
        await page.click("button[data-group=family]");
        await page.click("button[data-metric=share]");
        if (!(await page.$$("#compare-table tbody tr")).length) errors.push("empty comparison table");
      }
      const shot = path.join(outDir, `${path.basename(file, ".html")}_${mode}.png`);
      await page.screenshot({ path: shot, fullPage: true });

      if (file === "index.html") {
        // Party lookup: ballot letters complete to the party; settlement votes add up.
        await page.click("button[data-view=party]");
        await page.fill("#party-q", "מחל");
        const first = await page.textContent("#party-list li");
        if (!first.includes("הליכוד")) errors.push(`lookup "מחל" suggests: ${first.trim()}`);
        await page.press("#party-q", "Enter");
        const runs = (await page.$$("#party-detail table:first-of-type tbody tr")).length;
        if (runs < 2) errors.push(`Likud lookup shows ${runs} elections`);
        if ((await page.$$("#set-table tbody tr")).length < 2) errors.push("empty settlement table");
        await page.click("#set-table th[data-col=name]");
        await page.fill("#set-filter", "ירושלים");
        if ((await page.$$("#set-table tbody tr")).length < 2) errors.push("settlement filter found nothing");
        const bad = await page.evaluate(() => {
          initLookup();
          const out = [];
          for (const e of ENTITIES) {
            const sums = {};
            for (const r of settlementRows(e)) for (const [k, c] of Object.entries(r.cells)) sums[k] = (sums[k] || 0) + c.votes;
            for (const { el, p } of e.runs) {
              const own = e.runs.filter(x => x.el === el).reduce((s, x) => s + x.p.votes, 0);
              if (sums[el.knesset] !== own) out.push(`${e.name} K${el.knesset}: ${sums[el.knesset]} != ${own}`);
            }
          }
          return out;
        });
        if (bad.length) errors.push("settlement sums: " + bad.slice(0, 3).join("; "));
        await page.screenshot({ path: path.join(outDir, `index_party_${mode}.png`), fullPage: true });
      }
      console.log(`${file} [${mode}]: ${errors.length ? "FAIL " + errors.join("; ") : "ok"}`);
      failed ||= errors.length > 0;
      await page.close();
    }
  }
  await browser.close();
  console.log(`screenshots: ${outDir}`);
  process.exit(failed ? 1 : 0);
})();

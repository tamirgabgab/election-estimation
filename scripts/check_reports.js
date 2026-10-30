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
      console.log(`${file} [${mode}]: ${errors.length ? "FAIL " + errors.join("; ") : "ok"}`);
      failed ||= errors.length > 0;
      await page.close();
    }
  }
  await browser.close();
  console.log(`screenshots: ${outDir}`);
  process.exit(failed ? 1 : 0);
})();

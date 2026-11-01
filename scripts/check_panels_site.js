// Checks reports/knesset_27_panels.html in Chromium: no console errors, no
// horizontal page scroll at desktop and phone width, and the calculator's
// example forecast for every panel (printed as JSON for
// scripts/check_panels_site.py to compare with the Python model).
// Screenshots go to <out_dir>.
//
// Usage: node scripts/check_panels_site.js <out_dir> <base election ballots raw file>
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

(async () => {
  const outDir = process.argv[2];
  const rawFile = process.argv[3];
  fs.mkdirSync(outDir, { recursive: true });
  const file = "file://" + path.resolve(__dirname, "..", "reports", "knesset_27_panels.html");
  const browser = await chromium.launch();
  const result = { errors: [], overflow: {}, forecasts: {} };
  for (const [name, width, scheme] of [["desktop", 1200, "light"], ["mobile", 400, "dark"]]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
    page.on("console", (m) => { if (m.type() === "error") result.errors.push(m.text()); });
    page.on("pageerror", (e) => result.errors.push(String(e)));
    await page.goto(file);
    await page.waitForSelector("#result table");
    result.overflow[name] = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    // Full-page capture can fail under load: retry, and report it without failing the check.
    for (let attempt = 0; attempt < 3; attempt++) {
      try { await page.screenshot({ path: path.join(outDir, `panels_${name}.png`), fullPage: true }); break; }
      catch (e) { if (attempt === 2) result.screenshotErrors = (result.screenshotErrors || []).concat(name); else await page.waitForTimeout(2000); }
    }
    if (name === "desktop") {
      const panels = await page.evaluate(() => DATA.panels.length);
      for (let i = 0; i < panels; i++) {
        await page.click(`#compare tr.pick[data-i="${i}"]`);
        await page.waitForSelector("#forecast");
        result.forecasts[i] = await page.evaluate(() => ({
          panel: document.getElementById("h-panel").textContent,
          direct: Object.fromEntries([...document.querySelectorAll("#forecast tbody tr")].map((r) => [r.dataset.letter, +r.dataset.direct])),
          shares: Object.fromEntries([...document.querySelectorAll("#forecast tbody tr")].map((r) => [r.dataset.letter, +r.dataset.share])),
        }));
      }
      // Bloc majorities and the coalition builder.
      const boxes = await page.$$("#coalition input");
      for (const b of boxes.slice(0, 3)) await b.check();
      result.majority = { rows: await page.$$eval("#majority tbody tr", (r) => r.length),
        coalition: await page.$eval("#coalition-out", (e) => e.textContent) };
      // Import the base election's per-box committee file into the default panel:
      // it must give the same forecast as the built-in example.
      const def = await page.evaluate(() => defaultPanel());
      await page.click(`#compare tr.pick[data-i="${def}"]`);
      await page.waitForSelector("#forecast");
      await page.setInputFiles("#cec-file", rawFile);
      await page.waitForFunction(() => document.getElementById("import-msg").textContent.startsWith("נמצאו"));
      result.imported = { panel: def, message: await page.evaluate(() => document.getElementById("import-msg").textContent),
        direct: await page.evaluate(() => Object.fromEntries([...document.querySelectorAll("#forecast tbody tr")].map((r) => [r.dataset.letter, +r.dataset.direct]))) };
    }
    await page.close();
  }
  await browser.close();
  console.log(JSON.stringify(result));
})();

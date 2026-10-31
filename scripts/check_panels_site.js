// Checks reports/knesset_27_panels.html in Chromium: no console errors, no
// horizontal page scroll at desktop and phone width, and the calculator's
// example forecast for every panel (printed as JSON for
// scripts/check_panels_site.py to compare with the Python model).
// Screenshots go to <out_dir>.
//
// Usage: node scripts/check_panels_site.js <out_dir>
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

(async () => {
  const outDir = process.argv[2];
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
    await page.screenshot({ path: path.join(outDir, `panels_${name}.png`), fullPage: true });
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
    }
    await page.close();
  }
  await browser.close();
  console.log(JSON.stringify(result));
})();

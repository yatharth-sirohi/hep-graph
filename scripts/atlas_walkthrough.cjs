// Open every local map of a running HEP Atlas the way a reader would and
// record what is on screen: shapes drawn, feature rows, unlocated rows, the
// scale bar, console errors. Screenshots go to OUT; a summary JSON is printed.
//
//   NODE_PATH=<repo>/node_modules node scripts/atlas_walkthrough.cjs \
//     http://localhost:8830 /path/to/out [slug ...]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.argv[2] || 'http://localhost:8830';
const OUT = process.argv[3] || 'walkthrough';
const ONLY = process.argv.slice(4);

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const atlas = await (await fetch(`${BASE}/atlas/generated/atlas.json`)).json();
  const mapRecords = Array.isArray(atlas.maps) ? atlas.maps : Object.values(atlas.maps || {});
  const maps = mapRecords.map((m) => m.id.replace(/^map:/, ''))
    .filter((slug) => !ONLY.length || ONLY.includes(slug));
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', (err) => errors.push(String(err)));

  const rows = [];
  for (const slug of maps) {
    errors.length = 0;
    const loaded = await page.goto(`${BASE}/atlas#/map/${slug}`, { waitUntil: 'load', timeout: 180000 })
      .then(() => true, (err) => { errors.push(`goto: ${err.message.split('\n')[0]}`); return false; });
    if (!loaded) { rows.push({ slug, shapes: 0, markers: 0, featureRows: 0, unlocated: 0, checksPassed: 0, checksFailed: 0, scaleBar: null, errors: [...errors] }); continue; }
    await page.waitForSelector('.leaflet-container', { timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(2500);
    const seen = await page.evaluate(() => {
      const q = (s) => document.querySelectorAll(s).length;
      const scale = document.querySelector('.leaflet-control-scale-line');
      return {
        title: (document.querySelector('.map-view h2, .map-view h1') || {}).textContent || null,
        shapes: q('.leaflet-overlay-pane path'),
        markers: q('.leaflet-marker-pane > *'),
        featureRows: q('.map-feature-rows > *'),
        unlocated: q('.map-unlocated-row'),
        checksPassed: q('.map-check.is-passed'),
        checksFailed: q('.map-check.is-failed'),
        scaleBar: scale ? scale.textContent : null,
      };
    });
    const shot = path.join(OUT, `${slug}.png`);
    await page.screenshot({ path: shot, timeout: 60000 }).catch((err) => errors.push(`screenshot: ${err.message.split('\n')[0]}`));
    rows.push({ slug, ...seen, errors: [...errors], shot });
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'walkthrough.json'), JSON.stringify(rows, null, 1));
  for (const r of rows) {
    const flag = (!r.shapes && !r.markers) || r.errors.length || r.checksFailed || !r.scaleBar ? '  <-- look' : '';
    console.log(`${r.slug.padEnd(44)} shapes ${String(r.shapes).padStart(4)} markers ${String(r.markers).padStart(4)} rows ${String(r.featureRows).padStart(3)} unlocated ${String(r.unlocated).padStart(2)} checks ${r.checksPassed}/${r.checksPassed + r.checksFailed} scale ${r.scaleBar || '-'} errors ${r.errors.length}${flag}`);
  }
})();

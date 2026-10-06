import { chromium, expect } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';

// Read-only UI audit. No intercepted responses or simulated healthy database.
const directory = 'report/evidence/phase00-02-review';
mkdirSync(directory, { recursive: true });
const browser = await chromium.launch();
const context = await browser.newContext({ reducedMotion: 'reduce' });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(error.message));
const routes = ['/', '/explore', '/journey', '/stories/lantern-path', '/lens', '/guide', '/dna', '/sources'];
const results = { mode: 'demo', database: 'unavailable', states: [], selectorChecks: {}, errors };
try {
  for (const viewport of [{ width: 1600, height: 900 }, { width: 390, height: 844 }, { width: 768, height: 1024 }]) {
    await page.setViewportSize(viewport);
    for (const locale of ['en', 'zh-CN']) {
      await context.addCookies([{ name: 'folkverse_locale', value: locale, url: 'http://127.0.0.1:3000' }]);
      for (const route of routes) {
        const response = await page.goto(`http://127.0.0.1:3000${route}`);
        await page.evaluate(() => document.fonts.ready);
        await page.locator('h1').waitFor({ state: 'visible' });
        const state = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth > innerWidth,
          locale: document.documentElement.lang,
          heading: document.querySelector('h1')?.textContent,
          atlasVisible: !!document.querySelector('.liaoning-atlas') && !!document.querySelector('.liaoning-atlas')?.getBoundingClientRect().height,
        }));
        results.states.push({ route, viewport, locale, status: response.status(), ...state });
        if (locale === 'en' && viewport.width !== 768) {
          await page.screenshot({ path: `${directory}/${route === '/' ? 'home' : route.split('/')[1]}-${viewport.width}.png`, fullPage: true, animations: 'disabled' });
        }
      }
    }
  }
  await context.addCookies([{ name: 'folkverse_locale', value: 'en', url: 'http://127.0.0.1:3000' }]);
  await page.setViewportSize({ width: 1600, height: 900 });
  await page.goto('http://127.0.0.1:3000/guide');
  results.selectorChecks.oldHomeLink = await page.getByRole('link', { name: 'FolkVerse China', exact: true }).count();
  results.selectorChecks.actualHomeLink = await page.getByRole('link', { name: 'FolkVerse home', exact: true }).count();
  results.selectorChecks.oldGuideSceneImage = await page.locator('.scene-picture img').count();
  results.selectorChecks.newGuideImage = await page.locator('.jinyao-cinematic-image img').count();
  await page.goto('http://127.0.0.1:3000/explore');
  results.selectorChecks.defaultView = await page.getByRole('button', { name: 'Explore map', exact: true }).getAttribute('aria-pressed');
  results.selectorChecks.defaultAtlasVisible = await page.locator('.liaoning-atlas').isVisible();
  await page.getByRole('button', { name: 'Preview examples', exact: true }).click();
  await page.getByRole('button', { name: 'Music', exact: true }).click();
  const opener = page.getByRole('button', { name: /An evening of melodies/ });
  await opener.click();
  await expect(page.getByRole('button', { name: 'Close sources', exact: true })).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(page.getByRole('link', { name: /Explore the evidence chain/ })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', { name: 'Close sources', exact: true })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(opener).toBeFocused();
  results.fixtureDrawerKeyboard = 'PASS (labelled fixture; not a published source)';
  await page.goto('http://127.0.0.1:3000/stories/lantern-path');
  await expect(page.getByRole('button', { name: 'Play narration', exact: true })).toBeEnabled();
  await page.getByRole('button', { name: 'Play narration', exact: true }).click();
  await expect.poll(() => page.locator('audio').evaluate(audio => audio.currentTime)).toBeGreaterThan(0);
  await page.getByRole('button', { name: /Follow the mountain light/ }).click();
  await expect(page.getByRole('heading', { name: 'The mountain light', exact: true })).toBeVisible();
  await expect(page.locator('audio')).toHaveCount(0);
  await page.getByRole('button', { name: /Begin again/ }).click();
  await page.getByRole('button', { name: /Cross the river bridge/ }).click();
  await expect(page.getByRole('heading', { name: 'The river bridge', exact: true })).toBeVisible();
  results.fixtureStoryAudioAndBranches = 'PASS (original fiction and real recorded audio)';
  await page.goto('http://127.0.0.1:3000/journey');
  await page.locator('summary').filter({ hasText: 'Preview a learning route' }).click();
  await page.getByRole('button', { name: 'Move down screen', exact: true }).click();
  await expect(page.locator('.journey-stops li').first()).toContainText('Fujian');
  await page.getByRole('button', { name: 'Remove table', exact: true }).click();
  await expect(page.locator('.journey-route .panel-heading')).toContainText('13 / 20');
  await page.evaluate(() => { document.body.style.zoom = '2'; });
  results.cssZoom200Overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  results.fixtureJourneyEdits = 'PASS (deterministic fixtures, not API journeys)';
  await page.evaluate(() => { document.body.style.zoom = ''; });
  const upstream = await page.request.get('http://127.0.0.1:3000/api/v1/health');
  results.health = { status: upstream.status(), body: await upstream.json() };
  console.log(JSON.stringify(results, null, 2));
} finally {
  writeFileSync(`${directory}/browser-probe.json`, `${JSON.stringify(results, null, 2)}\n`);
  await browser.close();
}

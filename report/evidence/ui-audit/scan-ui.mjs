import { chromium } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';

const directory = 'report/evidence/ui-audit';
mkdirSync(`${directory}/screens`, { recursive: true });
const routes = { home: '/', explore: '/explore', journey: '/journey', stories: '/stories/lantern-path', lens: '/lens', guide: '/guide', dna: '/dna', sources: '/sources', status: '/status' };
const sizes = { desktop: { width: 1600, height: 900 }, phone: { width: 390, height: 844 }, tablet: { width: 768, height: 1024 } };
const browser = await chromium.launch();
const results = [];
try {
 for (const [size, viewport] of Object.entries(sizes)) {
  for (const locale of ['en', 'zh-CN']) {
   const context = await browser.newContext({ viewport, reducedMotion: 'reduce', deviceScaleFactor: 1 });
   await context.addCookies([{ name: 'folkverse_locale', value: locale, url: 'http://127.0.0.1:3000' }]);
   for (const [name, route] of Object.entries(routes)) {
    const page = await context.newPage();
    const errors = [], failedRequests = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('requestfailed', request => failedRequests.push({ url: request.url(), error: request.failure()?.errorText }));
    const response = await page.goto(`http://127.0.0.1:3000${route}`, { waitUntil: 'networkidle' });
    await page.locator('img').evaluateAll(images => images.forEach(image => image.loading = 'eager'));
    await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth));
    await page.evaluate(() => document.fonts.ready);
    if (name === 'explore' || name === 'sources') await page.locator('.collection-results [role=status]').waitFor({ state: 'detached' });
    await page.screenshot({ path: `${directory}/screens/${name}-${size}-${locale}.png`, fullPage: true, animations: 'disabled' });
    const metrics = await page.evaluate(() => {
     const nav = document.querySelector('.nav-tabs'), current = nav?.querySelector('[aria-current=page]');
     const n = nav?.getBoundingClientRect(), c = current?.getBoundingClientRect();
     const controls = [...document.querySelectorAll('button,a,input,textarea,[role=button]')].filter(node => node.getBoundingClientRect().width && node.getBoundingClientRect().height).map(node => {
      const r=node.getBoundingClientRect(); const s=getComputedStyle(node);
      return { text: (node.getAttribute('aria-label') || node.textContent || '').trim().slice(0,100), width:r.width, height:r.height, fontSize:s.fontSize, tag:node.tagName, class:node.getAttribute('class') };
     });
     return {
      title: document.title, heading:document.querySelector('h1')?.textContent,
      documentWidth:document.documentElement.scrollWidth, documentHeight:document.documentElement.scrollHeight,
      viewportWidth:innerWidth, viewportHeight:innerHeight,
      currentTab: current ? { text:current.textContent, visible:c.left >= n.left && c.right <= n.right, left:c.left, right:c.right, navLeft:n.left, navRight:n.right, scrollLeft:nav.scrollLeft } : null,
      controlsBelow44: controls.filter(c => c.width < 44 || c.height < 44),
      smallText:[...document.querySelectorAll('p,span,small,label,a,button')].filter(node => node.getBoundingClientRect().width && parseFloat(getComputedStyle(node).fontSize) < 12 && node.textContent.trim()).map(node=>({text:node.textContent.trim().slice(0,120),fontSize:getComputedStyle(node).fontSize})),
      images:[...document.images].map(image => {const r=image.getBoundingClientRect(); return {src:image.currentSrc,alt:image.alt,renderWidth:r.width,renderHeight:r.height,naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,objectFit:getComputedStyle(image).objectFit,objectPosition:getComputedStyle(image).objectPosition,class:image.className}}),
      resources:performance.getEntriesByType('resource').map(entry=>({name:entry.name,transferSize:entry.transferSize,encodedBodySize:entry.encodedBodySize,duration:entry.duration})),
      landmarks:[...document.querySelectorAll('main,nav,header,footer')].map(node=>({tag:node.tagName,label:node.getAttribute('aria-label')})),
     };
    });
    await page.addScriptTag({ path: '.local/ui-audit-axe.min.js' });
    const axe = await page.evaluate(async () => {
     const result = await window.axe.run(document, { runOnly: { type:'tag', values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice'] } });
     const summarize=items=>items.map(item=>({id:item.id,impact:item.impact,help:item.help,helpUrl:item.helpUrl,nodes:item.nodes.map(node=>({target:node.target,html:node.html,failureSummary:node.failureSummary}))}));
     return {version:result.testEngine.version,violations:summarize(result.violations),incomplete:summarize(result.incomplete)};
    });
    const result={name,route,size,locale,status:response.status(),errors,failedRequests,metrics,axe};
    results.push(result);
    writeFileSync(`${directory}/scan.json`,JSON.stringify({checked_at:new Date().toISOString(),results},null,2)+'\n');
    console.log(`${name} ${size} ${locale}: HTTP ${result.status}, overflow ${metrics.documentWidth > viewport.width}, axe ${axe.violations.map(v=>v.id).join(',') || 'none'}, active tab ${metrics.currentTab?.visible ?? 'n/a'}`);
    await page.close();
   }
   await context.close();
  }
 }
} finally { await browser.close(); }

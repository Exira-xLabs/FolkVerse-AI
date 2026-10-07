// Real local browser/BFF/API/provider checks. No network response interception or keys.
import { chromium } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
const followups = process.argv.includes('--followups');
const polish = process.argv.includes('--polish');
const output = polish ? 'report/evidence/phase03-hybrid-part06-live' : followups ? 'report/evidence/phase03-hybrid-part04-followups' : 'report/evidence/phase03-hybrid-part04';
mkdirSync(output, { recursive: true });
const result = { started_at: new Date().toISOString(), mode: 'real local browser/BFF/API/configured provider', turns: [], errors: [] };
const browser = await chromium.launch();
try {
  for (const questions of polish ? [
    ['Explain Fuzhou shadow puppetry', '剪影是什么意思？'],
    ['沈阳故宫始建于哪一年？'],
  ] : followups ? [
    ['Explain Fuzhou shadow puppetry', '请用中文再解释一次'],
    ['When was Shenyang Imperial Palace founded?', 'Explain that simply'],
  ] : [
    ['Explain Fuzhou shadow puppetry', 'What is shadow puppetry?', '什么是皮影戏？', 'When was Shenyang Imperial Palace founded?'],
    ['沈阳故宫始建于哪一年？', 'When was Fuzhou shadow puppetry invented?', 'What are the current opening hours of Shenyang Imperial Palace?'],
  ]) {
    const context = await browser.newContext(); const page = await context.newPage();
    page.on('pageerror', e => result.errors.push(e.message));
    await page.addInitScript(() => {
      window.__frames = [];
      const original = window.fetch;
      window.fetch = async (...args) => {
        const response = await original(...args);
        const input = args[0]; const url = typeof input === 'string' ? input : input.url ?? String(input);
        if (new URL(url, location.href).pathname === '/api/v1/guide') response.clone().text().then(text => window.__frames.push({ status: response.status, text })).catch(() => window.__frames.push(null));
        return response;
      };
    });
    await page.goto('http://127.0.0.1:3000/guide');
    await page.getByRole('button', { name: 'Open Jinyao chat', exact: true }).click();
    await page.getByRole('combobox', { name: 'Explanation depth' }).selectOption('beginner');
    if (followups) await page.getByRole('checkbox').check();
    for (const question of questions) {
      const index = result.turns.length;
      const localIndex = await page.evaluate(() => window.__frames.length);
      const started = performance.now();
      await page.getByRole('textbox').fill(question); await page.getByRole('textbox').press('Enter');
      await page.waitForFunction(n => window.__frames.length > n, localIndex, { timeout: 65000 });
      const observation = await page.evaluate(n => window.__frames[n], localIndex);
      const events = {};
      for (const frame of observation?.text.split(/\r?\n\r?\n/) ?? []) {
        const name = /^event: (.+)/m.exec(frame)?.[1]; const data = /^data: (.+)/m.exec(frame)?.[1];
        if (name && data) events[name] = JSON.parse(data);
      }
      const answer = events.answer;
      await page.waitForFunction(() => document.querySelector('.jinyao-chat-turn:last-child')?.getAttribute('data-status') !== 'pending', {}, { timeout: 65000 });
      result.turns.push({ question, status: observation?.status, elapsed_ms: performance.now() - started, answer, sources: events.sources?.items, error: events.error, ui_status: await page.locator('.jinyao-chat-turn').last().getAttribute('data-status') });
      if (!answer || await page.locator('.jinyao-chat-turn').last().getAttribute('data-status') !== 'ready') result.errors.push(`Failed live turn ${index + 1}`);
      else if ((question.includes('invented') || question.includes('opening hours')) ? answer.status !== 'insufficient' : answer.status !== 'answered') result.errors.push(`Unexpected support state ${index + 1}`);
      if (answer?.evidence_ids.length) {
        await page.getByRole('button', { name: /Inspect answer sources|查看回答来源/ }).last().click();
        const dialog = page.getByRole('dialog', { name: /Evidence behind this answer|回答所依据的资料/ });
        await page.waitForTimeout(1500);
        if (!(await dialog.textContent()).includes(events.sources.items[0].text)) result.errors.push(`Source inspection failed ${index + 1}`);
        await page.keyboard.press('Escape');
      }
    }
    await page.evaluate(() => fetch('/api/v1/session', { method: 'DELETE' }));
    await context.close();
  }
} catch (error) { result.errors.push(error.message); }
finally { await browser.close(); result.completed_at = new Date().toISOString(); writeFileSync(`${output}/live-hybrid.json`, JSON.stringify(result, null, 2)+'\n'); }
console.log(JSON.stringify({ turns: result.turns.map(t => ({ question: t.question, status: t.answer?.status, reason: t.answer?.reason, elapsed_ms: t.elapsed_ms, ui_status: t.ui_status, provider: !!t.answer?.provider_attempt_id, error: t.error })), errors: result.errors }, null, 2));
process.exitCode = result.errors.length ? 1 : 0;

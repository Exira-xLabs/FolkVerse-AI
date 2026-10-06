// Real local browser/BFF/API delivery smoke check. No response interception.
// Requires running live services; may use their normal bounded provider quota
// once generated social replies replace the current policy replies. Changes no config.
import { chromium } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const base = new URL(process.env.FOLKVERSE_DELIVERY_URL ?? 'http://127.0.0.1:3000');
if (!['127.0.0.1', 'localhost', '[::1]'].includes(base.hostname) ||
    !['http:', 'https:'].includes(base.protocol) || base.username || base.password) {
  throw new Error('Delivery verification requires a local service URL without credentials.');
}
const output = process.env.FOLKVERSE_EVIDENCE_DIR ?? 'report/evidence/phase03-hybrid-part01-final';
mkdirSync(output, { recursive: true });
const result = { mode: 'real local browser/BFF/API; no intercepted responses', checks: [], errors: [], provider_usage: 'Not scored by this delivery check; configured service admission applies.' };
const check = (name, passed) => {
  result.checks.push({ name, passed });
  if (!passed) throw new Error(`Check failed: ${name}`);
};
const browser = await chromium.launch();
const page = await browser.newPage();
page.on('pageerror', () => { result.errors.push('Browser page exception'); });
try {
  await page.goto(new URL('/guide', base).href);
  await page.getByRole('button', { name: 'Open Jinyao chat', exact: true }).click();
  check('live chat visible', (await page.locator('.jinyao-chat-notice').innerText()).includes('configured AI provider'));
  for (const [locale, message, sendName] of [['en', 'hi', 'Send message'], ['zh-CN', '你好', '发送消息']]) {
    if (locale === 'zh-CN') {
      await page.getByRole('button', { name: 'Close Jinyao chat', exact: true }).click();
      await page.getByRole('button', { name: 'Switch to Chinese', exact: true }).click();
      await page.getByRole('button', { name: '打开锦瑶聊天', exact: true }).click();
    }
    await page.getByRole('textbox').fill(message);
    await page.getByRole('textbox').press('Enter');
    const turn = page.locator('.jinyao-chat-turn').last();
    await turn.locator('.from-jinyao').waitFor();
    await page.waitForFunction(() => document.querySelector('.jinyao-chat-turn:last-child')?.getAttribute('data-status') !== 'pending', { }, { timeout: 65000 });
    check(`${locale} greeting reaches ready state`, await turn.getAttribute('data-status') === 'ready');
    check(`${locale} reply is nonempty`, !!(await turn.locator('.from-jinyao p').first().innerText()).trim());
    await page.getByRole('textbox').fill(locale === 'en' ? 'Next message' : '下一条消息');
    check(`${locale} composer released`, await page.getByRole('button', { name: sendName, exact: true }).isEnabled());
    await page.getByRole('textbox').fill('');
  }
  const count = await page.locator('.jinyao-chat-turn').count();
  await page.getByRole('button', { name: '关闭锦瑶聊天', exact: true }).click();
  await page.getByRole('button', { name: '打开锦瑶聊天', exact: true }).click();
  check('close/reopen preserves both greetings', await page.locator('.jinyao-chat-turn').count() === count && count === 2);
  check('no browser exceptions', result.errors.length === 0);
} catch (error) {
  // Store controlled check failures, not service payloads, cookies or private messages.
  result.errors.push(error.message.startsWith('Check failed:') ? error.message : 'Delivery walkthrough could not complete; inspect local service status.');
} finally {
  await page.evaluate(() => fetch('/api/v1/session', { method: 'DELETE' })).catch(() => undefined);
  await browser.close();
  writeFileSync(path.join(output, 'live-delivery.json'), JSON.stringify(result, null, 2) + '\n');
}
console.log(JSON.stringify(result, null, 2));
process.exitCode = result.errors.length || result.checks.some(item => !item.passed) ? 1 : 0;

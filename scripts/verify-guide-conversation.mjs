// Local real-provider walkthrough. Uses existing admission/budget; never reads keys.
import { chromium } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const base = new URL(process.env.FOLKVERSE_DELIVERY_URL ?? 'http://127.0.0.1:3000');
if (!['127.0.0.1', 'localhost', '[::1]'].includes(base.hostname) || !['http:', 'https:'].includes(base.protocol) || base.username || base.password) throw new Error('Local URL required.');
const output = process.env.FOLKVERSE_EVIDENCE_DIR ?? 'report/evidence/phase03-hybrid-part02';
mkdirSync(output, { recursive: true });
const result = { started_at: new Date().toISOString(), mode: 'Real local browser/BFF/API and configured model; no intercepted responses', checks: [], errors: [], turns: [] };
const check = (name, passed) => { result.checks.push({ name, passed }); if (!passed) throw new Error(`Check failed: ${name}`); };
const browser = await chromium.launch(); const page = await browser.newPage();
page.on('pageerror', () => result.errors.push('Browser exception'));
// Chromium does not expose a consumed fetch SSE body through Response.text().
// Observe a clone in the page; return the original network response unchanged.
await page.addInitScript(() => {
  window.__guideObservations = [];
  const original = window.fetch;
  window.fetch = async (...args) => {
    const response = await original(...args);
    const input = args[0];
    const url = typeof input === 'string' ? input : input.url ?? String(input);
    if (new URL(url, location.href).pathname === '/api/v1/guide') {
      response.clone().text().then(text => {
        const frame = text.split(/\r?\n\r?\n/).find(p => /^event: answer\r?\n/.test(p));
        const data = frame?.split(/\r?\n/).find(line => line.startsWith('data: '));
        const answer = data ? JSON.parse(data.slice(6)) : null;
        window.__guideObservations.push(answer ? {
          locale: answer.locale, answer_text: answer.answer_text,
          conversation_choice: answer.conversation_choice,
          provider_attempt: !!answer.provider_attempt_id,
          presentation_version: answer.presentation_version,
          claim_count: answer.claims.length, evidence_count: answer.evidence_ids.length,
        } : null);
      }).catch(() => window.__guideObservations.push(null));
    }
    return response;
  };
});
const send = async (message, expectedLocale, expectedPairs) => {
  const outgoing = page.waitForRequest(r => r.url().endsWith('/api/v1/guide'));
  const observationIndex = result.turns.length;
  await page.getByRole('textbox').fill(message); await page.getByRole('textbox').press('Enter');
  const request = (await outgoing).postDataJSON();
  check(`${message}: request language`, request.locale === expectedLocale);
  check(`${message}: consented history count`, request.conversation.length === expectedPairs);
  await page.waitForFunction(() => document.querySelector('.jinyao-chat-turn:last-child')?.getAttribute('data-status') !== 'pending', {}, { timeout: 65000 });
  await page.waitForFunction(index => window.__guideObservations.length > index, observationIndex, { timeout: 65000 });
  const answer = await page.evaluate(index => window.__guideObservations[index], observationIndex);
  check(`${message}: checked answer frame`, !!answer);
  check(`${message}: published ready reply`, await page.locator('.jinyao-chat-turn').last().getAttribute('data-status') === 'ready');
  check(`${message}: real model composition`, answer.provider_attempt && answer.presentation_version === 'conversation_composition_v1');
  check(`${message}: no cultural evidence invented`, answer.claim_count === 0 && answer.evidence_count === 0);
  result.turns.push({ input: message, locale: answer.locale, reply: answer.answer_text, model_attempt: true, history_pairs: request.conversation.length });
  return answer;
};
try {
  await page.goto(new URL('/guide', base).href);
  await page.getByRole('button', { name: 'Open Jinyao chat', exact: true }).click();
  check('context off by default', !(await page.getByRole('checkbox').isChecked()));
  const first = await send('hi', 'en', 0);
  await page.getByRole('checkbox').check();
  const repeated = await send('hello', 'en', 1);
  check('consented repeated greeting varies opening and invitation', first.conversation_choice.opening_id !== repeated.conversation_choice.opening_id && first.conversation_choice.invitation_id !== repeated.conversation_choice.invitation_id);
  await send('你好', 'zh-CN', 2);
  await page.getByRole('combobox', { name: '回复语言' }).selectOption('en');
  await send('你好呀', 'en', 3);
  await page.getByRole('checkbox').uncheck();
  await send('thank you', 'en', 0);
  await send('bye', 'en', 0);
  await send('Nice to meet you, I’m new here', 'en', 0);
  await page.getByRole('combobox', { name: 'Reply language' }).selectOption('auto');
  await send('今天有点烦，想轻松聊聊', 'zh-CN', 0);
  check('no browser exceptions', result.errors.length === 0);
} catch (error) {
  result.errors.push(error.message.startsWith('Check failed:') ? error.message : 'Walkthrough could not complete; inspect service status.');
} finally {
  await page.evaluate(() => fetch('/api/v1/session', { method: 'DELETE' })).catch(() => undefined);
  await browser.close();
  result.completed_at = new Date().toISOString();
  writeFileSync(path.join(output, 'live-conversation.json'), JSON.stringify(result, null, 2) + '\n');
}
console.log(JSON.stringify(result, null, 2));
process.exitCode = result.errors.length ? 1 : 0;

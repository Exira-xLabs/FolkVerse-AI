import { chromium } from '@playwright/test';
import { writeFileSync } from 'node:fs';
const browser=await chromium.launch();
const context=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,reducedMotion:'reduce'});
const page=await context.newPage();const checks=[];
try {
 await page.goto('http://127.0.0.1:3000/explore');
 await page.locator('.atlas-world').waitFor();
 checks.push({id:'phone-map-sizes',...await page.locator('.atlas-city-name').first().evaluate(node=>{
  const matrix=node.getScreenCTM(),font=parseFloat(getComputedStyle(node).fontSize);
  return {fontCSS:font,screenFontHeight:font*Math.hypot(matrix.c,matrix.d),devicePixelRatio:devicePixelRatio};
 })});
 await page.goto('http://127.0.0.1:3000/stories/lantern-path');
 await page.waitForTimeout(2000);
 checks.push({id:'audio-metadata',...await page.locator('audio').evaluate(audio=>({duration:audio.duration,readyState:audio.readyState,error:audio.error?.message,networkState:audio.networkState})),display:await page.locator('.audio-controls').innerText()});
 await page.getByRole('button',{name:'Switch to Chinese'}).click();
 checks.push({id:'chinese-audio',...await page.locator('audio').evaluate(audio=>({src:audio.src,duration:audio.duration})),display:await page.locator('.audio-controls').innerText()});
 await page.goto('http://127.0.0.1:3000/guide');
 await page.screenshot({path:'report/evidence/ui-audit/states/guide-phone-dpr2.png',fullPage:true});
 await page.setViewportSize({width:320,height:844});
 for(const route of ['/','/explore','/journey','/stories/lantern-path','/lens','/guide','/dna','/sources','/status']){
  await page.goto('http://127.0.0.1:3000'+route);
  checks.push({id:'320-reflow',route,...await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth}))});
 }
 await page.goto('http://127.0.0.1:3000/explore');
 await page.getByRole('button',{name:/复州皮影戏/}).click();
 const dialog=page.getByRole('dialog');
 await dialog.getByRole('heading',{name:'复州皮影戏',exact:true}).waitFor();
 const before=await page.evaluate(()=>window.scrollY);
 await page.mouse.move(5,500);await page.mouse.wheel(0,-450);await page.waitForTimeout(100);
 checks.push({id:'modal-background-scroll',before,after:await page.evaluate(()=>window.scrollY)});
 await page.screenshot({path:'report/evidence/ui-audit/states/source-drawer-phone-320.png',fullPage:false});
 writeFileSync('report/evidence/ui-audit/extra.json',JSON.stringify({checked_at:new Date().toISOString(),checks},null,2)+'\n');
 console.log(JSON.stringify(checks,null,2));
}finally{await browser.close();}

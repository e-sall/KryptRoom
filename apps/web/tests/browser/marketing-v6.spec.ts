import {test,expect,type Page} from '@playwright/test';
import {setCssViewport} from './css-viewport';
async function disjoint(page:Page,selector:string){
 const boxes=await page.locator(selector).evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));expect(boxes).toHaveLength(4);
 for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],b=boxes[j];expect(a.right<=b.left||b.right<=a.left||a.bottom<=b.top||b.bottom<=a.top).toBe(true);}
 if(await page.evaluate(()=>innerWidth>=768))expect(boxes[2].top-boxes[1].bottom).toBeGreaterThanOrEqual(24);
}
test('V6 real DAG rectangles remain disjoint on homepage, Product and technical demo',async({page},info)=>{
 test.setTimeout(90000);
 for(const width of [320,375,390,834,1366,1440,1536,1600,1920]){
  await setCssViewport(page,{width,height:width<768?844:900});await page.emulateMedia({reducedMotion:'reduce'});
  for(const [route,selector] of [['/','.persistent-visual .showcase-state'],['/product','.product-state-story .showcase-state'],['/demo','.demo-state']]){
   await page.goto(route);await page.evaluate(()=>document.fonts.ready);if(route==='/demo')await page.getByRole('button',{name:'Scene 7: Explore the State',exact:true}).click();
   await disjoint(page,selector);const edges=page.locator(route==='/demo'?'.demo-desktop-edges path':'.showcase-edges-desktop path');
   expect(await edges.evaluateAll(es=>es.map(e=>[e.getAttribute('data-edge'),e.getAttribute('data-parent-index')]))).toEqual([['S1-S2','0'],['S1-S3','0'],['S2-S4','0'],['S3-S4','1']]);
   const labels=await page.locator(selector).evaluateAll(es=>es.map(e=>({scroll:e.scrollHeight,client:e.clientHeight,wide:e.scrollWidth,width:e.clientWidth})));for(const l of labels){expect(l.scroll).toBeLessThanOrEqual(l.client+1);expect(l.wide).toBeLessThanOrEqual(l.width+1);}
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  }
 }
 await page.screenshot({path:info.outputPath('v6-technical-lineage.png'),fullPage:true});
});
test('V6 natural sticky story reaches four phases before release and reverses without a scroll trap',async({page})=>{
 await setCssViewport(page,{width:1366,height:768});await page.emulateMedia({reducedMotion:'no-preference'});await page.goto('/');
 const track=page.locator('#how-it-works'),panel=track.locator('.how-panel');await expect(track).toHaveAttribute('data-enhanced','true');
 for(const step of [0,1,2,3,1,0,3]){
  await track.evaluate((e,i)=>{const p=e.querySelector('.how-panel')!;const r=e.getBoundingClientRect();const distance=r.height-p.getBoundingClientRect().height;scrollTo(0,scrollY+r.top-110+distance*(i*.23+.01));},step);
  await expect(track.locator('.how-visual')).toHaveAttribute('data-step',String(step));
  const r=await panel.boundingBox(),nav=await page.locator('.marketing-navbar').boundingBox();expect(r!.y).toBeGreaterThan(nav!.y+nav!.height+16);expect(r!.y+r!.height).toBeLessThanOrEqual(768);
 }
 const last=track.getByRole('button',{name:/Run Computation/});await last.focus();await page.keyboard.press('Enter');await expect(last).toHaveAttribute('aria-current','step');
 const before=await page.evaluate(()=>scrollY);await page.keyboard.press('PageDown');await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(before);
 await track.evaluate(e=>scrollTo(0,scrollY+e.getBoundingClientRect().bottom+10));await expect(page.locator('.persistent-scene')).toBeInViewport();
 await page.emulateMedia({reducedMotion:'reduce'});expect(await panel.evaluate(e=>getComputedStyle(e).position)).toBe('static');
});
test('V6 exterior labels, combined positioning, subtle icons and decorative CTA retain accessible actions',async({page})=>{
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await page.evaluate(()=>document.fonts.ready);
 for(const selector of ['.why-scene','.persistent-scene','.founder-scene','#how-it-works','.home-cta-section']){
  const section=page.locator(selector),label=await section.locator(':scope>.section-label').boundingBox(),panel=await section.locator(':scope>.section-panel,:scope>.how-panel,:scope>.home-final-cta').boundingBox();expect(label!.y+label!.height).toBeLessThan(panel!.y);expect(Math.abs(label!.x-panel!.x)).toBeLessThan(1);
 }
 const position=await page.locator('.hero-positioning').boundingBox(),headline=await page.locator('#home-title').boundingBox();expect(position!.y+position!.height).toBeLessThan(headline!.y);await expect(page.locator('.hero-positioning')).toContainText('with Incoming Quantum Computing Layer');await expect(page.locator('.home-hero>.quantum-marker')).toHaveCount(0);
 for(const link of await page.locator('.founder-links a').all()){expect(await link.evaluate(e=>getComputedStyle(e).borderTopWidth)).toBe('0px');const box=await link.boundingBox();expect(box!.width).toBeGreaterThanOrEqual(44);expect(await link.locator('svg').evaluate(e=>e.getBoundingClientRect().width)).toBe(18);}
 await page.locator('.solutions-dropdown summary').click();await expect(page.locator('.solutions-menu>a>span[aria-hidden]')).toHaveCount(0);
 await expect(page.locator('.cta-structure')).toHaveAttribute('aria-hidden','true');await page.locator('.home-final-cta a').focus();await expect(page.locator('.home-final-cta a')).toBeFocused();await expect(page.locator('.home-final-cta a')).toHaveAttribute('href','/book-demo');
 await page.goto('/developers');const rects=await page.locator('.marketing-reading>p:last-of-type,.marketing-reading>.button-row').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));expect(rects[1].top-rects[0].bottom).toBeGreaterThanOrEqual(24);
});

test('V6 business copy and dashboard labels remain inside their panels at narrow widths',async({page})=>{
 await page.emulateMedia({reducedMotion:'reduce'});
 for(const width of [320,375,390]){await setCssViewport(page,{width,height:844});await page.goto('/');await page.evaluate(()=>document.fonts.ready);
 for(let i=0;i<7;i++){
  await page.locator('.business-controls nav button').nth(i).click();
  const blocks=await page.locator('.business-story-caption p,.business-story-caption h3,.business-panel[data-visible="true"] p,.business-panel[data-visible="true"] small,.business-panel[data-visible="true"] h3,.business-panel[data-visible="true"] li,.business-panel[data-visible="true"] .business-trend-axis').evaluateAll(es=>es.map(e=>({text:e.textContent,rect:e.getBoundingClientRect().toJSON(),frame:e.closest('.business-panel,.business-story-caption')!.getBoundingClientRect().toJSON(),font:parseFloat(getComputedStyle(e).fontSize)})));
  for(const b of blocks){expect(b.rect.top,b.text??'').toBeGreaterThanOrEqual(b.frame.top);expect(b.rect.bottom,b.text??'').toBeLessThanOrEqual(b.frame.bottom);expect(b.rect.left,b.text??'').toBeGreaterThanOrEqual(b.frame.left);expect(b.rect.right,b.text??'').toBeLessThanOrEqual(b.frame.right);expect(b.font,b.text??'').toBeGreaterThanOrEqual(12);}
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 }
 }
 for(const width of [834,1366]){await setCssViewport(page,{width,height:900});await page.goto('/');await page.locator('.business-controls nav button').nth(1).click();
 const label=await page.locator('.business-input-mask').boundingBox();for(const card of await page.locator('.business-environments article').all()){const r=await card.boundingBox();expect(label!.y).toBeGreaterThanOrEqual(r!.y+r!.height+8);}
 }
});

import { test, expect } from '@playwright/test';
import { setCssViewport } from './css-viewport';

test('V7.2 native wheel and keyboard selection',async({page})=>{
 await setCssViewport(page,{width:1366,height:768});await page.goto('/');await page.locator('.how-panel').scrollIntoViewIfNeeded();await page.getByRole('button',{name:/02 Invite Participants/}).click();const y=await page.evaluate(()=>scrollY);await page.mouse.move(700,350);await page.mouse.wheel(0,220);await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(y);await expect(page.locator('.how-visual')).toHaveAttribute('data-step','1');await page.mouse.wheel(0,-220);await expect.poll(()=>page.evaluate(()=>scrollY)).toBeLessThan(y+20);
 await page.emulateMedia({reducedMotion:'reduce'});for(let i=0;i<4;i++){const b=page.locator('.how-layout button').nth(i);await b.focus();await page.keyboard.press('Enter');await expect(b).toHaveAttribute('aria-current','step');await expect(page.locator('.how-visual')).toHaveAttribute('data-step',String(i));}await page.keyboard.press('Tab');await page.keyboard.press('End');await expect(page.locator('.marketing-footer')).toBeInViewport();
});
test('V7 canonical surfaces, inline Quantum and contained labels fit desktop at actual CSS sizes',async({page})=>{
 for(const [width,height] of [[1366,768],[1440,900],[1536,864],[1600,900],[1920,1080]]){
 await setCssViewport(page,{width,height});await page.goto('/');await page.evaluate(()=>document.fonts.ready);
 const lines=await page.locator('.hero-positioning p').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));expect(Math.abs(lines[0].top-lines[1].top)).toBeLessThan(3);
 for(const sel of ['.why-scene','.persistent-scene','#how-it-works']){const section=page.locator(sel),panel=section.locator('.section-panel,.how-panel');const p=await panel.boundingBox(),l=await section.locator('.section-label').boundingBox();expect(l!.y).toBeGreaterThan(p!.y);expect(l!.x).toBeGreaterThan(p!.x);expect(await panel.evaluate(e=>getComputedStyle(e).backgroundColor)).toBe('rgb(25, 25, 24)');}
 for(const a of await page.locator('.home-narrative>a,.persistent-editorial>a').all())expect(await a.evaluate(e=>getComputedStyle(e).fontSize)).toBe('13px');
 await expect(page.getByText('Conceptual architecture · no raw dataset is loaded or exchanged by this preview.')).toHaveCount(0);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width ?? innerWidth))).toBe(true);
 }
});
test('V7 technical presentation expands its graph without changing scene or selected state',async({page})=>{
 await setCssViewport(page,{width:1366,height:768});await page.goto('/demo');await page.getByRole('button',{name:'Scene 7: Explore the State',exact:true}).click();await page.getByRole('button',{name:'Inspect S2: Private Join',exact:true}).click();
 const before=await page.locator('.demo-center').boundingBox();await page.getByRole('button',{name:'Presentation',exact:true}).click();expect((await page.locator('.demo-center').boundingBox())!.width).toBeGreaterThan(before!.width);await expect(page.locator('.demo-selected-state h3')).toContainText('S2');
 await page.getByRole('button',{name:'Explore',exact:true}).click();await expect(page.locator('.demo-selected-state h3')).toContainText('S2');await expect(page.locator('.demo-current')).toContainText('Explore the State');
});
test('V7 editorial pages retain accurate Quantum, security index, contact and roomy developer actions',async({page})=>{
 await page.goto('/technology');await expect(page.locator('.quantum-research h2')).toHaveText('Incoming Quantum Computing Layer');await expect(page.locator('.quantum-research')).toContainText('no operational QPU integration');
 await page.goto('/security');for(const a of await page.locator('.technical-index a').all()){const href=await a.getAttribute('href');await expect(page.locator(href!)).toHaveCount(1);}
 await page.goto('/developers');const r=await page.locator('.marketing-reading>p:last-of-type,.marketing-reading>.button-row').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));expect(r[1].top-r[0].bottom).toBeGreaterThanOrEqual(40 - .05);
 await page.goto('/book-demo');await expect(page.getByRole('link',{name:/Contact the Founder/})).toHaveAttribute('href','mailto:elimanesall.eng@gmail.com?subject=KryptRoom%20-%20Demo%20Inquiry');
});

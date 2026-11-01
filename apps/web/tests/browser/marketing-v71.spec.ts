import {setCssViewport} from './css-viewport';
import {test,expect} from '@playwright/test';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const gallery=path.join(fileURLToPath(new URL('../../../../docs/m8/pr7/marketing-v72/',import.meta.url)),process.env.QA_BROWSER==='webkit'?'webkit':'.');
test('V7.1 actual desktop rectangles, subtle links, labels and pointer reveal',async({page})=>{
 test.setTimeout(90000);
 for(const [width,height] of [[1366,768],[1440,900],[1536,864]]){
  await setCssViewport(page,{width,height});await page.goto('/');await page.evaluate(()=>document.fonts.ready);
  const colors=await page.locator('.hero-positioning .eyebrow,.quantum-marker span').evaluateAll(es=>es.map(e=>getComputedStyle(e).color));expect(colors[0]).toBe(colors[1]);
  const boxes=await page.locator('.hero-positioning p').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));expect(Math.abs(boxes[0].top-boxes[1].top)).toBeLessThan(4);expect(boxes[1].left-boxes[0].right).toBeGreaterThanOrEqual(5);expect(boxes[1].left-boxes[0].right).toBeLessThanOrEqual(7);
  await page.screenshot({path:path.join(gallery,`${width}-hero.png`)});
  const link=page.locator('.why-scene .home-narrative>a');const style=await link.evaluate(e=>({font:getComputedStyle(e).fontSize,border:getComputedStyle(e).borderBottomWidth,dec:getComputedStyle(e).textDecorationLine}));expect(style).toEqual({font:'13px',border:'0px',dec:'none'});await link.hover();expect(await link.evaluate(e=>getComputedStyle(e).borderBottomWidth)).toBe('0px');
  expect(await page.locator('#how-it-works').evaluate(e=>getComputedStyle(e).borderTopWidth)).toBe('0px');
  for(const sel of ['.why-scene','.founder-scene']){const label=await page.locator(sel+' .home-narrative>.section-label').boundingBox();const title=await page.locator(sel+' .home-narrative h2').boundingBox();expect(title!.y-label!.y-label!.height).toBeLessThan(32);}
  const label=await page.locator('.persistent-scene .section-label').boundingBox(),frame=await page.locator('.persistent-scene .section-panel').boundingBox();expect(label!.y-frame!.y).toBeLessThanOrEqual(38);
  const fy=await page.locator('.founder-scene .section-label,.founder-profile h3').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().top));expect(Math.abs(fy[0]-fy[1])).toBeLessThan(3);
  if(width<=1440){for(const [name,sel] of [['why','.why-scene'],['technology','.persistent-scene'],['founder','.founder-scene']] as const)await page.locator(sel).screenshot({path:path.join(gallery,`${width}-${name}.png`)});await link.screenshot({path:path.join(gallery,`${width}-secondary-link.png`)});}
  if(width<=1440){for(let step=0;step<4;step++){await page.locator('.how-layout button').nth(step).click();await page.waitForTimeout(600);await page.locator('.how-panel').screenshot({path:path.join(gallery,`${width}-how-${step+1}.png`)});}}
  const cta=page.locator('.home-final-cta');expect(await cta.locator('.cta-local .cta-structure').evaluate(e=>getComputedStyle(e).opacity)).toBe('1');await cta.scrollIntoViewIfNeeded();await page.mouse.move(5,5);expect(await cta.locator('.cta-local').evaluate(e=>getComputedStyle(e).opacity)).toBe('0');const r=await cta.boundingBox();
  if(width<=1440)await cta.screenshot({path:path.join(gallery,`${width}-cta-rest.png`)});
  for(const [name,x,y] of [['top-left',.1,.15],['center',.5,.5],['button',.5,.8],['bottom-right',.9,.85]] as const){await page.mouse.move(r!.x+r!.width*x,r!.y+r!.height*y);await expect(cta).toHaveAttribute('data-pointer','true');await expect.poll(()=>cta.locator('.cta-local').evaluate(e=>getComputedStyle(e).opacity)).toBe('1');if(width<=1440)await cta.screenshot({path:path.join(gallery,`${width}-cta-${name}.png`)});}
  await page.mouse.move(5,5);await expect(cta).toHaveAttribute('data-pointer','false');await expect.poll(()=>cta.locator('.cta-local').evaluate(e=>getComputedStyle(e).opacity)).toBe('0');if(width<=1440)await cta.screenshot({path:path.join(gallery,`${width}-cta-leave.png`)});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width ?? innerWidth))).toBe(true);
  await page.goto('/technology');const rd=page.locator('.quantum-research');await expect(rd.locator('p')).toHaveCount(1);await expect(rd).toContainText('This remains planned R&D');if(width<=1440)await rd.screenshot({path:path.join(gallery,`${width}-rd.png`)});
 }
});

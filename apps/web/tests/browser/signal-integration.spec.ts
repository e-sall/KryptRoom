import { test,expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { setCssViewport } from './css-viewport';
test('Signal exact source geometry, common eight-second bar animation and reduced motion',async({page})=>{
 await page.goto('/');await expect(page.locator('#kr-signal-v4 svg')).toHaveAttribute('viewBox','0 0 1000 508');
 await expect(page.locator('.cinematic-showcase')).toHaveCount(0);
 await expect(page.locator('#product-demo button,#product-demo a,#product-demo video,#product-demo canvas')).toHaveCount(0);
 const data=await page.locator('#kr-signal-v4').evaluate(e=>({
  circles:[...e.querySelectorAll('.rings circle')].map(n=>[n.getAttribute('cx'),n.getAttribute('cy'),n.getAttribute('r')]),
  widths:[...e.querySelectorAll('.risk-fill-group rect')].map(n=>n.getAttribute('width')),
  animations:[...e.querySelectorAll('.rings,.ring-dot,.metric,.risk-fill-group')].map(n=>({name:getComputedStyle(n).animationName,duration:getComputedStyle(n).animationDuration,iterations:getComputedStyle(n).animationIterationCount})),
 }));
 expect(data.circles).toEqual([['370','300','55'],['430','300','55']]);expect(data.widths).toEqual(['173','115.33','57.67']);
 expect(data.animations.map(a=>a.name).sort()).toEqual(['kr4bars','kr4dot','kr4metric','kr4rings']);
 data.animations.forEach(a=>{expect(a.duration).toBe('8s');expect(a.iterations).toBe('infinite');});
 const scales=[];for(const t of [0,4300,7000,8000,12300]){
  scales.push(await page.locator('.risk-fill-group').evaluate((e,t)=>{const animation=e.getAnimations()[0];animation.pause();animation.currentTime=t;return new DOMMatrix(getComputedStyle(e).transform).a;},t));
 }
 expect(scales[0]).toBeCloseTo(0);expect(scales[1]).toBeCloseTo(1);expect(scales[2]).toBeCloseTo(1);expect(scales[3]).toBeCloseTo(0);expect(scales[4]).toBeCloseTo(1);
 await page.emulateMedia({reducedMotion:'reduce'});
 await expect(page.locator('.risk-fill-group')).toHaveCSS('animation-name','none');
 expect(await page.locator('.risk-fill-group').evaluate(e=>new DOMMatrix(getComputedStyle(e).transform).a)).toBe(1);
 expect((await new AxeBuilder({page}).include('#product-demo').analyze()).violations).toEqual([]);
});
test('Signal retains native ratio across desktop tablet mobile with readable mobile alternative',async({page})=>{
 for(const [width,height]of [[1366,768],[1440,900],[1536,864],[1920,1080],[834,1112],[390,844],[320,800]]){
  await setCssViewport(page,{width,height});await page.goto('/');await page.emulateMedia({reducedMotion:'reduce'});
  await page.locator('.signal-showcase').evaluate(e=>scrollTo(0,scrollY+e.getBoundingClientRect().top-90));
  const r=await page.locator('#kr-signal-v4 svg').boundingBox();expect(r!.width/r!.height).toBeCloseTo(1000/508,2);
  // WebKit's physical-to-CSS conversion can report 1000.000076 for 1000px.
  expect(r!.width).toBeLessThanOrEqual(1000.001);expect(r!.y).toBeGreaterThanOrEqual(89);
  if(width>=1200)expect(r!.y+r!.height).toBeLessThan(height);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width??innerWidth))).toBe(true);
  if(width<700)await expect(page.locator('.signal-mobile-summary')).toBeVisible();
  await page.screenshot({path:test.info().outputPath(`signal-${width}.png`)});
 }
});
test('Walkthrough supplements technical exploration and half cursor keeps the original hotspot',async({page})=>{
 await setCssViewport(page,{width:1366,height:768});await page.goto('/demo');
 await page.getByRole('button',{name:'Scene 7: Explore the State',exact:true}).click();
 await page.getByRole('button',{name:'Inspect S2: Private Join',exact:true}).click();
 await page.getByRole('button',{name:'Presentation',exact:true}).click();await expect(page.locator('.demo-selected-state h3')).toContainText('S2');
 await page.getByRole('button',{name:'Explore',exact:true}).click();await expect(page.locator('.demo-selected-state h3')).toContainText('S2');
 await page.locator('#product-walkthrough').scrollIntoViewIfNeeded();await expect(page.locator('[data-movie-cursor]>path')).toHaveCount(1);
 const tip=await page.locator('[data-movie-cursor]>path').evaluate(e=>{const m=(e as SVGGraphicsElement).transform.baseVal.consolidate()!.matrix;const p=new DOMPoint(1,1).matrixTransform(m);return {x:p.x,y:p.y,scaleX:m.a,scaleY:m.d};});
 expect(tip).toEqual({x:1,y:1,scaleX:.5,scaleY:.5});
 expect((await new AxeBuilder({page}).include('#product-walkthrough').analyze()).violations).toEqual([]);
 await page.screenshot({path:test.info().outputPath('walkthrough-initial.png')});
});

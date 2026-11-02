import { test,expect,type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {setCssViewport} from './css-viewport';
const problems=new WeakMap<Page,string[]>();
test.beforeEach(async({page},info)=>{
 await setCssViewport(page,info.project.use.viewport!);const errors:string[]=[];problems.set(page,errors);
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()!=='GET'||!r.url().startsWith('http://127.0.0.1:3000/')||/\/api\/|rpc|groth16|sepolia/i.test(r.url()))errors.push(r.method()+' '+r.url());});page.on('websocket',ws=>errors.push(ws.url()));
});
test.afterEach(async({page})=>{expect(problems.get(page)).toEqual([]);expect(await page.evaluate(()=>[localStorage.length,sessionStorage.length,document.cookie])).toEqual([0,0,'']);});
test('Signal autoplay uses one eight-second bar timeline, loops and has no player controls',async({page})=>{
 await page.goto('/');const show=page.locator('.signal-showcase');await show.scrollIntoViewIfNeeded();
 await expect(show.locator('svg')).toHaveCount(1);await expect(show.locator('button,video,canvas,input,audio')).toHaveCount(0);
 await expect(show.locator('.risk-fill-group')).toHaveCSS('animation-duration','8s');await expect(show.locator('.risk-fill-group')).toHaveCSS('animation-iteration-count','infinite');
 const states=[];for(const t of [0,4300,8000,12300])states.push(await show.locator('.risk-fill-group').evaluate((e,t)=>{const a=e.getAnimations()[0];a.pause();a.currentTime=t;return new DOMMatrix(getComputedStyle(e).transform).a;},t));
 expect(states[0]).toBeCloseTo(0);expect(states[1]).toBeCloseTo(1);expect(states[2]).toBeCloseTo(0);expect(states[3]).toBeCloseTo(1);
});
test('Signal responsive native ratio, honest section evidence and accessible FAQ',async({page},info)=>{
 test.setTimeout(90000);await page.emulateMedia({reducedMotion:'reduce'});
 for(const [width,height]of [[1366,768],[834,1112],[390,844],[320,800]]){
  await setCssViewport(page,{width,height});await page.goto('/');const box=await page.locator('#kr-signal-v4 svg').boundingBox();expect(box!.width/box!.height).toBeCloseTo(1000/508,2);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width??innerWidth))).toBe(true);
  if(width<700)await expect(page.locator('.signal-mobile-summary')).toBeVisible();
  await page.locator('.signal-showcase').screenshot({path:info.outputPath(`signal-${width}.png`)});
 }
 for(const summary of await page.locator('.home-faq summary').all()){await summary.focus();await page.keyboard.press('Enter');await expect(summary.locator('..')).toHaveAttribute('open','');await page.keyboard.press('Enter');await expect(summary.locator('..')).not.toHaveAttribute('open','');}
 await expect(page.locator('.home-faq details')).toHaveCount(10);await expect(page.locator('.home-page>section:last-child')).toHaveAttribute('aria-labelledby','faq-title');
 expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
});
test('Signal reduced motion and no JavaScript preserve canonical content and technical links',async({page,browser},info)=>{
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await expect(page.locator('.risk-fill-group')).toHaveCSS('animation-name','none');
 expect(await page.locator('.risk-fill-group').evaluate(e=>new DOMMatrix(getComputedStyle(e).transform).a)).toBe(1);
 const ctx=await browser.newContext({javaScriptEnabled:false,viewport:info.project.use.viewport,reducedMotion:'reduce'}),p=await ctx.newPage();await setCssViewport(p,info.project.use.viewport!);await p.goto('http://127.0.0.1:3000/');
 await expect(p.locator('#kr-signal-v4 svg')).toBeVisible();await expect(p.locator('#kr-signal-v4')).toContainText('Only the signal.');await expect(p.getByRole('link',{name:'Interactive demo',exact:true})).toHaveAttribute('href','/demo');await expect(p.locator('.showcase-state')).toHaveCount(4);await ctx.close();
});
test('F01: complete Signal vector clears the actual floating navigation',async({page},info)=>{
 const sizes=info.project.name==='desktop'?[[1366,768],[1440,900]]:[[info.project.use.viewport!.width,info.project.use.viewport!.height]];
 for(const [width,height]of sizes){await setCssViewport(page,{width,height});await page.goto('/');await page.locator('.signal-showcase').evaluate(e=>scrollTo(0,scrollY+e.getBoundingClientRect().top-document.querySelector('.marketing-navbar')!.getBoundingClientRect().bottom-16));
  const nav=await page.locator('.marketing-navbar').boundingBox(),svg=await page.locator('#kr-signal-v4 svg').boundingBox();expect(svg!.y).toBeGreaterThanOrEqual(nav!.y+nav!.height+15);expect(svg!.x).toBeGreaterThanOrEqual(0);expect(svg!.x+svg!.width).toBeLessThanOrEqual(width);if(info.project.name==='desktop')expect(svg!.y+svg!.height).toBeLessThan(height);
 }
});
test('Signal declares synthetic approved aggregates and keeps canonical ring and data geometry',async({page})=>{
 await page.goto('/');const show=page.locator('#kr-signal-v4');for(const text of ['Only the signal.','Only approved aggregates are visible.','Independent data. Shared insight.','SYNTHETIC PREVIEW','NO LIVE COMPUTATION'])await expect(show).toContainText(text);
 expect(await show.locator('.risk-fill-group rect').evaluateAll(es=>es.map(e=>e.getAttribute('width')))).toEqual(['173','115.33','57.67']);
 expect(await show.locator('.rings circle').evaluateAll(es=>es.map(e=>[e.getAttribute('cx'),e.getAttribute('cy'),e.getAttribute('r')]))).toEqual([['370','300','55'],['430','300','55']]);
 await expect(page.locator('.cinematic-showcase')).toHaveCount(0);await expect(page.getByRole('link',{name:'Explore the full product walkthrough →'})).toHaveAttribute('href','/demo#product-walkthrough');
});
test("review F03: narrow ordered state cards have readable noncolliding labels", async ({page}) => {
  await page.emulateMedia({reducedMotion:"reduce"});
  for(const width of [320,375,390]) {
    await setCssViewport(page,{width,height:844}); await page.goto("/");
    const show=page.locator(".persistent-visual");
    const labels=await show.locator(".showcase-state > span, .showcase-state strong > span, .showcase-state small").evaluateAll(es=>es.map(e=>({font:parseFloat(getComputedStyle(e).fontSize),rect:e.getBoundingClientRect().toJSON(),parent:e.parentElement!.getBoundingClientRect().toJSON(),overflow:e.scrollWidth>e.clientWidth+1})));
    for(const label of labels) {expect(label.font).toBeGreaterThanOrEqual(12);expect(label.rect.left).toBeGreaterThanOrEqual(label.parent.left);expect(label.rect.right).toBeLessThanOrEqual(label.parent.right+1);expect(label.overflow).toBe(false);}
    for(const state of await show.locator(".showcase-state").all()) {
      // Explicit line boxes also cover hidden monospace metrics before the
      // first screenshot/font resolution on Linux, without relaxing stability.
      expect(await state.locator("strong, strong > span").evaluateAll(es=>es.map(e=>getComputedStyle(e).lineHeight))).toEqual(["20px","20px"]);
      const lines=await state.locator(":scope > span, :scope > strong, :scope > small").evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));
      for(let i=1;i<lines.length;i++) expect(lines[i].top).toBeGreaterThanOrEqual(lines[i-1].bottom);
    }
    const cards=await show.locator(".showcase-state").evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));
    for(let i=1;i<cards.length;i++) expect(cards[i].top).toBeGreaterThan(cards[i-1].bottom);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width??innerWidth))).toBe(true);
  }
});

test("review F04: original portrait uses local responsive optimization without layout shift", async ({page}) => {
  let release!:()=>void; const gate=new Promise<void>(resolve=>{release=resolve;});
  await page.route("**/images/elimane-sall-*.webp",async route=>{await gate;await route.continue();});
  const response=page.waitForResponse(r=>/\/images\/elimane-sall-\d+\.webp/.test(r.url()));
  await page.goto("/",{waitUntil:"domcontentloaded"});
  const portrait=page.getByAltText("Elimane Sall, founder of KryptRoom"); await portrait.scrollIntoViewIfNeeded();
  const before=await portrait.boundingBox(); release(); const delivered=await response;
  expect(delivered.status()).toBe(200); expect(delivered.headers()["content-type"]).toMatch(/^image\//);
  expect((await delivered.body()).length).toBeLessThan(300000);
  await portrait.evaluate(async e=>{await (e as HTMLImageElement).decode();});
  const url=new URL(await portrait.evaluate(e=>(e as HTMLImageElement).currentSrc));
  expect(url.pathname).toMatch(/^\/images\/elimane-sall-(480|768|1200)\.webp$/);
  await expect(page.locator(".founder-profile source")).toHaveAttribute("srcset",/1200w/);await expect(portrait).toHaveAttribute("width","3367");await expect(portrait).toHaveAttribute("height","3958");
  const after=await portrait.boundingBox();expect(after!.width).toBe(before!.width);expect(after!.height).toBe(before!.height);
  expect(await portrait.evaluate(e=>({fit:getComputedStyle(e).objectFit,position:getComputedStyle(e).objectPosition}))).toEqual({fit:"cover",position:"50% 35%"});
});

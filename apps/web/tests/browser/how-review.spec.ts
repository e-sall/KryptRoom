import { test, expect } from '@playwright/test';
import { collaborationSteps } from '../../src/features/marketing/collaboration-steps';
import { setCssViewport } from './css-viewport';

async function open(page: import('@playwright/test').Page) {
  await page.goto('/'); await page.evaluate(()=>document.fonts.ready);
  await expect(page.locator('#how-it-works')).toHaveAttribute('data-enhanced','true');
  await page.locator('.how-panel').scrollIntoViewIfNeeded();
}

async function assertStep(page: import('@playwright/test').Page, i: number) {
  await expect(page.locator('.how-visual')).toHaveAttribute('data-step',String(i));
  await expect(page.locator('.how-layout button[aria-current="step"]')).toHaveCount(1);
  await expect(page.locator('.how-layout button').nth(i)).toHaveAttribute('aria-current','step');
  await expect(page.locator('.how-visual figcaption > span')).toHaveText(`0${i+1} / 04`);
  await expect(page.locator('.how-visual figcaption strong')).toHaveText(collaborationSteps[i].title);
  await expect(page.locator('.how-visual figcaption p').first()).toHaveText(collaborationSteps[i].text);
  await expect(page.locator('.how-visual svg title')).toHaveText(`${collaborationSteps[i].title}: protected collaboration`);
  await expect(page.locator('.how-organizations')).toHaveAttribute('opacity',i>=1?'1':'0.12');
  await expect(page.locator('.how-inputs')).toHaveAttribute('opacity',i>=2?'1':'0');
  await expect(page.locator('.how-output')).toHaveAttribute('opacity',i===3?'1':'0');
}

// The acceptance path uses real wheel events only; no click, seek, scrollTo or timer.
async function wheelToStep(page: import('@playwright/test').Page,i:number) {
  for(let n=0;n<30;n++) {
    const distance=await page.locator('#how-it-works').evaluate((e,i)=>e.getBoundingClientRect().top-parseFloat((e as HTMLElement).style.getPropertyValue('--how-top'))+(i+.2)*Number((e as HTMLElement).dataset.scrollStep),i);
    if(Math.abs(distance)<2)break;
    const y=await page.evaluate(()=>scrollY);
    await page.mouse.wheel(0,Math.max(-160,Math.min(160,distance)));
    await expect.poll(()=>page.evaluate(()=>scrollY)).not.toBe(y);
    await page.waitForTimeout(80);
  }
  await assertStep(page,i);
}

test('How: entire fixed card fits while wheel alone activates 01→04→01, then exits',async({page})=>{
  test.setTimeout(90000);
  for(const [width,height] of [[1366,768],[1440,900],[1536,864],[1920,1080]]) {
    await setCssViewport(page,{width,height}); await open(page);
    const section=page.locator('#how-it-works'), panel=page.locator('.how-panel');
    await expect(section).toHaveCSS('padding-bottom','0px');
    await expect(panel).toHaveCSS('position','sticky');
    await page.mouse.move(width*.65,height*.5);
    let cardHeight=0;
    for(const i of [0,1,2,3,2,1,0]) {
      await wheelToStep(page,i);
      const geometry=await page.evaluate(()=>{
        const panel=document.querySelector('.how-panel')!, p=panel.getBoundingClientRect(),nav=document.querySelector('.marketing-navbar')!.getBoundingClientRect();
        const walker=document.createTreeWalker(panel,NodeFilter.SHOW_TEXT);let textClipped=false;
        while(walker.nextNode()){
          if(!walker.currentNode.textContent?.trim())continue;
          const range=document.createRange();range.selectNodeContents(walker.currentNode);
          for(const r of range.getClientRects())if(r.width&&r.height&&(r.top<p.top||r.bottom>p.bottom||r.left<p.left||r.right>p.right))textClipped=true;
        }
        return {height:p.height,top:p.top,bottom:p.bottom,left:p.left,right:p.right,viewport:innerHeight,navBottom:nav.bottom,
          textClipped,
          overflow:(panel as HTMLElement).scrollHeight>(panel as HTMLElement).clientHeight+1,
          clipped:[...panel.querySelectorAll('button,h2,.section-label,.how-visual svg,.how-visual figcaption p,.how-exit')].some(e=>{const r=e.getBoundingClientRect();return r.top<p.top||r.bottom>p.bottom||r.left<p.left||r.right>p.right;}),
          horizontal:document.documentElement.scrollWidth>Math.ceil(visualViewport?.width??innerWidth)};
      });
      cardHeight ||= geometry.height;
      expect(geometry.height).toBeCloseTo(cardHeight,1);
      expect(geometry.top).toBeGreaterThanOrEqual(geometry.navBottom+15);
      expect(geometry.bottom).toBeLessThanOrEqual(geometry.viewport-19);
      expect(geometry.left).toBeGreaterThanOrEqual(0);expect(geometry.right).toBeLessThanOrEqual(width+1);
      expect(geometry.overflow).toBe(false);expect(geometry.clipped).toBe(false);expect(geometry.horizontal).toBe(false);
      expect(geometry.textClipped).toBe(false);
      await expect(panel.locator('svg')).toHaveCount(1);
      await test.info().attach(`geometry-${width}-${i}`,{body:JSON.stringify(geometry),contentType:'application/json'});
      await page.screenshot({path:test.info().outputPath(`fitted-${width}-step-${i+1}.png`)});
    }
    for(const i of [1,2,3]) await wheelToStep(page,i);
    const y=await page.evaluate(()=>scrollY);await page.mouse.wheel(0,500);
    await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(y+300);
    await expect(page.locator('.persistent-scene')).toBeInViewport();
    const gap=await page.evaluate(()=>document.querySelector('.persistent-scene')!.getBoundingClientRect().top-document.querySelector('.how-panel')!.getBoundingClientRect().bottom);
    expect(gap).toBeGreaterThanOrEqual(0);expect(gap).toBeLessThanOrEqual(48);
    await page.screenshot({path:test.info().outputPath(`natural-scroll-${width}.png`)});
  }
});

test('How: every click and native keyboard activation changes the explanation and diagram',async({page})=>{
  await setCssViewport(page,{width:1366,height:768});
  await open(page);
  for(const [i,step] of collaborationSteps.entries()){
    const button=page.locator('.how-layout button').nth(i);await button.click();
    await expect(button).toHaveAttribute('aria-current','step');
    await expect(page.locator('.how-visual figcaption strong')).toHaveText(step.title);
    await expect(page.locator('.how-visual figcaption p').first()).toHaveText(step.text);
    await expect(page.locator('.how-visual svg title')).toHaveText(`${step.title}: protected collaboration`);
    await expect(page.locator('.how-output')).toHaveAttribute('opacity',i===3?'1':'0');
  }
  for(let i=0;i<4;i++){
    const button=page.locator('.how-layout button').nth(i);await button.focus();
    await page.keyboard.press(i%2?'Space':'Enter');
    await expect(page.locator('.how-visual')).toHaveAttribute('data-step',String(i));
    await expect(page.locator('.how-visual figcaption strong')).toHaveText(collaborationSteps[i].title);
  }
  await page.keyboard.press('Tab');
  expect(await page.locator('.how-layout').evaluate(e=>e.contains(document.activeElement))).toBe(false);
  const y=await page.evaluate(()=>scrollY);await page.keyboard.press('PageDown');
  await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(y+100);
  await page.getByRole('link',{name:'Continue to Technology →'}).click();
  await expect(page.locator('#persistent-title')).toBeInViewport();
});

test('How: reduced motion keeps natural scroll and selectable steps',async({page})=>{
  await setCssViewport(page,{width:1366,height:640});
  await page.emulateMedia({reducedMotion:'reduce'});await open(page);
  await expect(page.locator('.how-panel')).toHaveCSS('position','sticky');
  await page.locator('.how-layout button').nth(2).click();
  await expect(page.locator('.how-visual')).toHaveAttribute('data-step','2');
  const fitted=await page.locator('.how-panel').evaluate(e=>{const r=e.getBoundingClientRect(),n=document.querySelector('.marketing-navbar')!.getBoundingClientRect();return r.top>=n.bottom+15&&r.bottom<=innerHeight-19&&(e as HTMLElement).scrollHeight<=(e as HTMLElement).clientHeight+1;});
  expect(fitted).toBe(true);
  const y=await page.evaluate(()=>scrollY);await page.mouse.wheel(0,400);
  await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(y+200);
});

test('How: compact mobile has selectable details and natural document scroll',async({page})=>{
  test.setTimeout(60000);
  await setCssViewport(page,{width:390,height:844});await open(page);
  await expect(page.locator('.how-visual-sticky')).toHaveCSS('position','static');
  for(const i of [0,1,2,3,2,1,0]){await page.locator('.how-layout button').nth(i).click();await assertStep(page,i);}
  const y=await page.evaluate(()=>scrollY);await page.mouse.wheel(0,400);await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(y+100);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width??innerWidth))).toBe(true);
});

import {test,expect} from '@playwright/test';
import {setCssViewport} from './css-viewport';
test('production walkthrough has no seek API, suspends, resumes and holds scene 13',async({page},info)=>{
 test.setTimeout(120000);await setCssViewport(page,info.project.use.viewport!);
 await page.clock.install();await page.clock.pauseAt(new Date(await page.evaluate(()=>Date.now()+1000)));
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/demo');const film=page.locator('#product-walkthrough'),svg=film.locator('svg');await film.scrollIntoViewIfNeeded();
 expect(await page.evaluate(()=>window.kryptroomMovieReview)).toBeUndefined();
 await expect(film.locator('button,input,audio,video,[tabindex]')).toHaveCount(0);
 if((info.project.use.viewport?.width??1440)<=700){await expect(film.locator('.cinematic-static')).toBeVisible();await expect(svg).toBeHidden();return;}
 await expect(film).toHaveAttribute('data-running','true');const surface=await svg.elementHandle();
 await page.clock.runFor(1200);expect(Number(await svg.getAttribute('data-time'))).toBeGreaterThan(900);
 await page.evaluate(()=>scrollTo(0,0));await expect(film).toHaveAttribute('data-running','false');
 const paused=await svg.getAttribute('data-time');await page.clock.runFor(10000);await expect(svg).toHaveAttribute('data-time',paused!);
 await film.scrollIntoViewIfNeeded();await expect(film).toHaveAttribute('data-running','true');
 await page.clock.runFor(100000);await expect(svg).toHaveAttribute('data-time','92400');await expect(film).toHaveAttribute('data-running','false');
 await page.clock.runFor(10000);await expect(svg).toHaveAttribute('data-time','92400');
 expect(await surface!.evaluate(e=>e===document.querySelector('#product-walkthrough svg'))).toBe(true);
 expect((await film.locator('[data-movie-paint]>text:not([display="none"])').allTextContents()).filter(t=>t==='Review action')).toHaveLength(3);
 expect(errors).toEqual([]);
});

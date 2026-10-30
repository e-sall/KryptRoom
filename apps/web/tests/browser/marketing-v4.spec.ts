import {test,expect} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {setCssViewport} from "./css-viewport";
const routes=["product","technology","security","solutions-manufacturing","solutions-healthcare","solutions-finance","solutions-research","book-demo"];
test("V4 left brand, Solutions keyboard disclosure, exact destinations and honest routes",async({page},info)=>{
 test.setTimeout(120000);await setCssViewport(page,info.project.use.viewport!);await page.goto("/");
 const nav=page.locator(".marketing-navbar");
 const boxes=await nav.locator(":scope > .brand, :scope > nav").evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));
 expect(boxes[0].left).toBeLessThanOrEqual(boxes[1].left+1);
 const summary=nav.locator("summary");await summary.focus();await page.keyboard.press("Enter");
 await expect(nav.locator("details")).toHaveAttribute("open","");
 const menu=nav.locator(".solutions-menu");await expect(menu.getByRole("link")).toHaveCount(4);
 expect(await menu.evaluate(e=>e.getBoundingClientRect().right<=innerWidth)).toBe(true);
 await page.keyboard.press("Tab");await expect(menu.getByRole("link").first()).toBeFocused();await page.keyboard.press("Escape");await expect(summary).toBeFocused();await expect(nav.locator("details")).not.toHaveAttribute("open","");
 await expect(page.locator(".hero-disclaimer")).toHaveCount(0);
 await expect(page.locator(".hero").getByRole("link",{name:"See how it works"})).toHaveAttribute("href","/#how-it-works");
 await expect(page.getByRole("link",{name:"Elimane Sall on LinkedIn"})).toHaveAttribute("href","https://www.linkedin.com/in/elimane-sall-523720349/");
 await expect(page.locator(".home-final-cta .button")).toHaveCount(1);
 for(const route of routes){await page.goto('/'+route);await page.evaluate(()=>document.fonts.ready);expect(await page.locator("main").innerText()).not.toContain("—");expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width??innerWidth))).toBe(true);expect((await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa","wcag22aa"]).analyze()).violations).toEqual([]);}
 await page.goto("/product");
 const cards=await page.locator(".product-state-story .showcase-state").evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));
 expect(cards).toHaveLength(4);for(let i=0;i<cards.length;i++)for(let j=i+1;j<cards.length;j++){const a=cards[i],b=cards[j];expect(a.right<=b.left||b.right<=a.left||a.bottom<=b.top||b.bottom<=a.top).toBe(true);}
 expect(await page.locator(".product-state-story .showcase-dag path").first().evaluate(e=>getComputedStyle(e).fill)).toBe("none");
 await page.goto("/book-demo");await expect(page.getByRole("heading",{name:"Coming soon",exact:true})).toBeVisible();await expect(page.getByRole("link",{name:"Contact the Founder"})).toHaveAttribute("href","mailto:elimanesall.eng@gmail.com?subject=KryptRoom%20-%20Demo%20Inquiry");await expect(page.locator("form,input,iframe")).toHaveCount(0);
});
test("V4 typography, real choreography, portrait DPR and founder alignment",async({page,browser},info)=>{
 await page.goto("/");await page.evaluate(()=>document.fonts.ready);
 expect(await page.locator("h1").evaluate(e=>getComputedStyle(e).fontFamily)).toContain("KR Newsreader");
 const show=page.locator(".home-showcase");await show.scrollIntoViewIfNeeded();await expect(show).toHaveAttribute("data-running","true");
 await expect(show.locator(".showcase-film")).toHaveAttribute("data-act","0");
 expect(await show.locator(".showcase-film").textContent()).toBe("");
 const running=await show.locator(".film-packets i").first().evaluate(e=>getComputedStyle(e).animationPlayState);expect(running).toBe("running");
 await show.getByRole("button",{name:"Pause demo"}).click();expect(await show.locator(".film-packets i").first().evaluate(e=>getComputedStyle(e).animationPlayState)).toBe("paused");
 await page.emulateMedia({reducedMotion:"reduce"});expect(await show.locator(".film-packets i").first().evaluate(e=>getComputedStyle(e).animationName)).toBe("none");
 if(info.project.name==="desktop") {const rects=await page.locator(".founder-profile picture, .founder-profile > div").evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));expect(Math.abs((rects[0].top+rects[0].bottom)/2-(rects[1].top+rects[1].bottom)/2)).toBeLessThan(2);}
 const ctx=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:2});const dpr=await ctx.newPage();await dpr.goto("http://127.0.0.1:3000/");const portrait=dpr.getByAltText("Elimane Sall, founder of KryptRoom");await portrait.scrollIntoViewIfNeeded();await portrait.evaluate(async e=>(e as HTMLImageElement).decode());
 const measured=await portrait.evaluate(e=>({source:(e as HTMLImageElement).currentSrc,width:e.getBoundingClientRect().width,dpr:devicePixelRatio}));expect(measured.source).toMatch(/-(768|1200)\.webp$/);expect(measured.dpr).toBe(2);await ctx.close();
});

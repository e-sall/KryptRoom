"use client";
import { useEffect } from "react";

/** Complete native focus scrolling where a fixed bar or browser rounding obscures it. */
export function FocusVisibility() {
  useEffect(() => {
    let frame = 0;
    let keyboardNavigation = true;
    const pointerInput = () => { keyboardNavigation = false; cancelAnimationFrame(frame); };
    const keyboardInput = () => { keyboardNavigation = true; };
    const keepVisible = (event: FocusEvent) => {
      const target = event.target;
      if (!keyboardNavigation || !(target instanceof HTMLElement) || !target.matches("a,button,input,select,textarea,summary,[tabindex='0']")) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        if (!target.isConnected || document.activeElement !== target) return;
        const modal = target.closest("dialog[open]");
        if (modal) { target.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "instant" }); return; }
        const header = document.querySelector<HTMLElement>(".marketing-navbar");
        const nav = document.querySelector<HTMLElement>(".mobile-bottom-nav");
        const top = header && !header.contains(target) ? Math.max(0, header.getBoundingClientRect().bottom) + 8 : 8;
        const bottom = nav && nav.getClientRects().length && !nav.contains(target) ? nav.getBoundingClientRect().top - 8 : innerHeight - 8;
        const rect = target.getBoundingClientRect();
        if (rect.top < top) window.scrollBy({ top: rect.top - top, behavior: "instant" });
        else if (rect.bottom > bottom) window.scrollBy({ top: rect.bottom - bottom, behavior: "instant" });
      });
    };
    document.addEventListener("focusin", keepVisible);
    document.addEventListener("pointerdown", pointerInput, true);
    document.addEventListener("keydown", keyboardInput, true);
    return () => {
      cancelAnimationFrame(frame); document.removeEventListener("focusin", keepVisible);
      document.removeEventListener("pointerdown", pointerInput, true); document.removeEventListener("keydown", keyboardInput, true);
    };
  }, []);
  return null;
}

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CinematicShowcase } from "../src/features/marketing/cinematic/cinematic-showcase";
import { duration, offsets, position } from "../src/features/marketing/cinematic/timeline";
import artwork from "../src/features/marketing/cinematic/artwork.json";

describe("cinematic preview boundary", () => {
  it("has an honest readable fallback without browser animation APIs or operational controls", () => {
    const {container}=render(<CinematicShowcase/>);
    expect(screen.getByText("Concept preview · Synthetic data")).toBeVisible();
    expect(screen.getByText("6 production · 4 transit · 2 other.")).toBeVisible();
    expect(screen.getByText(/No action assigned, approved or executed/)).toBeVisible();
    expect(container.querySelectorAll("button,input,a,audio,iframe")).toHaveLength(0);
    expect(container.querySelectorAll("svg")).toHaveLength(1);
  });
  it("keeps boundary navigation deterministic and holds the unapproved ending", () => {
    expect(position(-100)).toEqual({index:0,local:0});
    offsets.slice(1).forEach((at,i)=>{
      expect(position(at-1).index).toBe(i);
      expect(position(at)).toEqual({index:i+1,local:0});
    });
    expect(position(duration+10000)).toEqual({index:11,local:7600});
  });
  it("imports only audited SVG primitives, without executable markup or external references", () => {
    type Node={tag:string;attrs:Record<string,string|undefined>;children:Node[]};
    const allowed=new Set(["svg","g","text","rect","path","circle","ellipse","defs","filter","feGaussianBlur","linearGradient","stop"]);
    function check(n:Node){
      expect(allowed.has(n.tag)).toBe(true);
      for(const [name,value]of Object.entries(n.attrs)){
        expect(name).not.toMatch(/^(on|href|style|tabindex)/i);
        if(value)expect(value).not.toMatch(/javascript:|https?:\/\//i);
      }
      n.children.forEach(check);
    }
    (artwork as unknown as Node[]).forEach(check);
  });
});

import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import Home from "../src/app/page";
import { MarketingContent } from "../src/features/marketing/marketing-pages";
import { solutions } from "../src/features/marketing/solutions";

describe("marketing V4 founder direction", () => {
 it("keeps the left brand, exact navigation and one final CTA",()=>{
  const {container}=render(<Home />);
  expect(container.querySelector(".marketing-navbar")?.firstElementChild).toHaveClass("brand");
  expect([...container.querySelectorAll(".marketing-navbar nav > a")].map(a=>a.textContent)).toEqual(["Product","Technology"]);
  expect(container.querySelectorAll(".solutions-menu a")).toHaveLength(4);
  expect(container.querySelectorAll(".hero .button")).toHaveLength(2);
  expect(container.querySelectorAll(".home-final-cta .button")).toHaveLength(1);
  expect(screen.getByRole("link",{name:"Elimane Sall on LinkedIn"})).toHaveAttribute("href","https://www.linkedin.com/in/elimane-sall-523720349/");
  expect(container.textContent).not.toContain("—");
 });
 it.each(solutions)("describes $name as a synthetic proposed use",s=>{
  const {container}=render(<MarketingContent section={s.slug}/>);
  for(const value of [s.problem,s.participants,s.sensitive,s.workflow,s.output]) expect(container).toHaveTextContent(value);
  expect(container).toHaveTextContent("not a customer");expect(container.textContent).not.toContain("—");
 });
 it("keeps eight precise technology sections and planned quantum status",()=>{
  const {container}=render(<MarketingContent section="technology"/>);
  expect(container.querySelectorAll(".editorial-rows > section")).toHaveLength(8);
  for(const text of ["Planned R&D","not threshold FHE","not MPC arithmetic","semi-honest","Layer B","Layer C"]) expect(container).toHaveTextContent(text);
  expect(container.textContent).not.toContain("—");
 });
});

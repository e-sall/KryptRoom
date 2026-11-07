import { describe, expect, it, vi } from "vitest";
vi.mock("server-only", () => ({})); // Only Next's build marker; real Node crypto runs below.
import { csrfValid, digest, equal, opaque, proxyPath, returnPath, seal, unseal } from "../src/server/auth/security";

const key = Buffer.alloc(32, 1);
describe("PR2 BFF boundaries", () => {
  it("uses independent opaque handles and keyed lookup values", () => {
    const a = opaque(), b = opaque();
    expect(a).toMatch(/^[A-Za-z0-9_-]{43}$/); expect(a).not.toBe(b);
    expect(digest(key,a)).toHaveLength(64); expect(digest(key,a)).not.toBe(a);
    expect(digest(Buffer.alloc(32,2),a)).not.toBe(digest(key,a));
    expect(equal(a,a)).toBe(true); expect(equal(a,b)).toBe(false); expect(equal(a,a+"x")).toBe(false);
  });
  it("authenticates persisted tokens, purpose, key ID and random nonce", () => {
    const a = seal(key,"test-v1","access:session-one","synthetic-access-value");
    expect(a).not.toContain("synthetic-access-value");
    expect(unseal(key,"test-v1","access:session-one",a)).toBe("synthetic-access-value");
    expect(seal(key,"test-v1","access:session-one","synthetic-access-value")).not.toBe(a);
    for (const [k,id,purpose,value] of [
      [Buffer.alloc(32,2),"test-v1","access:session-one",a],
      [key,"test-v2","access:session-one",a],
      [key,"test-v1","refresh:session-one",a],
      [key,"test-v1","access:session-two",a],
      [key,"test-v1","access:session-one",a.slice(0,-3)+"AAA"],
    ] as const) expect(() => unseal(k,id,purpose,value)).toThrow();
  });
  it.each([null,"https://evil.test","//evil.test","/\\evil.test","/%2fexample.test","/%5cevil.test","/%0aevil.test","/%invalid"])("rejects unsafe return path %s", value => {
    expect(returnPath(value)).toBe("/bff/api/v1/me");
  });
  it("permits ordinary internal navigation", () => {
    expect(returnPath("/app/rooms?view=list")).toBe("/app/rooms?view=list");
  });
  it("allowlists exact backend routes and methods", () => {
    const oid = "019a0000-0000-7000-8000-000000000010";
    expect(proxyPath(["organizations",oid,"members"],"GET")).toBe(`/api/v1/organizations/${oid}/members`);
    expect(proxyPath(["organizations",oid,"members"],"POST")).toBeNull();
    for (const path of [["run"],["auth","complete"],["https:","evil.test"],["organizations",".."],["organizations%2f"]])
      expect(proxyPath(path,"POST")).toBeNull();
  });
  it("requires all CSRF controls together", () => {
    const headers = new Headers({Origin:"http://127.0.0.1:3004","X-CSRF-Token":"bound-token",
      "Sec-Fetch-Site":"same-origin","Content-Type":"application/json"});
    expect(csrfValid(headers,"http://127.0.0.1:3004","bound-token")).toBe(true);
    for (const name of ["Origin","X-CSRF-Token","Sec-Fetch-Site","Content-Type"]) {
      const bad = new Headers(headers); bad.delete(name);
      expect(csrfValid(bad,"http://127.0.0.1:3004","bound-token")).toBe(false);
    }
    for (const site of ["cross-site","same-site"]) {
      const bad = new Headers(headers); bad.set("Sec-Fetch-Site",site);
      expect(csrfValid(bad,"http://127.0.0.1:3004","bound-token")).toBe(false);
    }
  });
});

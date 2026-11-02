# PR20 update draft — publish only with the approved head

Proposed title: **M8 PR7 — Final Signal homepage and Product Walkthrough**

The homepage uses the founder's canonical The Signal V4 SVG and synchronized
eight-second CSS animations. The preserved 92.4-second film now supplements the
technical `/demo` experience, with the pointer scaled to 50% around its original
hotspot. The locked 600px How card and final walkthrough CTA alignment are retained.
All data remain synthetic; no crypto, AI or chain service is invoked.

Local validation: 116 unit/component passes; complete Chromium suite 205 passes
and two inherited exclusions; final WebKit surface checks and exact-candidate
promotion validation are recorded in KRYPTROOM-M8-MAIN-RELEASE-READINESS.md.
No new hosted CI success is claimed until the actual published SHA has completed.

**BLOCKED for publication/merge:** M8-SEC-001 expired November 1 at 23:59 Toronto.
M8-SEC-002 remains independent through November 4 at 02:00:41 Toronto, excludes
merge/production and does not renew ESLint approval. Full audit remains 16
moderate findings from one minimatch advisory, production zero; not a fix or
proof of inexploitability. No forced dependency change or weakened controls.

After the security gate is dispositioned, replace this draft's status and evidence
with the actual pushed head and its checks. Keep PR20 open until explicit founder
merge approval. No main merge, deployment, tag or M9 authorization.

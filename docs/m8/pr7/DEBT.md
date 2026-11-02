# M8 freeze candidate — risk, exception and deferred work

Owner for repository decisions: founder / maintainer e-sall. This inventory does
not extend any security approval or start M9.

- **Accepted, time-bounded — M8-SEC-001:** ESLint 9 EOL in development tooling
  only. Founder renewal expires **2026-11-01 23:59 America/Toronto**, reevaluate
  before PR7 merge or expiry. New material risk stops work. Exit is a separately
  reviewed compatible supported configuration with full tests/audits. Bounded
  read-only monitoring is active; no automatic renewal. See current exception
  and Phase 0 report. The withdrawn GHSA portion is closed, not a patched package.
- **Required for merge — governance/design:** independent review of final PR7
  head, actual screenshots and new marketing direction; security reevaluation
  and explicit founder approval. Green checks alone cannot close M8 or merge it.
- **Bounded QA limitation — accessibility:** Axe/keyboard/reflow/motion coverage
  is not WCAG certification. No NVDA, VoiceOver or TalkBack session was performed.
  Manual assistive-technology, browser toolbar zoom and physical device testing
  remain to be reviewed; 200% reflow is simulated with CSS viewport dimensions.
- **Bounded QA limitation — browsers:** Windows Playwright engines are not actual
  Safari/iOS/Android hardware certification. CI remains Chromium; optional local
  Firefox/WebKit scope and actual outcomes are in the Freeze QA report.
- **Accepted frontend performance tradeoff:** automatic Next Link prefetching is
  disabled for M8 links after WebKit speculative-preload errors. Explicit navigation
  is tested and preserved; first activation may load the route. Reevaluate on a
  supported framework/browser setup before future operational deployment.
- **Deferred operational integration:** authenticated Room APIs, Control Plane,
  KryptNode linkage/orchestration, production identity/key lifecycle/KMS, durable
  service events, field-scoped authorization/reveal, evidence APIs and genuine
  verifier/anchor status adapters. The preview grants none of those capabilities.
- **Deferred booking:** no provider, slots, form, submission or confirmation.
  Contact wording links only to the real project repository.
- **Deferred deployment review:** no production release or hosting approved.
  TLS/CSP/nonces, authentication and full operational security need a separate
  review; the founder's tooling exception is not deployment authorization.
- **Retained core limits:** two-party semi-honest/trusted hosts, bounded numeric
  fixtures and operations, local keys rather than production KMS, no general
  malicious security/rollback protection, bounded metadata proof rather than
  proof of all MPC arithmetic, one historical state-only testnet anchor. See
  unchanged core documentation; this frontend performs no new validation of them.
- **Source fidelity:** source-derived P11/P05 reference conversions do not certify
  recovered original interactions or pixel-perfect typography. Homepage direction
  is the later founder-approved brief; no Clean proprietary assets are included.
- **Existing repository governance:** no license was added. Private reporting
  channel availability is still a repository-settings question; unchanged
  SECURITY.md explains the safe reporting route without asserting it is enabled.

No ML expansion, quantum implementation, new crypto operation, blockchain
transaction, Groth16 run, live backend, production deployment or M9 is included.

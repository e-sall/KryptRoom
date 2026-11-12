# PR6 security disposition — no exception granted

Fresh official metadata/audits: 2026-11-11/12 UTC; raw JSON, commands, exits and
scanner DB metadata are in the handoff. Root full/production: 0/0; frontend:
8 moderate/0; locked Python runtime/development: 0/0. Those results do not cover
OS packages or prove non-exploitability. Application lockfiles are unchanged.

Installed minimatch 3.1.5/10.2.6 and Next's compiled nft tracing/build copy remain
unresolved. Eight findings propagate one advisory across dependency paths. No
visitor-controlled path was demonstrated; this is not proof of inexploitability.
Untrusted glob/build inputs must not be introduced. Official React 7.37.5/import
2.32.0/JSX-a11y 6.10.2 peers still exclude ESLint 10. Isolated strict resolution
of ESLint 10.14.0 plus Next/config 16.4.6 fails ERESOLVE. Existing rules retained;
no major override, force, legacy-peer-deps or renewed exception. Latest minimatch
11.0.8 covers both advisories but is not declared compatible with consumers of 10.
The new GHSA-cf2h-pxjq-68xw affects 11.0.0–11.0.6: 11.0.1 alone is insufficient.

## Image inventory and actual remediation

Official Trivy 0.76.2 pinned by digest; scanner has no Docker socket, credentials
or source. Current DB, complete image tar, offline full OS/language inventory,
all severities and unfixed entries visible. No ignores/exclusions.

- API baseline: 358 occurrences, 100 HIGH/CRITICAL. Final: 350, 98 HIGH/CRITICAL.
  Removed: apt/libapt two HIGH; unused pip five MEDIUM and one LOW.
- BFF baseline: 242, 45 HIGH/CRITICAL. Final: 219, 35 HIGH/CRITICAL.
  Removed: unused global npm tooling 10 HIGH, 12 MEDIUM, one LOW.
- Node security patch also addresses officially reported HTTP2/TLS issues; a
  package inventory alone does not certify every embedded Node library.
  The standalone BFF scan detects OS inventory after npm removal; it does not
  establish exhaustive CVE coverage of bundled JavaScript. The separate production
  lock audit remains necessary and is zero, not a proof of complete runtime safety.
- An isolated pip 26.3 candidate exposed a HIGH setuptools entry through its
  bundled SBOM; rejected, not accepted. Final runtime has no pip. Build/test
  installer remains an inherited risk, distinct from locked application audits.
- Critical residual examples: API libsqlite3 CVE-2025-7458 and zlib
  CVE-2023-45853; BFF zlib CVE-2023-45853. Vendor affected/will_not_fix/no fixed
  package is not risk acceptance. No unreviewed major OS migration was applied.
- PostgreSQL/Keycloak image inventories NOT RUN locally; required in prepared CI.
  Test/browser/build images are not certified clean. A maintained base migration
  needs compatibility evidence and fresh exact-image scans before release.

All old exceptions remain unused. Current settings are local/test only. Fixture
secrets, loopback IdP and local HTTP BFF are not production configuration. Separate
production design must cover secret distribution/rotation, least-privilege DB,
TLS, Secure cookies and IdP. Logical restore PASS does not validate PITR, encrypted
off-host retention, key recovery or timed whole-service recovery. No new risk
acceptance, publication, merge or deployment is implied.

Sources: [ESLint support](https://eslint.org/version-support/),
[original advisory](https://github.com/isaacs/minimatch/security/advisories/GHSA-g3hv-75wg-m249),
[11.x regression](https://github.com/isaacs/minimatch/security/advisories/GHSA-cf2h-pxjq-68xw),
[Node security release](https://nodejs.org/en/blog/release/v22.23.5).

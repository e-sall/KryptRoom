# Security disposition proposal — NOT APPROVED

Owner and approval authority: founder / repository maintainer e-sall.

## Current blockers

M8-SEC-001 expired on **2026-11-01 at 23:59 America/Toronto**
(`2026-11-02T04:59Z`). It covered ESLint 9 EOL only. Push and a new ESLint 9
execution remain blocked. The final successful lint was run before expiry;
subsequent browser-test maintenance has TypeScript/browser validation but no
fresh lint on the final commit. No renewal or suppression was performed.

The [official ESLint support policy](https://eslint.org/version-support/) still
lists v9 as EOL and v10 as current. Read-only official npm metadata reports
eslint 10.14.0 and eslint-config-next 16.4.3, but eslint-plugin-react 7.37.5,
jsx-a11y 6.10.2 and import 2.32.0 still exclude ESLint 10 in their peers.
React hooks 7.1.1 accepts it; that alone does not make the complete chain compatible.
No packages were installed or overrides forced.

The [minimatch advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249) remains
moderate, with <11.0.1 affected and 11.0.1 patched. Current full audit: 16 moderate
propagated findings from that one advisory; production audit: zero. The recorded
3.1.5/10.2.6 dependency paths and embedded Next tracing mechanism remain unresolved.
No visitor-controlled glob path has been demonstrated; absence of such a path
and a zero production audit do not prove inexploitability.

M8-SEC-002 remains temporary until **2026-11-04 02:00:41 America/Toronto**
(`07:00:41Z`), with trusted development/build inputs only; it explicitly does not
cover merge or production. This mission authorizes release preparation and a
conditional push, not an implicit extension of either deadline or merge scope.

## Options requiring founder decision

- Preferred exit: validate a supported compatible lint chain and a complete
  minimatch/tracing remediation in a separate bounded dependency change, with
  pinned reproducible install and unchanged audits/tests. A blind major override
  or npm audit fix --force is not an acceptable substitute.
- If release preparation must continue first: explicitly approve a short renewed
  M8-SEC-001 window limited to the same dev/CI tooling, recording receipt, owner,
  expiry and exit criteria. Suggested maximum for this next review window:
  November 3 at 23:59 Toronto, before the existing M8-SEC-002 expiry. This is a
  proposal, not risk acceptance or a new expiration in force.
- If minimatch is still unresolved at merge time: explicitly disposition the
  proposed code-only dev/main merges, with no production deployment, trusted
  inputs and no extension beyond M8-SEC-002's existing deadline unless separately
  approved. Its current wording cannot silently grant that scope.

All existing CI permissions, audits, isolation, tests and manual confirmation
guards remain intact. No new material advisory was found in the refreshed audit.
No live proving, chain transaction, merge or deployment occurred.

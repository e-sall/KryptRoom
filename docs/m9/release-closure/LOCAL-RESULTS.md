# M9 release closure — local only

Base: approved PR6 `66ac0dfa40ea8303f31ab49629a6278862bb28c4`.
Branch `codex/m9-release-closure`. Ready for targeted local QA; publication NO-GO.

## Corrections and root causes

Debian12 OS libraries/utilities account for repeated runtime findings. Official
digest-pinned Alpine3.23 bases retain Python3.12.16 and Node22.23.5. Exact stable
krb5-libs1.22.3-r0 and zlib1.4-r0 fix remaining Alpine findings. Changing base also
removes affected components rather than patching every Debian package. Runtime
installers remain removed as in PR6. Browser acceptance strictly installs the same
npm lock on glibc instead of copying incompatible musl native modules.
No application source/dependency/lock, migration, Core or marketing change.

Secret/bootstrap negatives use the actual running PostgreSQL immutable image ID.
Restore permits this named disposable fixture, preserving explicit acknowledgement,
fixed *_test databases and arbitrary-container refusal; five new negative tests.
Artifact verification also handles the actual Keycloak OCI index -> selected
platform manifest -> scanned config chain. Digests, sizes and platform uniqueness
are checked; missing/ambiguous/tampered/wrong-config bindings refuse. This fixes an
observed archive/config mismatch without treating an index ID as a config ID.

## Scans

Pinned Trivy0.76.2, same recorded database/cache for before/after, OS and language
inventories, all severities and unfixed findings; exit1 on any vulnerability.
No exclusions/threshold reduction. Flat handoff contains full raw reports and a
per-CVE/component/exposure/fix/decision inventory. Unknown reachability is not safety.

- API: 96 HIGH + 2 CRITICAL, 31 unique H/C CVEs -> zero findings.
- BFF: 34 HIGH + 1 CRITICAL, 11 unique H/C CVEs -> zero findings.
- PostgreSQL original: 133 HIGH + 4 CRITICAL, 66 unique H/C CVEs.
- PostgreSQL candidate: 131 HIGH + 4 CRITICAL, 65 unique H/C CVEs.
- Keycloak unchanged: six HIGH, six unique H/C CVEs; 81 all-severity findings.

Both second-build runtime scans also zero. This measures known findings, not all
embedded-code risks/exploitability. PG residuals group into Debian utilities/
libraries and gosu embedded Go. Inspected gosu1.20 still uses Go1.24.6: no benefit,
not retained. Trixie experiments retained more findings. Keycloak needs supported
OS/JDK/Guava fixes; no manual JAR swap. Missing FixedVersion is not accepted risk.

PG17.12 arrived during this work with vendor fixes ahead of scanner coverage,
including RLS-related CVE-2026-120154. Local candidate upgrades signed PGDG server/
client/libpq and apt, keeping major17, glibc/locale/volume. No GIN/GiST/bpchar app
indexes found for migration caveats; this does not qualify all Keycloak/production
indexes/extensions/backups. Official17.12 bookworm/trixie/alpine3.23 tags returned404.
Default immutable Compose/CI pins unchanged; new release minimum >=17.12 and <18
intentionally blocks default17.11 until reviewed immutable artifact adoption.
Candidate is local only and still has unresolved vulnerabilities.

## Executed local validation

- Two fresh native Linux contexts, API/BFF --no-cache runtime builds, strict clean
  installs and production Next builds PASS. A/B package inventories equal; same
  host, not bit-identical artifacts or independent-host reproducibility.
- Real full Compose: PG17.12, TLS Keycloak, migrations, source-free standalone API/
  BFF, readiness PASS. UID10001/read-only/cap-drop preserved. Data/history table
  fingerprints, roles/SCRAM, RLS/functions/owners/ACL equal across upgrades and A->B.
- 109 Python unit +39 real PG tests PASS; guarded downgrade/history seed and actual
  logical restore PASS with data/security preservation. Ruff/format, mypy28,
  lock exports and wheel/sdist build PASS.
- Alpine lint/types/153 frontend tests PASS; separate glibc acceptance lint/types/
  153 tests also passed. 73 CI/gate/classification tests, 15 YAML parses, Actionlint
  PASS; optional Actionlint ShellCheck/pyflakes integrations absent, NOT RUN.
- Three real Edge/Chromium scenarios PASS on baseline, new A and fresh B: real
  OIDC/PKCE, Rooms Save/reopen/ETag/conflicts, interorganization denial,
  invitations/revocation, API/IdP recovery and session expiry. No response mocks.
  First final-A attempt timed out in two cases; A rerun and B passed without
  product edits. Cause not proven; overwritten first raw log unavailable. This
  does not establish a zero-flake suite.
- migrate/API/tests secret access, foreign UID refusal, five source +six native PG
  invalid-secret cases PASS; invalid bootstrap leaves zero app roles. Runtime logs
  and36 client files checked against synthetic secrets and74 real encrypted-session
  tokens: no leak found. Bounded fixture evidence, not a general DLP guarantee.

Initial harness issues (metadata mounts, host-loopback bridge, writable test HOME,
private fixture access) were corrected outside product code. Restore correctly
refused missing-history test data before a real history seed. Guards remain active.

## Dependency and release gates

Root full/production and Python runtime/dev audits zero. Frontend npm10.9.10:
eight MODERATE, production zero. Minimatch3.1.5/10.2.6 and Next/nft remain affected;
production audit zero does not exclude tracing/build exposure. ESLint9 EOL remains.
Strict ESLint10/official Next/React/import/JSX-a11y resolution returns ERESOLVE;
complete compatible remediation not proven. No forced peers, overrides or locks.
Strict gates reject findings/missing/invalid/expired evidence. No exception renewed
or reused; local diagnostic results do not authorize hosted frontend publication.

Publication NO-GO: PG/Keycloak CVEs, PG default artifact adoption, npm/ESLint,
independent GitHub enforcement and exact-SHA hosted CI. Production secrets,
secure-cookie deployment, production restore/PITR, HA/load testing NOT VALIDATED.
No crypto/Groth16/blockchain/RoomState/hosted run. Core Freeze, prior functional
contracts/migrations, /demo, Signal and pre-existing work preserved. No push/merge/
deployment. Next action: QA04 exact delta/evidence, then separate Founder decisions.

Primary references inspected2026-11-12:
- https://alpinelinux.org/releases/
- https://security.alpinelinux.org/vuln/CVE-2026-4738
- https://www.postgresql.org/docs/17/release-17-12.html
- https://www.postgresql.org/support/security/17/
- https://eslint.org/version-support/
- https://www.keycloak.org/downloads

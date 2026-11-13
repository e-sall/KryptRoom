# M9 PR7 — final local security remediation

Base approved `5363d68cf1ab82d06a352870396e0bbb9007b40d`.
Branch `codex/m9-pr7-security`; no publication or hosted execution authorized.

## Implemented

The existing local PostgreSQL17.12 recipe now builds unmodified gosu1.20 source
commit `29b939aa5bd4dc588af765b8248f6e39150d2565` with official digest-pinned
Go1.27.4. Verify archive SHA256 before compilation; Go's upstream go.sum and
`-mod=readonly`, `GOTOOLCHAIN=local`, `CGO_ENABLED=0`, `-trimpath` retain dependency
and platform control. This is a local rebuild, not the maintainer-signed release
binary. No new privilege algorithm. No `-s` flag removing symbol visibility.

Signed Debian12 SASL2 packages2.1.28+dfsg-10+deb12u1 upgrade both installed SASL
packages; no required dependency removed. Server/client17.12 and libpq pins remain.
The tested final local image ID is
`sha256:ca43ed0e0defbd6c0328e100eb600cf7d56bda3625e69f4f1944ed9666b4acec`.
No tag is substituted into Compose/CI defaults. Official17.12 bookworm/trixie/
alpine3.23 tags returned404 at inspection. A local ID is immutable on this host,
not a published artifact transferable to clean hosted runners. Default17.11 remains
blocked by the >=17.12 release minimum until reviewed artifact adoption.

New controller requires an immutable ID before invoking Docker and tests actual
UID/supplementary groups, invalid user, nonroot elevation denial, unprivileged PID1
and explicit SIGTERM. PostgreSQL declares SIGINT as its default stop signal;
the first controller test mistakenly expected TERM from docker stop. That harness
assumption was corrected, with the first failure preserved. Actual PostgreSQL
restart/shutdown and persistence are exercised separately by Compose/browser tests.
The legacy builder also rejected COPY --chmod; explicit chmod after ordinary COPY
and a portable pre-extraction SHA256 check replace BuildKit-only assumptions.

## Scans and remaining causes

Pinned Trivy0.76.2, full OS/language inventories, all severities including unfixed,
same current DB (updated2026-11-12) before/after. No excludes or threshold changes.

- PostgreSQL candidate: 131HIGH+4CRITICAL,65unique H/C ->106HIGH+3CRITICAL,
  39unique H/C; all-severity findings548 ->485. Go-related binary findings are
  removed by the rebuild. This is not proof that every original Go CVE was reachable.
- Keycloak26.8.2: six HIGH/six unique H/C unchanged (81 all-severity findings).
- Approved immutable API/BFF images unchanged, freshly rescanned: zero findings
  each, matching approved closure. No redundant application rebuild/QA reopening.

Per-CVE inventory in the flat handoff retains component, version, status, exposure,
available fix/unknown and required decision for every remaining H/C occurrence.
No compatible newer backport was found in the selected Debian repositories for
remaining SQLite/libxml2/Kerberos/utilities. Changing distro or transplanting shared
libraries needs broader compatibility qualification; no unsupported mix adopted.
Debian documents a source-versus-built-component issue for zlib CVE-2023-45853;
retain the raw scanner flag and gate failure rather than applying an ignore.

Keycloak official latest remains26.8.2. UBI query confirms SQLite3.34.1-11.el9_8
and Java21.0.13.0.9-1.2.el9 still current in that channel. Four SQLite findings
remain. Guava33.7.2 fixes its reported issue, but no supported parent distribution
containing it was found: a JAR transplant could invalidate Quarkus dependency/
augmentation assumptions. A qualified upstream-parent rebuild/update is required;
no claim that such a remediation is globally impossible.

For CVE-2026-91403, Red Hat directs RHEL Java users to system CA updates and warns
that the initial Java-only distrust was insufficient. The image already carries
ca-certificates2026.2.92_v9.0.319-90.3.el9_8 (same as current UBI). Actual default
Java cacerts inspection parses118 public certificates: the two root subjects
named by the vendor are absent. No roots removed ad hoc. This is bounded store
evidence, not proof about overridden stores/all TLS paths, and the HIGH scanner
finding is NOT excluded/relabelled. A local certificate-parser deprecation warning
is retained in evidence; it does not establish Java chain-validation behavior.

Fresh npm10.9.10 audits: frontend8MODERATE, production0; root full/production0.
Current official Next/React/import/JSX-a11y peers still cap ESLint9; a strict
ESLint10.14.0 candidate returns ERESOLVE. Minimatch11.0.8 exists, but no compatible
backport for installed3.1.5/10.2.6 or complete supported Next/nft chain was found.
No forced peers, override, dependency removal or lock edits. Findings/EOL remain
OPEN and strict hosted gates blocked. Python runtime/dev hash-lock audits return0.

## Executed acceptance and limits

Real native Linux Compose uses immutable images, PG17.12, TLS Keycloak, standalone
API/BFF and restricted secrets. Before/after volume fingerprints compare actual
Room/history data, RLS, role/SCRAM flags and function definitions/owners/ACLs: equal.
39 real PostgreSQL tests pass, covering migration/security/concurrency/history.
Four new negative image-selection tests pass; native privilege-helper acceptance
passes. migrate/API/tests access and foreign UID rejection pass; five secret-source
negatives plus six native bootstrap negatives create zero app roles on failure.
Ruff/format, mypy28, wheel/sdist packaging and73 CI/gate/classification tests pass.

Three existing real Edge/Chromium scenarios pass on the approved baseline and
six observed post-upgrade replays pass. Assertions, retries0 and15s navigation/
action limits unchanged. External instrumentation records status/routes/durations,
not bodies/headers/query strings/tokens. No page JS errors or failed page requests
in these replays. The previous two timeouts are NOT reproduced or explained;
their original overwritten logs remain unavailable. No invented root-cause fix.
Runtime logs and36 served client files were checked against14 synthetic secrets
and48 real encrypted-session tokens: no match. Fixture-only, not universal DLP.

Prior109 unit/153 frontend/lint/types/production builds are reused only for the
unchanged source/lock/runtime images; they are not new PR7 executions. No hosted CI,
Firefox/WebKit/real-device test, heavy crypto, Groth16 or blockchain. No production
secret/backup/PITR certification. Local services can stop when WSL loses its
foreground holder; a stopped fixture was resumed on retained volumes/identical
images before the final privacy read. This is not a diagnosed cause of old timeouts.

Application source, migrations, dependency locks, classifier, workflows, Core and
M8 marketing unchanged. No GitHub setting, push, PR, merge or deployment.
Verdict: READY FOR LOCAL QA; publication NO-GO. Required next action: QA04 exact
delta/evidence review, then compatible remaining fixes, reviewed immutable artifact
adoption, independent enforcement and separately authorized exact-SHA hosted CI.

Primary references inspected2026-11-12:
- https://github.com/tianon/gosu/blob/29b939aa5bd4dc588af765b8248f6e39150d2565/SECURITY.md
- https://www.keycloak.org/downloads
- https://www.keycloak.org/server/containers
- https://access.redhat.com/security/cve/cve-2026-91403
- https://access.redhat.com/security/vulnerabilities/RHSB-2026-012
- https://security-tracker.debian.org/tracker/CVE-2023-45853
- https://security-tracker.debian.org/tracker/CVE-2025-7458
- https://security-tracker.debian.org/tracker/CVE-2026-6653
- https://eslint.org/version-support/

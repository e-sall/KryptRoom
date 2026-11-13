# M9 hosted CI bootstrap — local preparation

Base approved PR7 c2a8e7b8d30472297beecd4a2fdb08b512c62e46.
Branch release/m9-hosted-ci-20261112. No push/PR/merge/hosted run/settings change.

## First execution boundary

Read-only remote refs: dev d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83,
main1715b504e2041127056127ab5236a3248195a234. Inspect all4main/13dev/15PR7 workflows,
then16candidate workflows. No workflow_run/workflow_call/schedule/other chained
events found. Full raw definitions, permissions/secret references and per-job
conditions are in the flat handoff; do not infer protection from a classifier name.

First push on this exact branch selects only M9 Hosted CI Bootstrap. A PR to dev
and a synchronize event with the same full diff select13 workflows. PSI and M5
proof acceptance path filters do not match this diff; M7 live is manual-only.
Six potential heavy jobs are structurally dependent on successful change-scope:
M2 join, M2.5 persistent-state, M3 analytics, M4 NN, M6 OpenFHE and M5 Groth16.
On the exact diagnostic allowlist PR, core=true is emitted then classification deliberately FAILS.
The implicit successful-needs condition prevents their execution on this diagnostic
diff. A real Core path edit can make M5 event-applicable again. Actual Core/unknown
edits do not qualify for this execution refusal: their existing
mandatory crypto routing stays intact. The launch audit rejects such a diff before
any push/PR. Its recipe and private-nn.yml are not edited; fixtures/proof history stay unchanged.

Fast Core contracts remain: root npm tests/PSI test vectors, Rust native relation/
canonicalization, M7 local Foundry tests and Python/privacy/reproducibility checks.
They are not MPC/FHE integration, Groth16 generation or chain broadcast. With the
current diff the PSI workflow itself is not selected. Workflow-level 'not triggered'
and job-level 'blocked by failed dependency' are distinct in TRIGGERS.json/HTML.

Other branches and explicit manual workflows keep their existing Core behavior.
No generic core=false exception. No manual prover/chain workflow is authorized.
On this PR the new policy/aggregate also refuse outstanding Core validation: one
cannot merge by selecting a skipped heavy job as a successful required check.

## Diagnostic workflow

Owner/repository/fork refusal precedes candidate checkout. Only contents:read;
all new actions pinned to full SHAs, no environments/external secrets or write
token grants. Candidate helper is not an independent trust authority.

Policy checks exact source SHA, PR merge SHA, existing ancestor baseline and a
closed diagnostic path allowlist. That allowlist does NOT change Core classification.
Actual Core/unknown changes refuse diagnostic builds. The aggregate always runs
and refuses failed/missing/cancelled/skipped required consumers. Other PRs have
explicit non-applicability, not a claim that critical M9 tests ran.

Backend: hash-locked Python, audits, style/types/unit/build/package measurements.
Security: root audits and the unchanged strict frontend gate. Eight moderate
findings/EOL/invalid or missing records stay refusals; no renewed exception.
Images: build API and PG17.12 candidate, inspect the selected default PG/Keycloak
digests, full OS/language/unfixed scans without service startup. Preserve all
reports and bind archive/index/config IDs/source SHA. Selected PG17.11 is also
refused by the17.12 floor. No scan ignores or false PASS on scanner errors.

Frontend lint/types/build/unit/browser operations wait for successful security.
Real PostgreSQL/RLS/migration/secret/restart/restore/identity acceptance waits for
backend, image and frontend success. Original fixture functions are reused in a
CI-only controller; its root role is host orchestration, not API/browser root.
Rebuilt actual running image IDs are rescanned before cleanup; their bytes are
not assumed identical to a separate preflight build. Artifacts contain public
package/image measurements and reports, never private runtime credentials.

Expected first hosted result: release aggregate RED. Backend may pass; npm and
image jobs refuse; frontend/identity are skipped by prerequisites. These expected
refusals are not successful functional acceptance. Hosted runs/real scheduling/
Docker build-service-scan orchestration are NOT RUN in this mission. Previous
PR2–PR7 local QA remains a reference, not hosted certification.

## Solo governance and next actions

Local routing/security suite:87 tests PASS (including14 bootstrap regressions),
plus4 auditor-filter tests PASS. Actionlint PASS with ShellCheck/pyflakes integrations
unavailable;16 YAML definitions parse. PowerShell launch syntax parses. Real temporary
Git histories exercise missing/non-ancestor baselines, first push and PR merge SHA.
Certified PR7 raw findings are integrity-checked and still refused even if their
audit/scanner exit is incorrectly zero. No dependency audit or product QA is rerun.

No external human reviewer is engaged or invented. Hosted execution is a separate
runner, not independent security review. Ruleset required checks are not configured
or newly verified here. In-checkout workflow/helper changes can remove their own
guards: no adversarial self-modification guarantee. Re-audit every new exact SHA
before pushing; unreviewed workflow/event/helper deltas are a publication NO-GO.

After the authorized first run, required stable context: m9-bootstrap-release,
source GitHub Actions (verify actual App/context from that run). For a future PR,
also retain ci-scope-classification, release-ready and existing applicable M9/Core
checks. Never require only individual skippable integration jobs. Current PR Core
refusal must remain red until a separate crypto-validation/governance decision;
no merge approval is supplied by this bootstrap.

Use LAUNCH.ps1 with the full reviewed SHA from the handoff and Python3.12 with
hash-locked M9 dev tools/PyYAML. Verify is read-only; Push and PR each require their
own explicit authorization switch. Runs lists exact-head push runs without a
manual workflow dispatch. Do not dispatch state-proof-acceptance or M7 live.
Inspect the run via `gh run view <id> --repo e-sall/KryptRoom --web`; review the
run's jobs/logs and SHA. A PR can only be opened after its own authorization and
fresh trigger audit; no merge command is supplied.

SAFE TO AUTHORIZE FIRST PUSH applies only to this exact locally reviewed commit,
this branch and the audited GitHub Actions events. It is not an authorization to
push now, release, merge or deploy. Unknown external webhooks/settings are outside
this workflow audit. All known vulnerability and governance gates stay open.

GitHub semantics used:
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://docs.github.com/en/actions/reference/workflows-and-actions/expressions
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

# M9 publication routing proposal — not authorized for publication

Base: dev `7fde54f86b8df11d162eb317414dc1d2f932b70a`.
Branch: `ci/m9-scope-isolation`. Requires independent architecture/security review,
founder scope approval and separate disposition of M8 tooling used to validate this
CI transition. No workflow has been dispatched or published by this proposal.

## Behavior

The existing `core` output/API is preserved. Add explicit `web` and `m9` outputs,
stdout JSON and a GitHub step summary. `ci-scope-classification` is a unique,
always-emitted policy check on relevant PR/push/manual events, without path filters.
Missing revisions, invalid event SHAs or failed policy tests fail the job; manual
and unknown events retain full applicability. Complete merge-base diffs, new-branch
comparison to dev, no-renames and more than 300 files remain supported.

Only the established M9 component structure and docs are M9-owned. Unknown component
entrypoints remain conservative. Shared contracts, security policy, classifier/CI
changes and unknown files require all relevant consumers. In particular, classifier
files are no longer blanket-exempt as frontend plumbing. M8-only changes select
web, M9-only changes select M9, mixed changes union the consumers, and any Core
change still selects Core even when mixed with either UI or backend files.

The isolated M9 workflow is recognized only by two exact, complete SHA-256 recipes:
the original `c99d8f5` recipe and the proposed scoped follow-up retained as CI test
fixtures. Arbitrary additions, edits, deletions, unknown prior recipes, removed
manual triggers, audit suppression or permissions changes are conservative. This
is not a `.github/workflows/**`, `tests/**` or cryptographic-fixture exemption.

M8's existing `foundation` job remains present on dev/main PR/push and manual events.
It validates routing and classifies first. For web=false it reports explicit
non-applicability without installing Node/frontend packages. For web=true every
original action/command remains, with the same versions, permissions and timeout.
A classification failure fails foundation; there is no continue-on-error fallback.

The proposed M9 follow-up does the same for `m9-control-foundation`: stable context,
explicit non-applicability, full original Python/PostgreSQL/audit checks when m9=true,
and unchanged manual behavior. It must be applied to M9 only during its separately
approved reconciliation; it is not a runnable backend workflow on this pre-M9 branch.

## Cryptographic and required-check boundaries

No existing M1–M7 workflow is edited. In particular `private-nn.yml` is byte-identical,
so no M5 workflowHash or transitive M7 vector refresh is introduced. Native policy,
contract, privacy, PSI, Rust and Foundry checks remain selected as before; only
already-conditional heavy MPC/FHE jobs become non-applicable for M9-only diffs.
Core changes keep those jobs. Existing proof triggers/recipe and manual live-chain
workflow are unchanged. This exact CI-only diff selects neither Groth16 nor live
blockchain execution. A future watched proof/Core change still selects its original
checks; no historical-proof reuse is implemented.

GitHub currently reports dev/main unprotected, no required contexts and no rulesets.
No protection or check is removed/configured here. An emitted check is not equivalent
to enforced merge protection. Before activation, review a unique required
`ci-scope-classification` context plus the existing relevant checks; do not replace
domain regressions with the policy job. Do not require a nonexistent path-filtered
workflow. Foundation and the proposed M9 context always report a real job result.

## Local validation and publication order

44 policy tests pass: all 31 prior fixture/contract/gating regressions unchanged,
plus 13 M9/negative/consumer/context tests. Actionlint 1.7.12 reports zero errors for
the policy workflow, web workflow and proposed M9 workflow. A read-only source
projection with the original M9 implementation, root fix and this routing passes
the 44 policy tests plus all 20 M9 unit/static tests. No database/crypto suite was
needlessly rerun. Original M9's real PostgreSQL/restart evidence remains bound to
its unchanged backend/locks. Exact-head hosted checks are still required later.

Order: independent review; separately approve/publish/root-security PR; merge to dev
only under a later authorization; separately approve CI and its M8 nonproductive
tooling risk; publish/validate CI PR; integrate it under a later authorization;
then reconcile M9 without rewriting its published history, apply/review its scoped
workflow/test follow-up, and validate the new exact SHA before M9 publication.
Nothing here authorizes a push, merge, proof, transaction, main change or deployment.

# Draft — promote approved M8 preview to main

**Not published. Do not open/merge until the prerequisites below are satisfied.**

Proposed title: **Promote M8 frontend preview and preserve main history**.
Base: `main`. Provisional head: `release/m8-main-candidate-20261102`.
The final head must be regenerated from actual approved `origin/dev` after PR20
merges. The present local candidate includes a feature snapshot for validation;
it is not an authorization to bypass dev approval.

## Proposed PR description

Promotes the M8 synthetic collaboration interface and its final marketing
experience: canonical The Signal V4 on the homepage, the preserved 92.4-second
Product Walkthrough on `/demo` with a half-size pointer, viewport-fitted How,
Rooms/Easy Setup, Graph Workspace, Computations/Results, Provenance and Activity.
Backend adapters remain disconnected. No live crypto, AI or blockchain operation
is initiated by the frontend and no production security claim is added.

Preserves the seven main-only historical commits through merge ancestry. Their
sole added workflow is already byte-identical in dev, so reconciliation does not
change its manual-only trigger or the validated Core. No force update or history
rewrite. Current main-to-candidate file inventory is in `promotion-files.txt`.

Validation must name the final published promotion SHA. Existing local checks
and old PR20 checks are evidence only for their recorded snapshots; require fresh
hosted checks and security reevaluation before any merge. Do not manually dispatch
Groth16 or blockchain workflows.

## Preconditions

1. Resolve/renew M8-SEC-001 explicitly; obtain permitted exact-head PR20 CI.
2. Disposition remaining minimatch risk for merge, then obtain explicit PR20→dev approval.
3. Refresh dev/main; regenerate the candidate from actual dev, preserving main ancestry.
4. Validate its exact code/tree and hosted checks without disabling existing controls.
5. Obtain separate main merge approval. Deployment and tag require their own authorization.

## Rollback and proposed version

If a later approved promotion causes a regression, create a revert branch from
the then-current main and revert the actual promotion merge using first-parent
semantics (`git revert -m 1 <actual-promotion-merge>`), then validate and review
that PR. Never force-reset main. This reverses repository code only: it must not
delete RoomStates, alter historical proofs/receipts or reverse on-chain records.
No rollback command has been executed.

Proposed tag: **v0.8.0-preview.1**, explicitly a synthetic frontend preview.
No local or remote tags existed at inspection; recheck before a future authorized
tag. No tag, release object or deployment has been created.

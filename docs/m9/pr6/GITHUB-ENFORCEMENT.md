# Founder configuration plan — no remote setting changed

Read-only REST 2026-11-12 UTC: ruleset 26999669 active on main/dev, deletion and
non-fast-forward blocked, PR required. Approvals=0; stale dismissal/code-owner/
last-push/conversation requirements=false; required checks absent; bypass empty.
Classic protection endpoints: 403, UNKNOWN. Remote dev:
d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83; main:
1715b504e2041127056127ab5236a3248195a234. Local PR2–PR6 not published.

## Exact manual sequence, after separate authorization

1. Repository → Settings → Collaborators → Add people: invite an actual trusted
   independent reviewer with the write access needed for counted reviews. They
   must accept. e-sall alone cannot independently approve their own change.
2. Settings → Rules → Rulesets → KryptRoom Protected Branches → Edit. Keep Active,
   main/dev targets, deletion/force-push restrictions and empty bypass list.
3. Require a pull request before merging → Required approvals: at least 1. Enable
   Dismiss stale approvals, Code Owners review, approval of most recent reviewable
   push and conversation resolution. Retain merge commits, not linear-history-only.
   Restrict review dismissal to agreed independent authority where supported.
4. Separately review/install .github/CODEOWNERS with the REAL accepted reviewer
   covering itself, workflows/helpers/classifier, dependency manifests/locks,
   Dockerfiles, migrations, secret scripts and security documentation. No fake
   owner or active placeholder file is installed by PR6.
5. AFTER authorized hosted validation, Rulesets → Require status checks to pass
   → Add checks: select actual exact-SHA check-run names and source GitHub Actions
   (app_id 15368), not Any source. Require branches up to date. Preserve existing
   applicable Core/M8/M9 contexts. Proposed additional required aggregate:
   `release-ready`, workflow M9 Release Readiness. Its policy/backend/security/
   packaging dependencies must succeed when applicable. Inspect actual names
   after the run; never substitute conditionally missing jobs or invented greens.
6. Settings → Branches → Branch protection rules: administrator verifies BOTH
   main/dev effective review/check/no-force/no-delete/admin-enforcement rules.
   Export screenshots/REST JSON. Connector 403 is not proof of their absence.
7. After separate authorization, harmless governance test PR: missing/stale review,
   last-pusher approval, failed/cancelled check must prevent merge. No Groth16 run
   is authorized for that test. Keep merge/deployment permissions separate.

Observed existing dev check source: GitHub Actions app 15368. Distinct contexts
include `ci-scope-classification`, `m9-control-foundation`, `foundation`,
`python-contract-and-privacy`, `contract-canonicalization-and-privacy` and
`foundry-contract`. `change-scope`, `policy` and `contract-and-privacy` occur in
multiple workflows: selecting the name alone does not prove each workflow ran.
Keep those controls; a separately reviewed unique-naming/required-workflow plan
is necessary rather than guessing which duplicate result protects the branch.
Future `m9-identity-organizations` and `release-ready` have no hosted run here.

## Trust gaps that these clicks alone do not solve

An editable checkout helper/workflow can emit its own check name. Pinning GitHub
Actions as source does not prevent that. Required reviews protect merge, not the
execution of unreviewed workflows. Same-repository PR does not mean reviewed code.

Independent authority still needed: accepted human plus a validator governed
outside the PR. Use an organization-required workflow from a separately controlled
immutable source if the plan permits; otherwise a separately administered narrow
GitHub App/check. Availability/custodian/setup remain unverified governance gates.
Protected environments with independent reviewer and Prevent self-review can gate
execution only when the trusted workflow cannot remove its own environment.
No reviewer or configuration is invented. Until resolved, hosted execution and
publication remain blocked. No pull_request_target PR checkout or production
secrets introduced.

Review records must bind exact PR test-merge SHA, ancestral baseline, event/repo,
lock/audit/nft hashes, pinned image, issue/expiry≤24h and revocation. Independently
controlled custodian issues/revokes them; admin variables alone do not authenticate
independence. No truthful record can declare lint supported/audit clean today.
Unsigned artifact measurements are not independently signed provenance.

[GitHub review/check rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

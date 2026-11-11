# M9-PR2 release unblock — 2026-11-10 Toronto

**BLOCKED; publication NO-GO.** Code QA of
`b68d56bb1de530dc0e432fe9c054164be05477dc` remains approved; no code QA reopened.
This follow-up changes only this release-control plan. No dependencies, lockfiles,
helper, workflow, classifier, Core, preview or security exceptions are changed.

## Frontend dependencies: no complete compatible fix established

Fresh npm **10.9.4** audit: **8 moderate / 0 high / 0 critical**; production audit:
**0 findings**. The complete audit exits 1 and remains blocking. These are eight
affected package/metavulnerability entries from one advisory, not eight distinct
advisories. Installed minimatch 10.2.6 via typescript-eslint/typescript-estree is
affected; minimatch 3.1.5 is outside this advisory's >=7,<11.0.1 range.
Next's embedded nft remains a separate artifact-review concern, not disproved
by a clean production npm audit.

Current official metadata: Next/eslint-config-next 16.4.6; ESLint 10.14.0;
typescript-eslint/typescript-estree 8.72.2; minimatch 11.0.7. React plugin 7.37.5,
import 2.32.0 and jsx-a11y 6.10.2 still declare peers through ESLint 9.
The maintained ESLint 10 line itself declares minimatch ^10.2.6; latest estree
declares ^10.2.2. Neither range admits patched minimatch 11.

An isolated npm10 strict lock-only resolution of Next/config 16.4.6 plus ESLint
10.14.0 fails ERESOLVE (import plugin peer conflict). No node_modules installation,
scripts, force, override or audit suppression was used. The audit=false flag on
that resolution probe suppresses only its automatic duplicate audit, not any
repository/CI security control; separate full/production audits were executed.
No candidate lockfile was copied into the repository.

Next 16.4.6 tarball integrity still matches the previously inspected official
artifact. Reuse its established byte-identical embedded-nft finding instead of
repeating an unchanged tarball inspection. No patch-only Next update is claimed
to fix the advisory. A coordinated upstream fix or a separately designed major
lint-chain migration/backport is needed; neither is silently implemented here.
ESLint 9 remains EOL. No new exception is proposed.

One full audit initially timed out at 120 s (not PASS). A retry with zero fetch
retries and a 15 s fetch timeout returned the full eight findings. Raw reports,
strict-resolution stderr, metadata and command results are in the small external
evidence directory `C:/Users/Admin/Documents/Codex/M9-PR2-RELEASE-UNBLOCK-20261110`.
No fresh lint/type/build/browser suite is claimed: no frontend code or dependency
changed and its strict preflight remains red. Docker is unavailable; hosted CI is
not authorized. Do not spend another full QA cycle on the unchanged 61-test gate.

## Observed GitHub state — read only

Ruleset **26999669**, "KryptRoom Protected Branches", is active on exact refs
main/dev, with deletion, non-fast-forward and pull-request rules. It reports no
bypass actors and current_user_can_bypass=never. Approving review count is **0**;
code-owner review, stale dismissal and last-push approval are false. There is no
required-status-check rule. This confirms PR-only protection, not independent
review or checks enforcement. No setting was modified.

Baseline check-runs were read to identify actual contexts. Source is GitHub
Actions App **15368**. Unique contexts already observed: `ci-scope-classification`,
`m9-control-foundation`, `foundation`. The Identity recipe's context is
`m9-identity-organizations`, but a hosted run of this PR2 SHA remains NOT RUN.
After separately authorized hosted validation, require these exact contexts with
source App 15368 and strict up-to-date checks. They are merge gates, not proof
that PR-owned workflow code cannot lie. Do not substitute workflow display titles
for API check names or fabricate a hosted success for the new Identity context.

Several Core jobs share `change-scope`, `policy` or `contract-and-privacy` names.
Do not treat one ambiguous name as certification of all Core workflows or remove
their validations. A trusted external verifier must match applicable workflow
IDs/paths, exact head/merge SHA and classification to all required results before
its own unique status can certify the Core matrix. No Core workflow is renamed
or exempted in this follow-up; no heavy or Groth16 run is started.

## Minimal Founder actions — separate authorization/configuration required

1. Designate one real trusted independent collaborator with write access and
   their acceptance of CI/security review ownership. Keep sole-maintainer self-
   approval explicitly insufficient. Set required approvals=1, code-owner review,
   stale-review dismissal, last-push approval by another person, thread resolution,
   and retain no silent bypass. Install CODEOWNERS through an authorized PR on the
   base branch first; proposed entries below are not active owners.
2. Register exact required contexts above only with verified source and actual
   hosted evidence. Also require a unique independently produced
   `trusted-publication-preflight` context, tied to its real App ID once installed.
   No App ID is invented and this nonexistent context must not be marked green.
3. Before execution, independently approve the exact source/base/event and build
   recipes. PR rules/reviews/checks protect merge, not the push/PR executions that
   happen first. Fork approval settings also do not protect against an owner's
   push removing a gate. A reviewer-approved environment alone is insufficient
   when the PR can delete that environment reference.
4. If automatic enforcement against an untrusted checkout is required, use an
   independently controlled preflight/execution authority: for example a trusted
   separate CI repository plus a dedicated GitHub App publishing checks to this
   repository. Keep untrusted repository Actions disabled until the independent
   execution route is established; otherwise PR-owned workflows can still start
   first. The external verifier reads manifests/recipes without running project
   scripts, then authorizes isolated frontend execution only after its own checks.
   This is an explicit infrastructure decision, NOT implemented/configured here.
   App permissions should be contents/metadata/actions-read as needed and checks-
   write only, with no repository write/admin or production secrets. Evidence of
   real permission enforcement and a negative tamper test is mandatory.

Minimal CODEOWNERS plan, pending a real designated login (not an installed file):

```text
/.github/ @DESIGNATED_INDEPENDENT_REVIEWER
/apps/web/package.json @DESIGNATED_INDEPENDENT_REVIEWER
/apps/web/package-lock.json @DESIGNATED_INDEPENDENT_REVIEWER
/apps/web/eslint.config.mjs @DESIGNATED_INDEPENDENT_REVIEWER
/apps/web/next.config.ts @DESIGNATED_INDEPENDENT_REVIEWER
/apps/web/*config* @DESIGNATED_INDEPENDENT_REVIEWER
/apps/web/Dockerfile* @DESIGNATED_INDEPENDENT_REVIEWER
/services/control-api/compose.identity.yml @DESIGNATED_INDEPENDENT_REVIEWER
/services/control-api/scripts/identity-* @DESIGNATED_INDEPENDENT_REVIEWER
/docs/m9/pr2/*SECURITY* @DESIGNATED_INDEPENDENT_REVIEWER
```

Owner must have write access, and the base branch's ownership file governs PR
review. Protect CODEOWNERS itself. These placeholders are not valid ownership or
a fictitious reviewer. No configuration is applied to main/dev by this document.
This path list targets publication recipes; it is not a trust boundary for arbitrary
application code. All source/scripts consumed by a build still need review before
execution by the independent authority, not only the files in CODEOWNERS.

## Record provenance and revocation

Current repository-variable review JSON remains declarative, not authenticated.
Do not treat a matching hash or fixed=true assertion as artifact verification.
Avoid building a new attestation service just to unblock an uncorrected audit.
The minimal future trusted authority must own the review evidence independently
of the PR checkout: approver identity, immutable review reference, repository,
merge/head SHA, baseline, event/run attempt, lock/audit/helper/recipe hashes,
issue/expiry and revocation state. Verify evidence immediately before execution;
replace/cancel stale runs after new commits, base changes or revocation. A variable
edit does not revoke a job that already consumed it. Cancellation is not a claim
of erasing data already processed. No such live revocation mechanism is supplied
or claimed by the current local helper.

## Single targeted final QA instruction

Compare the new local commit to b68d56b: only this plan may differ. Verify fresh
npm10 reports, registry peer/dependency metadata, the ERESOLVE log and ruleset
export; check the exact-context/source and pre-execution versus pre-merge design.
Reuse the approved 61 tests because their files/assumptions are unchanged. Do not
rerun frontend/Core/cryptographic suites for this documentation-only delta.
Return whether the remaining blockers and Founder actions are accurately stated;
do NOT turn that review into release approval. Actual dependency remediation,
trusted enforcement, hosted acceptance and Founder publication permission remain
separate prerequisites. No PR3 or production authorization is implied.

Sources: https://github.com/advisories/GHSA-g3hv-75wg-m249 ;
https://eslint.org/version-support/ ;
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets ;
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners .

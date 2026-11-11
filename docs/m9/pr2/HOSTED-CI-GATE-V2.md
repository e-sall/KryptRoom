# Hosted CI Gate V2 — local implementation, publication NO-GO

Starting candidate: `4b7e6bb4cafe7062360e79322f0cd63579bae119`.
PR2 baseline: `d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83`.
Only the helper, two frontend-consuming workflows, targeted tests and this document
are changed. No classifier, dependency, cryptographic implementation or runtime
security change. No exception is created. Prior QA-PR2 findings remain CLOSED.

## Enforcement and local behavior

Both Identity and M8 run standard-library gate tests, then the same helper before
their applicable frontend installs/builds. Default GitHub step success conditions
prevent subsequent frontend steps after refusal; artifact collection still runs.
There is no continue-on-error or cross-workflow success assumption. Only the newly
added upload action is pinned to the full v6 commit SHA
`b7c566a772e6b6bfb58ed0dc250532a479d7789f`; existing action references are preserved.

The helper binds the declarative review record to the actual checkout SHA, baseline,
event, repository, lockfile, audit content and pinned audit image. PR source means
the test merge SHA, not just head. Baseline must exist and be an ancestor. A first
push with before=000... refuses rather than inventing a baseline; later approval
must establish a valid independent baseline, e.g. for explicit workflow_dispatch.
The original events/dispatch and scope decisions remain intact. Shared CI changes
remain conservatively Core-relevant; no new classification exemption is added.

Review JSON requires exact fields, revoked=false and UTC issuance/expiration with
total lifetime at most 24 h. This is not a security exception: EOL/unfixed tooling,
missing review or any audit finding still refuses. An audit succeeds only with
exit 0, version 2, complete zero counts, empty vulnerabilities map and no error.
Malformed, duplicate-key or non-finite JSON refuses. Failures preserve evidence.
Timeout requests removal of the uniquely named container; unconfirmed cleanup
also refuses. Runner destruction may prevent cleanup and requires ephemeral
runners/external lifecycle controls. No live revocation of already-running jobs
is claimed. A rerun removes a stale local-validation marker before checking.

## Local validation and limits

Tests include real temporary Git graphs (missing/non-ancestor/zero baseline,
PR merge source versus head), negative review/audit cases, a real subprocess
refusal preventing a downstream marker process, and static default-success
ordering in both workflows. Docker/hosted execution is NOT RUN on this workstation
(Docker executable unavailable). Transport/container cleanup uses explicitly
simulated IO; an actual Python subprocess timeout is tested separately.
Actionlint validates the two YAML files; no hosted results are claimed.

Executed on Python 3.12.16: 61 unit/classification methods PASS (50 scope and
11 gate methods, including 29 named negative review/audit variants). Actionlint
exit 0; optional Shellcheck/Pyflakes integrations NOT RUN. Git delta whitespace
validation passes. The earlier scope assertion was extended only for the exact
new gate-test/helper/upload operations; original frontend commands and order are
still required. The unchanged classifier returns core=true, web=true, m9=true
for this shared-security delta; no heavyweight job was executed locally.

The raw historical npm10 audit at `.github/fixtures/frontend-security-audit.json`
is a synthetic-project dependency scan reference, not a crypto fixture or fresh
audit: it contains eight moderate findings and must be refused. The fixture is
copied unchanged from the prior evidence, collected November 9 Toronto / November
10 UTC. No finding is fixed, suppressed or accepted by these changes. Fresh audits
and supported lint/embedded Next-nft remediation remain publication prerequisites.

## GitHub configuration plan — NOT applied

The helper and call sites live in the PR checkout and can be replaced by that PR.
The repository variable FRONTEND_SECURITY_EVIDENCE_JSON has no signature or
verified issuing authority here. Matching hashes/booleans establish consistency,
not authenticity or actual artifact safety. A local PASS is NOT a trusted merge
authorization. GitHub protections/permissions remain UNKNOWN from prior 403 and
incomplete connector evidence. No remote setting was changed.

Before publication, independently verify Settings > Branches and Rules > Rulesets
for dev (and separately main): actual required contexts and status-source identity,
no silent bypass including administrators, stale approval dismissal, last-push
independent review, effective path ownership. Determine whether the repository's
plan/ownership supports an imposed trusted required workflow; otherwise design
an independently managed App/service enforcement. A PR-controlled job name alone
does not provide this guarantee. Do not invent a reviewer for a sole-maintainer
repository or treat self-approval as independent review.

Proposed CODEOWNERS entries, not installed, pending identification of real trusted
independent reviewers with appropriate access:

```text
/.github/workflows/                 <designated-independent-ci-reviewer>
/.github/frontend_security_gate.py  <designated-independent-security-reviewer>
/.github/test_frontend_security_gate.py <designated-independent-security-reviewer>
/.github/fixtures/frontend-security-audit.json <designated-independent-security-reviewer>
/.github/CODEOWNERS                 <designated-independent-security-reviewer>
```

These placeholders are an implementation plan, not valid configured owners.
Review must cover all CI paths, including classifier changes; no classifier is
modified by this patch. Also verify Actions permissions (contents:read, no PR
approval escalation), forks/allowed actions, variables edit authority, secret
names/scopes and environment restrictions. Supply only redacted configuration
exports, never secret values. No pull_request_target execution of untrusted code.

Separate blockers: external enforcement, authenticity/revocation governance of the
review record, eight npm findings and ESLint EOL, real hosted acceptance and a new
explicit publication authorization. No previous exception is reused. No PR3,
Groth16, blockchain action, push, merge or deployment is authorized by this document.

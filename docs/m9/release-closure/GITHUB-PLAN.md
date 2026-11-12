# Independent release enforcement — proposal only

No settings or hosted workflows changed/executed. Read-only ruleset26999669:
Active main/dev, PRs required, deletion/force-push banned, zero required approvals
and no required checks. Classic protection API403: UNKNOWN, not absent.

## Founder actions

1. Settings -> Collaborators -> Add people: designate a real independent trusted
   collaborator with write permission. Author/sole maintainer cannot supply their
   own independent approval. No fictional reviewer or disabled independence.
2. Settings -> Rules -> Rulesets -> KryptRoom Protected Branches26999669 -> Edit.
   Keep Active, main/dev, deletion/non-fast-forward bans and empty bypass list.
   Require PR approvals>=1, dismiss stale approvals, approval of most recent
   reviewable push, conversation resolution and Code Owner review. Keep merge
   commits available. Apply only after separate governance authorization.
3. Separately reviewed CODEOWNERS with that real collaborator/team: workflows,
   ci_scope.py, frontend_security_gate.py, release_checks.py, gate/policy tests,
   CODEOWNERS, runtime Dockerfiles, locks and security/migration scripts. Verify
   effective ownership; closure adds no fictional CODEOWNERS file.
4. Establish a validator outside PR authority BEFORE candidate code executes:
   organization ruleset-required workflow in a separately protected repository if
   supported, or independent GitHub App with unique required context. Executable,
   policy/record store/credentials cannot come from the PR. Bind head AND tested
   merge SHA, base, repository/event, full diff, lock/audit hashes, expiry/revocation.
   Missing/expired/revoked evidence or unknown scope must fail. Admin variables
   plus an editable checkout helper alone are insufficient. Otherwise NO-GO.
5. Same ruleset -> Require status checks. Minimal release candidates: release-ready,
   ci-scope-classification, m9-control-foundation, m9-identity-organizations,
   foundation(M8), plus ALL applicable Core checks. These are current YAML job IDs,
   not observed hosted contexts on this commit. Verify actual exact-head context
   names and GitHub App sources after separately authorized execution. Require
   up-to-date branch/validated merge queue; prove failed/missing/refused checks
   block merge. Generic duplicate policy/change-scope/contract-and-privacy names
   cannot identify a required workflow by themselves: independently review unique
   aggregates or trusted required workflows. Never silently remove Core checks.
6. Settings -> Branches: inspect classic main/dev protection. Rulesets -> Rule
   insights/effective branch rules: verify applicability, sources and no bypass.
   Remote enforcement remains NOT VERIFIED until administrator checks succeed.

## Before execution versus before merge

Reviews/CODEOWNERS/required checks constrain merge; they do not prevent PR code
already executing. Preserve contents:read, no production secrets or privileged
self-hosted runners, approved-source checks and independent pre-execution approval.
Never execute untrusted head via pull_request_target. Checkout helper is defense
in depth, not inviolable independent authority.

Security/runtime/workflow delta remains conservatively Core+web+M9. No classifier
change/exemption. PR opening may automatically trigger M5 proof work: establish
explicit execution authorization/gates BEFORE opening it. None ran here.
Remote dev lacks the local PR2–PR6 stack: closure-vs-PR6 is not full future PR diff.
Reconcile approved histories and recalculate scope on the exact publication SHA.

Sequence: verified independent protections -> dependency/CVE remediation and
reviewed immutable PG/IdP artifacts -> explicit Founder push/hosted-run approval ->
non-force push -> authorized PR without merge -> exact-head/tested-merge hosted CI ->
independent delta review -> separate risk/merge decision. Main and deployment
require separate approvals. No implicit risk exception is proposed or activated.

References:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

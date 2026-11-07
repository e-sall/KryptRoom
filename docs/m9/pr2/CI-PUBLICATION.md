# PR2 CI and publication gate

Local preparation only. No hosted job was dispatched and no remote branch/PR
was created. The portable `CI-MATRIX.json` records every changed path, its hash,
per-path scopes, complete-diff classification and exact workflow event settings.

## Routing

The complete diff selects Core, web and M9 because it includes the classifier and
a new execution recipe. PR2-only owned backend sources remain M9-only; BFF and
shared frontend dependencies select both web and M9. M8 visual-only files remain
web-only. Core/shared-security/unknown paths and unrecognized workflows retain
conservative Core selection. Fifty positive/negative classifier cases pass.

For a future pull_request to dev, the current static prediction is 11 workflows
and 22 job definitions:

- CI scope classification.
- M9 Control API Foundation.
- M9 Identity & Organizations (new, additive).
- FHE State Transition, Persistent RoomState, Private Analytics, Private Join,
  Persistent Private Neural Network (each retains its existing scope/contract/
  real-integration jobs).
- Public Chain Anchor (offline contract/privacy checks only).
- Committed State Transition Proof (fast Python/Rust contract/canonicalization).
- M8 Web Foundation (existing full frontend validations).

The PSI workflow's existing path filter does not select this diff. No PSI source
changes are present. The real Groth16 acceptance workflow's unchanged explicit
paths do not match this diff. Live chain acceptance is workflow_dispatch only.
All manual triggers and existing required-check contexts remain unchanged. No
claim is made that this local analysis configures GitHub protection rules.

## Security and execution

The new identity job has read-only contents permission, digest/SHA pins, no
production secrets, foreign-source refusal, strict hash-locked Python audit and
a strict frontend moderate-audit gate before its identity build. It then tests
an original PR1 database upgrade and real isolated identity acceptance, followed
by explicit fixture cleanup. The retained foundation job supplies Python style,
types, unit tests, packaging, audits and PostgreSQL lifecycle coverage.

Eight existing moderate frontend findings would fail the new strict gate. The
existing M8 job is independent and would also execute lint/build/browser checks.
Therefore a local-only exception cannot authorize publication or hosted execution,
even when the new job would stop early. Do not push until the security scope has
been resolved by a compatible fix or distinct explicit bounded Founder decision
and any corresponding control change has been reviewed.

## Next executable sequence

1. Independent 01/04 review of this exact source and security delta.
2. Resolve hosted frontend security exposure without suppressing audits or tests.
3. Obtain separate Founder authorization for push and PR creation.
4. Recheck remote dev, complete diff and workflow/security prerequisites.
5. Publish without force push, then inspect every applicable check on the exact SHA.
6. Request separate merge authorization only after hosted acceptance succeeds.

No old M8/M9 disposition, production approval, merge authority or PR3 start is
inferred from the local PR2 implementation authorization.

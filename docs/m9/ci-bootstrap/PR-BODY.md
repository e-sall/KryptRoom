Prepare owner-controlled non-production hosted M9 diagnostics on the reviewed
release branch. No merge/release/deployment approval. Includes the existing locally
reviewed PR2–PR7 stack; those local results are not hosted CI results.

The first push runs only M9 Hosted CI Bootstrap. Core remains conservatively true
for shared CI changes. On this PR, scope classification deliberately fails before
heavy dependent crypto jobs; required Core validation remains outstanding. No
private-nn.yml/fixtures/protocol change. Fast contract checks remain applicable.

Known npm/ESLint and image findings remain blocking. Frontend/services are gated
before execution; missing/failed/cancelled/skipped required consumers cannot satisfy
the stable aggregate. No new security exception or fictitious independent reviewer.
Any pipeline/helper/event delta needs a new local exact-SHA audit before push.

See docs/m9/ci-bootstrap/REPORT.md and the flat QA handoff for triggers, limitations
and reproducible commands. Do not merge this diagnostic PR automatically.

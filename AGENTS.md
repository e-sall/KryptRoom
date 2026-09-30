# Instructions for coding agents

1. Read `PROJECT_CONTEXT.md` before planning or editing.
2. Inspect the repository and current branch before meaningful changes.
3. Security and privacy claims must match code that has actually run and the documented threat model.
4. Never fake cryptography or relabel encryption at rest as encrypted computation.
5. Raw participant data must never reach the Control Plane.
6. Use mature, reviewed cryptographic libraries; do not invent cryptographic algorithms.
7. Test privacy-critical code, protocol configuration, negative disclosure cases, and reproducibility where practical.
8. Keep private datasets, keys, traces, and protocol outputs out of Git.
9. Do not expand product scope or reorder milestones without approval.
10. If a product decision is missing, stop and ask the user one concise question.
11. For technical implementation details, use sound engineering judgment and record consequential choices in `docs/DECISIONS.md`.
12. Never claim malicious security when only an honest-but-curious or semi-honest model is implemented.
13. Do not silently downgrade a cryptographic protocol to a mock to make a test pass.
14. For each milestone: plan, implement, execute tests, diagnose failures, fix, document, update `CHANGELOG.md` and `TODO.md`, then commit cleanly.
15. Do not merge `dev` into `main` unless the milestone is stable and its evidence is documented.


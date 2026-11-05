# Root ZIP dependency remediation proposal

Baseline: dev `7fde54f86b8df11d162eb317414dc1d2f932b70a`.
Local branch: `security/adm-zip-061`. No publication or merge authorization.

Extract only the already-tested package manifest, lock entry and six dependency
tests from `fe8302767760c6c72f3d7febd221a191df5bdf2b`; do not import its promotion
ancestry, workflow edits, approval environment or unrelated documents.

The scoped override resolves `protoc-gen-js@3.21.4 -> adm-zip@0.6.1`. Only the
`node_modules/adm-zip` lock entry changes (version, URL, SRI and minimum Node 14).
PSI stays exactly 2.0.6 and protoc exactly 3.21.4. Existing test globs are retained;
the new dependency test glob and a targeted script are appended.

Fresh official registry metadata confirms the fixed 0.6.1 package/integrity.
Protoc 3.21.4 is deprecated in favor of 3.21.4-4, but that release also depends on
vulnerable adm-zip 0.5.10, so it does not solve this issue. Protoc 4.0.3 uses fflate
but is a generator major upgrade outside PSI's declared range. Neither is forced.
This narrowly scoped override is outside the parent's exact ZIP pin; compatibility
is therefore demonstrated by tests, not inferred from semver alone.

Validated locally on Windows Node 24.12.0/npm 10.9.4 and Linux Node 22.22.0/npm
10.9.4: **34 root tests pass**, including **six ZIP/protoc tests** and real two-node
PSI. The demo reveals cardinality 2 and `matchedIdentifiersRevealed=false`.
Two additional clean `npm ci --ignore-scripts` installations pass all six targeted
tests, preserve the exact lock bytes and retain all 25 original PSI package files.
Full and production npm audits are both **zero findings**, including on Linux.

The original protoc post-install script is exercised with a small synthetic HTTPS
archive fixture; the synthetic binary is never executed. This tests installer API
compatibility, not cryptography. The separate PSI tests use the real package.
Installation scripts remain disabled, matching existing CI. ZIP traversal/junction
and duplicate-name regressions are retained. No `audit fix --force`, protocol,
algorithm, cryptographic fixture, proof recipe, security exception or CI file changes.

Proposed PR: **Security: fix scoped protoc ZIP dependency without changing PSI**,
base `dev`, these four files only. Root-path changes are correctly classified Core
and retain their normal regression jobs; no Groth16 acceptance path or live chain
workflow is selected by this exact diff. Required hosted checks, independent review,
and founder publication/merge approval are still needed. This does not approve the
separate CI-routing proposal, M9 publication, M8 risk acceptance or main promotion.

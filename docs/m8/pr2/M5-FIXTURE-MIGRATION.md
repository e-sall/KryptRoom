# PR15: exact synthetic M5 fixture migration

## Authorization and boundary

Owner-authorized limited M1–M7 freeze exception, 2026-10-22. This refresh repairs
the deterministic golden-vector failure in run
[39786884104](https://github.com/e-sall/KryptRoom/actions/runs/39786884104).
It does **not** change M5's relation, contracts, hash functions, generator,
cryptographic implementation, proof semantics, or runtime configuration.

The approved M4 CI condition changes the full-text hash of
`.github/workflows/private-nn.yml`. The unchanged M5 generator deliberately binds
that hash into synthetic metadata. Retaining the old vectors would therefore
be inconsistent. The assertion detecting that inconsistency is kept unchanged.

Run only: `python tests/state_proof/generate_fixture.py`.
No fixture was hand-edited or produced by a substitute generator. Exactly six
generated files change under `tests/state_proof/fixtures/`:

- `S3_model.json`, `S3_model.content.json`
- `S4_eval.json`, `S4_eval.content.json`
- `receipt.json`, `hashes.json`

## Exhaustive hash and semantic audit

[M5-FIXTURE-HASHES.json](M5-FIXTURE-HASHES.json) records the before/after SHA-256
of all eight files, every one of the **35 changed JSON leaves** with its exact
JSON pointer, all new derived digest values, and unchanged source/report hashes.
The four changed canonicalHex fields are represented by exact decoded byte
lengths and hashes; complete hex is deterministically recoverable from their
sibling `value` and present in the tracked fixture. No change is omitted.
The inventory is verified by CI scope tests against the actual files.

Root workflowHash:

- Before: `d66c581c73dbe1953f73fc573d9377da3e792b350bc0f516475e57fef5ff5449`
- After: `490a46ad8295011b53f9399fc09de26b3f039d4a0c19958e7ef52951eee39c66`

The only semantic leaf differences are that workflowHash and its derived
training/evaluation transition commitments, S3/S4 state commitments and parent
references. Receipt/vector digests and canonical encodings change accordingly.
All other fields, object keys, array lengths and array order are identical.

Explicit invariants:

- S1 JSON and S1 content are byte-identical (both hashes recorded).
- codeHash stays `a8d0e674afa5b9bbdb5fa1d1c7cee1a7b31f997b0112b09683c997748d58a2ff`.
- Policies, authorized recipients/reveals, deny-default behavior, CryptoContexts,
  artifact identifiers/descriptors/commitments, operators, transition IDs,
  parent IDs/order, model/evaluation parameters and timestamps are unchanged.
- Vector entries 1, 2, 3 and 5 (policy, context, artifact/context, output policy)
  are entirely unchanged.

## Exact CI exception, not a directory exclusion

`.github/ci_scope.py` requires all six old Git blob byte hashes and all six
new byte hashes to equal the pinned migration, and both S1 files to match their
unchanged hashes. It also pins the M4 workflow to the exact approved new hash.
The old workflow may be either the pre-filter version (PR comparison with dev)
or the already-approved filter version (follow-up push comparison).

Partial refresh, arbitrary byte/whitespace change, deletion, rollback, subsequent
fixture edit, modified policy or S1 mismatch fails recognition. Every other
changed path still passes through the conservative core classifier: extra fixture,
generator, contract, relation, assertion, dependency or runtime workflow changes
require core checks. There is no `tests/state_proof/**` exclusion and no
unconditional fixtures exemption. Manual dispatch remains core.

This is a fixed compatibility entry for one reviewed migration, not a rule that
approves future regenerations. CI policy files themselves remain review-sensitive.
The frontend checkout fetches history solely to test immutable pre-migration blobs.

## Validation and historical proof preservation

- Existing Python M5 contract/canonicalization/privacy suite: 13 tests PASS locally.
- Existing Rust 1.96.0 native relation suite: 6 tests PASS locally.
- Scope/migration suite: 23 tests, including all required negative cases.
- Frontend lint, types, build (29 pages), 40 units and 31 Chromium tests PASS
  locally; two intentional non-mobile skips. Final CI links are recorded in PR15.
- After staging the six generated fixtures, a second run of the unchanged
  generator and `git diff --exit-code -- tests/state_proof/fixtures` PASS (exit 0).
  The original CI regeneration step and diff assertion remain byte-unchanged.

**No Groth16 generation or blockchain transaction is performed.**
Native Rust relation success and golden-vector reproducibility are not proof
generation or cryptographic validation of these new fixture bytes.

Historical proof bundles, receipts, SHAs and validation conclusions are untouched,
as are `docs/M5_VALIDATION.md` and `docs/STATE_PROOF.md`. The historical
authoritative run remains
[38922127315, attempt 2](https://github.com/e-sall/KryptRoom/actions/runs/38922127315)
on the documented historical commit; its provenance must not be rebound to PR15.
`tests/state_proof/fixtures/receipt.json` is a **synthetic test-vector receipt**,
not that historical proof bundle's receipt. No historical artifact was downloaded,
rewritten, replaced or uploaded by this migration.

The new fixture set has contract/canonicalization/reproducibility test coverage
only. It is **not claimed to be covered by a newly generated Groth16 proof**.

# PR #15 — exact downstream M7 synthetic-vector migration

Owner authorization: 2026-10-22. Baseline:
`7a0b261599cae121a08f1d13e260724056455b4f`.
This corrects the single deterministic-reproduction failure in the previous
[M7 run](https://github.com/e-sall/KryptRoom/actions/runs/39790417179).
It is not a new cryptographic acceptance, proof, deployment or chain anchor.

## Exact scope and inventory

Only `tests/chain_anchor/fixtures/state-proof.json` and `vectors.json`
are regenerated, exclusively by the unchanged
`python tests/chain_anchor/generate_vectors.py`.
The generator, vector builder, hashing/canonicalization, assertions, schemas,
contracts, runtime workflows and M1–M7 implementations are unchanged.

[M7-FIXTURE-HASHES.json](M7-FIXTURE-HASHES.json) is the exhaustive inventory:
exact old/new SHA-256 Git-blob bytes, every changed JSON pointer and both values,
including every changed commitment. Git's optional Windows CRLF conversion is
not part of those canonical source hashes. Both generated files use LF.

- `state-proof.json`: six leaves change: outputStateCommitment,
  transitionCommitment, receiptHash, publicValuesSha256, proofId, proofArtifact.uri.
- `vectors.json`: four leaves change: subjectCommitment,
  stateProofDocumentCommitment, stateOnlyAnchorCommitment,
  stateProofAnchorCommitment.
- All other leaves remain identical. In particular: room/state/transition IDs,
  versions, timestamp, program verification key, ELF digest, fixed proof digest,
  proof size/media type, evidence type and zero no-evidence commitment.

The old values remain explicit historical references in the inventory and Git.
Existing M5/M7 acceptance reports and their conclusions are not rewritten.

## Dependency chain and proof boundary

The approved CI condition change changed the complete M4 workflow file digest.
The preceding [M5 migration](M5-FIXTURE-MIGRATION.md) propagated that workflowHash
through S3/S4 metadata commitments and the synthetic transition receipt.
M7's unchanged vector builder reads that S4 document and receipt:

1. S4 commitment becomes the subject/output commitment.
2. The receipt's domain-separated digest changes the representative public
   claim digest, proof ID and descriptive proof URI.
3. The representative descriptor commitment changes.
4. The state-only and state-with-evidence anchor commitments change.

**Layer B is documentary commitment consistency, not Layer C proof validity.**
`state-proof.json` is a representative synthetic descriptor that reuses fixed
historical-looking proof fields. Its unchanged proof digest, program key and ELF
digest do **not** establish a proof of the updated receipt/public values.
The generated URI identifies no newly produced proof bundle. Do not submit this
descriptor as historical proof evidence or claim that its changed commitments
were verified by the historical Groth16 proof. No Layer C verifier/prover was run.
No anchor was submitted. The vectors are test data, not new published commitments.

Both S1 files, codeHash, policies, CryptoContexts, artifact IDs and commitments,
operators, recipients, parent ordering and transition semantics retain the
invariants documented and tested in the M5 inventory.

## Exact CI recognition

The M7 exception requires both old/new file hashes, with no JSON normalization.
For the full PR, it also requires the complete existing six-file M5 migration,
unchanged S1 hashes and exact approved workflow bytes.
For the follow-up push, all six M5 files must already have their exact new hashes
on both sides, both S1 hashes must match and the workflow must be unchanged at
the approved hash. Mixed/partial M5 baselines are rejected.

Arbitrary bytes, deletion, a partial refresh, a wrong old hash, rollback, later
fixture edits, an extra fixture, policy/context changes, generator/builder edits,
code/relations/assertions/schemas/contracts/dependencies or runtime workflow
changes still require core checks. No directory exemption is added.
Manual dispatch remains core=true. M7's Python suite and regeneration/diff job
are entirely unchanged and always execute for this PR.

## Dependency audit and historical preservation

Repository searches for fixture consumers and former commitments found no
additional synthetic fixture requiring refresh. M7 Python tests consume the two
files above; Foundry uses its own independent contract vector. M6 state-only
tests construct temporary metadata rather than another committed M5-derived
golden file.

The old state-only commitment remains in `docs/PUBLIC_CHAIN_ANCHOR.md` and
`.github/workflows/public-chain-anchor-live.yml`. These are intentionally
preserved historical acceptance references, not stale vectors to rewrite.
The manual live workflow retains its historical commitment guard: do not use
this new synthetic fixture set to claim or resume that historical acceptance.
Any future live run needs separately authorized inputs/provenance review.

Historical Groth16 proofs, proof-bundle receipts and SHAs, the Base Sepolia V1
deployment, finalized anchor, events and public artifacts were not modified or
re-created. No RPC transaction, deployment or live workflow was invoked.

## Executed local validation

- M7 Python: 45 PASS, including exact reproduction, privacy and layer separation.
- Foundry 1.8.5: format/build PASS; all 3 existing tests PASS in local EVM only.
  Windows emitted a nonfatal signature-cache permission warning; exit code 0.
- M5 Python: 13 PASS; Rust native relation: 6 PASS, zero prover executions.
- CI classifier/migration suite: 31 PASS, including required negative cases and
  exhaustive old/new inventory comparison. No existing M5/M7 assertion changed.
- Frontend: lint/types/build PASS (29 pages), 40 units PASS;
  Chromium desktop/tablet/mobile: 31 PASS, 2 existing non-mobile skips.
- Repeat both original generators after staging and after commit; require
  `git diff --exit-code -- tests/state_proof/fixtures tests/chain_anchor/fixtures`.

Final-head remote workflow conclusions are recorded in PR #15 after publication.
Skipped heavy jobs are not newly validated crypto. PR remains open for human
review; no merge is authorized. Existing M8-SEC-001 and preview-only limitations
remain unchanged.

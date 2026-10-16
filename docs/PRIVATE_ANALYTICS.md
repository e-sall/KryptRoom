# M3 — Persistent Private Cohort Analytics

Status: implemented, pending cryptographic integration validation.

M3 consumes precisely the existing S1 `match-mask` grid `[R,R]` and `lab-a-features` / `lab-b-features` grids `[R,R,1]`. The current join exposes one feature per lab; selectors use explicit zero-based columns and neutral metric IDs, with no inferred schema aliases. M1/M2 cryptographic circuits and the pinned SecretFlow 1.14.0b0 CHEETAH/FM128 configuration are unchanged.

## State and authorization

S1 must opt in at creation with `StatePolicy.allowedOperators = ["private_analytics"]`, the exact three allowed input artifact IDs, and explicit scalar permissions. The S1 transition retains its already-authorized cardinality in commitment-covered public metadata. Legacy S1 states remain readable, retain their original encoding, and do not acquire analytics permission automatically. There is no retroactive policy edit or migration.

The public bound request contains the exact parent state commitment, ordered ArtifactRefs and derived artifact commitments, canonical spec hash, code hash, workflow hash, crypto-context hash, policy hash, and requested-reveal hash. Both nodes agree on the public state/request hashes before computation. The code hash covers the seven runtime modules; the workflow hash covers the M3 CI workflow. These unsigned hashes bind content, not trusted execution or a malicious host.

`PrivateAnalyticsTransition` extends the existing `StateTransition` using optional canonical bindings. Its SHA-256 commitment covers the request, output state ID and ordered output artifact commitments. The existing RoomState commitment then covers the parent list, transition (including parent commitment), exact output descriptors, policy and crypto context. Artifact commitments hash each public ArtifactRef and crypto context using the existing sorted-key JSON encoding. Neither a coordinator nor a node receives both raw shares to hash them. AES-GCM ciphertext is randomized, so commitments are deterministic for fixed descriptors, not identical across fresh encryptions.

## Exactly four operations

- COUNT: `sum(mask)`.
- SUM: `sum(mask * selected_feature)`.
- MEAN: `sum(mask * selected_feature) / sum(mask)`.
- CROSS_MEAN: `sum(mask * lab_a_feature * lab_b_feature) / sum(mask)`.

The scalar results remain SPUObjects. The supplied six-metric fixture produces:

```text
analytics-count-matched-count
analytics-sum-sum-a
analytics-sum-sum-b
analytics-mean-mean-a
analytics-mean-mean-b
analytics-cross-mean-cross-ab
```

Only logical scalar outputs persist. Row products and reduction buffers remain transient. S2 uses `parentStateIds = ["S1"]`, the same compatible crypto context, existing node-local key file, native SPU dump/load, and existing context-bound AES-256-GCM envelope. S1 files are never updated.

COUNT uses int32; the other reductions cast to float32 for fixed-point SPU arithmetic. The absolute correctness tolerance is **0.001**, defined in `analytics_contract.py` and shared by tests. This tolerance covers the bounded synthetic acceptance fixture, not arbitrary feature magnitudes or unbounded cohorts. No floating-point exact-equality claim, general overflow guarantee, numeric-range proof, or performance benchmark is made.

MEAN and CROSS_MEAN require a valid positive parent cardinality before the runtime is created. Zero fails with `EMPTY_COHORT`, before division. COUNT/SUM can accept zero. The secret count remains the actual denominator; the stored public count is the previously authorized M2 result and a precondition under the semi-honest model. No new secret comparison circuit handles empty cohorts.

## Separate reveal action

Computation never reconstructs analytics outputs. A later invocation validates S2's lineage and commitments, checks both the committed requested-reveal set and StatePolicy, then loads only the selected scalar. `RevealService` is the sole M3 reconstruction boundary. Unauthorized requests fail before runtime creation, loading, SPU-to-PYU transfer, or reconstruction. There is no raw-artifact reveal CLI.

The default acceptance manifest requests and authorizes only `analytics.mean.mean-a`, to both labs; CROSS_MEAN remains secret. Empty `requestedReveals` keeps all analytics scalars secret. SUM can be revealed only through a separate explicit scalar authorization; it is never a default disclosure. Metadata exchange is separately authorized and contains only public hashes, sizes and descriptors. The Control Plane is absent.

## Verification

```sh
python -m pip install -r tests/private_analytics/requirements.txt
python -m unittest discover -s tests/private_analytics -p 'test_*.py' -v
npm test
sudo -E $(which python) tests/private_analytics/run_integration.py
```

The final command requires Linux Docker. It uses isolated temporary synthetic sources, creates S1 through M2/M2.5, destroys both containers, removes the CSVs, creates S2 from encrypted shares only, destroys both containers again, reloads S2 and reveals only the authorized mean. It attempts a denied CROSS_MEAN request and checks S1 byte-for-byte, identical public state documents, distinct local keys, exactly one local envelope per logical artifact per node, no source mounts, and no identifier output.

A separate synthetic correctness scenario explicitly authorizes all six scalars before creating S1; the expected values exist only in test assertions. This checks COUNT, both SUMs, both MEANs and cross-party CROSS_MEAN with actual SPU arithmetic. It does not broaden the acceptance fixture's policy.

## Limits

Two semi-honest non-colluding parties on trusted hosts; demo transport lacks production authentication. Public shapes, capacities, policies, neutral feature selectors, cardinality, commitments and authorized scalar outputs leak metadata. Repeated-query inference is not constrained. State and transition hashes are unsigned; a malicious host can rewrite documents and hashes. Node-local key files have no KMS/HSM, rotation, recovery, anti-rollback or distributed atomic commit. Key epoch is fixed to `room-state-v1`; wrong keys fail AES-GCM authentication. Context migration, additional joins, multi-state analytics, ML, FHE, proofs and UI are outside M3.

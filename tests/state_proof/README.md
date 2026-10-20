# M5 state-transition proof tests

This directory contains the fast relation checks and the explicit CPU Groth16
acceptance path for the bounded M5 statement.

The expensive acceptance workflow must be rerun when the guest, relation,
witness construction, canonicalization, public values, verifier cryptographic
material, or release-acceptance requirements change. In particular, a change to
RoomState fixtures or schemas that changes the committed public values requires
fresh acceptance evidence even when the SP1 guest source is unchanged.

Routine unrelated documentation and downstream M7 changes do not require a new
proof.

# SecretFlow SPU private join

Milestone 2 performs identifier equality and row alignment inside a two-party
SecretFlow SPU computation. It does not call SecretFlow's receiver-oriented PSI
APIs, because those APIs materialize matched rows at one or both participants.

Each KryptNode locally encodes its identifiers into a public fixed-width byte
shape, then transfers the resulting tensor directly from its PYU to the SPU.
The SPU returns three secret objects: a match mask, masked Lab A features, and
masked Lab B features. The mask is passed into a second SPU computation that
reconstructs only the authorized intersection cardinality. Identifiers are not
included in the handoff.

The join grid is deliberately fixed at the public capacity in the job manifest.
This prevents match positions or the true local row count from being exposed by
an output shape, at the cost of O(n*m) equality work. This implementation is a
small-data correctness milestone, not a scalable production join.

The runtime uses `CHEETAH` with `FM128`. `SEMI2K` remains a long-term target,
but its default trusted-first-party Beaver provider does not satisfy the current
two-party non-collusion model. No ML is implemented in this milestone.

## Run

The demo requires Docker with Linux containers and Docker Compose:

```bash
docker compose -f compose.private-join.yml up --pull always --abort-on-container-exit
```

Each service mounts only its own synthetic input file. The image is pinned to
the official SecretFlow 1.14.0b0 Linux/amd64 digest. SecretFlow 1.14 requires
Python 3.10 or 3.11; it does not support Python 3.12.

This remains pre-release research software. The SecretFlow 1.14.0b0 release is
a beta and is not approved here for real medical or regulated data.

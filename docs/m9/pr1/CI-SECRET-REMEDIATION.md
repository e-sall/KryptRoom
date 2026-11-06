# PR23 — native Linux secret delivery and bootstrap remediation

The hosted run on `721a235` rejected the migration configuration. Native Linux
reproduction established that operator-owned `0600` bind-mounted files were
unreadable by UID 10001. Earlier WSL `/mnt/c` validation exposed `0777` DrvFS
metadata and did not verify this POSIX condition. Those historical results remain
preserved, but do not establish native permission acceptance.

## Bounded correction

Canonical operator secrets remain `0600` in private `0700` directories. An offline,
one-shot preparer reads the three declared files and projects owner-only `0400`
copies into isolated volumes: PostgreSQL UID 999; migrate, API and tests UID 10001.
All consumer mounts are read-only and contain only their declared credentials.
Directories are `0700`. The API and migrations never run as root.

Only the preparer runs as root, with CHOWN and DAC_OVERRIDE, no network, no new
privileges and a read-only root filesystem. These two capabilities are limited to
reading the private input mounts and assigning the output volumes' ownership.
It has no Docker socket, repository mount or application process. All consumers
depend on successful preparation. Existing wrong metadata, unexpected files or
changed values are refused; no implicit repair or rotation is performed.

PostgreSQL reads and validates both application credentials before its first SQL.
Separate assignments preserve failed-read status, unlike `export VAR=$(cat ...)`.
Missing, unreadable, empty, malformed and wrongly owned/permitted credentials stop
initialization. SCRAM-SHA-256, SQL roles and privileges, schema and migrations are
unchanged. Password values are never diagnostics.

## Acceptance and review boundaries

The existing lifecycle command additionally verifies actual UID 10001 access for
migrate/API/tests, read-only mounts, foreign-UID refusal, SCRAM role passwords,
five source-input negatives, and six real PostgreSQL bootstrap negatives. Each
negative starts a fresh PostgreSQL 17 volume and inspects it afterward with the
same official image to establish that neither application role was created.

The original five PostgreSQL tests, unit tests, readiness/outage/restart chain,
locks, Ruff, mypy, builds and audits remain required. Linux/POSIX storage is
mandatory for this Compose profile; mode emulation on Windows storage is refused.

QA04-01 identified that bounded diagnostics had also truncated the leak scan.
The scan now reads all available Compose logs, including stderr, without printing
them. Only failure diagnostics use a bounded tail, redacted before display. Three
regressions cover an early sentinel followed by more than 200 ordinary lines,
stderr, and failure-output redaction; a leak must never report a passed scan.

This is local/CI credential delivery, not a production secret manager. Host root
and Docker daemon operators remain trusted. No business authority, endpoint,
cryptographic authorization, M1–M8 component, dependency lock or workflow recipe
changes. The M9 recipe hash remains the reviewed explicit-scope recipe; no
frontend exception or cryptographic check bypass is introduced.

The targeted 04 review, exact correction SHA, native results and hosted CI outcome
are recorded in the publication evidence/report. No merge or deployment is
authorized by this document.

# Security policy

KryptRoom is an experimental research prototype, not a production-ready or independently audited security product. There are no supported production releases or guaranteed response times.

## Reporting a vulnerability

Do not publish exploit details, credentials, encryption keys, private datasets, or sensitive logs in a public issue or pull request.

If this repository's GitHub Security tab offers **Report a vulnerability**, use that private reporting channel. Its availability depends on repository settings; this document does not imply that it is enabled. If unavailable, open a minimal issue requesting a private reporting channel without including vulnerability details. Wait for an agreed private channel before sharing sensitive material.

Include the affected commit and component, expected versus observed behavior, and a minimal synthetic reproduction. Redact secrets and identifying data. Do not test against third-party systems or real patient data.

## Security boundaries

- The protocol model is two-party honest-but-curious (semi-honest), not malicious security.
- Neither participant is authorized to receive matched identifiers or plaintext joined rows. Cardinality is an intentional disclosure; the M2.5 continuity fixture additionally authorizes a specific aggregate to both labs.
- Demo transport has no production peer authentication. Host compromise, collusion, side channels, and repeated-query inference are not prevented.
- M2.5's encrypted persistence and restart/reload continuity are verified on the synthetic CI fixture. Local key files are not a production KMS/HSM; rotation, recovery, anti-rollback, and crash-atomic multi-party commits are not implemented.
- Unsigned state commitments are content identifiers, not proofs of correct computation or protection against a malicious host rewriting state.

See [the threat model](THREAT_MODEL.md), [architecture](ARCHITECTURE.md), and [current validation status](README.md). Passing tests covers their fixtures, not a general security audit.

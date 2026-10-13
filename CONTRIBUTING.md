# Contributing

KryptRoom is an experimental, milestone-driven project. Discuss substantial changes in an issue before implementation. No project license has been selected: public visibility is not a general reuse grant. Resolve contribution and licensing terms with the maintainer before submitting substantial code; no CLA or contributor license is implied here.

## Scope and evidence

Read [AGENTS.md](AGENTS.md), [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [the threat model](THREAT_MODEL.md), and [architectural decisions](docs/DECISIONS.md). Use a dedicated branch and a focused pull request. Do not merge until required CI passes and the maintainer approves.

Preserve the no-identifier-disclosure default. Never substitute mocks or plaintext computation for a cryptographic integration test. Keep runtime images and dependencies pinned; explain any backend, trust-model, or output-policy change explicitly. Use synthetic fixtures only. Never commit keys, private datasets, local state, credentials, or sensitive protocol traces.

## Checks

Use Node.js 22, matching CI:

```sh
npm ci --ignore-scripts
npm test
npm run demo:psi
```

The test suite includes integration, privacy, and reproducibility checks, but local Node tests do not establish successful SPU execution. Changes affecting cryptographic runtime or persistence also require the real Linux Docker integration gates described in [README.md](README.md) and [the MPC runtime guide](engines/mpc/README.md). M2.5's create/terminate/restart/reload gate has succeeded for the pinned synthetic fixture; future changes must keep that gate green.

Describe commands run, exact outcomes, skipped checks, and limitations in the pull request. Update relevant architecture, decisions, context, changelog, and milestone status when behavior changes. Report vulnerabilities through [SECURITY.md](SECURITY.md), not a public issue containing sensitive details.

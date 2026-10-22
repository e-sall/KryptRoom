# KryptRoom web — M8 PR1 / PR2

Next.js App Router, React, TypeScript and Tailwind foundation. **No workspace API,
authentication, participant data, cryptographic execution or chain integration.**
Every business module explicitly displays an unavailable state. The component
gallery is an interface example, not a simulated service.

PR2 adds `/preview/rooms` and `/preview/rooms/new`: explicitly synthetic
Rooms discovery and progressive setup. All data is fixed example metadata;
fields/view state live only in React memory. `/app/rooms/new` remains unavailable.
No invitation, connection, Room creation or policy write can occur, including
when every example field is complete. Workspace navigation stops at a PR3
unavailable page; no graph editor, computation, proof or result is implemented.

## Run locally

Use Node >=22.14 (CI: 22.22.0), npm 10.9.4 (also recorded in `packageManager`),
then from this directory. If your npm differs, use `npx npm@10.9.4 ci`:

```sh
npm ci
npm run dev
```

Open `http://127.0.0.1:3000/app/rooms`. Other entry points: `/` (P01 hero shell),
`/design-system` (isolated specimens). `npm run build` and `npm start` run the
production application. Set `NEXT_TELEMETRY_DISABLED=1` to disable Next telemetry.

## Validate

```sh
npm run lint
npm test
npm run build
npm run typecheck
npx playwright install chromium
npm run test:e2e
```

On Linux, use `npx playwright install --with-deps chromium`. Browser tests start
their own production server on port 3000; stop any existing server first.
HTML report: `playwright-report/index.html`. Screenshots/traces: `test-results/`.
These generated directories and all `.env*` files are ignored.

## Boundaries and extension points

- `src/styles/tokens.css`: semantic palette, type, spacing, motion and radii.
- `src/components/ui.tsx`, `brand.tsx`, `icon.tsx`, `dialog.tsx`: reusable primitives.
- `src/components/app-shell.tsx`: navigation, breadcrumb, focus, inspector and sheets.
- `src/lib/navigation.ts`: closed route catalog and explicit disconnected boundary.
- `src/app/app/[module]`: unavailable modules, ready for PR2–5 route-specific views.
- `src/app/[section]`: unavailable marketing/demo sections for PR6.
- `src/components/design-system-preview.tsx`: local presentation state only.
- `src/features/rooms`: isolated preview view models, context, components and CSS.
- `src/app/preview/rooms`: preview-only routes; never a production API fallback.

The app has its own exact-version package lock. Root PSI dependencies and core
workflows are unchanged. No shadcn generator, chart library, React Flow, global
store or fabricated API contract is installed before its actual need.

Do not turn a badge, UI route or disabled button into an authorization boundary.
Future integration must obtain authoritative access, proof and finality status
from a reviewed service. Never send raw participant data, keys or secret shares
to the browser or Control Plane. No `Verified` / `Finalized` variant is offered
by the PR1 badge API.

See [the implementation evidence](../../docs/m8/pr1/README.md) for source
provenance, deviations, executed checks and limitations.
See [PR2 evidence](../../docs/m8/pr2/README.md) for Rooms/Easy Setup and screenshots.

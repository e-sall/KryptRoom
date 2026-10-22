"use client";

import { useState } from "react";
import { Brand, KLogo } from "./brand";
import {
  Badge,
  Button,
  ButtonLink,
  Card,
  StatusView,
  TextField,
  type Status,
  type ViewState,
} from "./ui";
import { Dialog } from "./dialog";

const swatches = [
  ["Canvas", "--kr-background", "#10100F"],
  ["Surface", "--kr-surface", "#191918"],
  ["Elevated", "--kr-elevated", "#242422"],
  ["Border", "--kr-border", "#343432"],
  ["Primary", "--kr-text-primary", "#F1F0EB"],
  ["Secondary", "--kr-text-secondary", "#A9A9A2"],
  ["Blue", "--kr-blue", "#7CAAD5"],
  ["Blue muted", "--kr-blue-muted", "#334B60"],
  ["Action", "--kr-action", "#EDECE6"],
  ["Success color", "--kr-success", "#84B89A"],
  ["Warning", "--kr-warning", "#DBB477"],
] as const;

export function DesignSystemPreview() {
  const [state, setState] = useState<ViewState>("empty");
  const [open, setOpen] = useState(false);
  return (
    <main className="standalone-page" id="main-content">
      <div className="button-row mb-8">
        <Brand />
        <Badge status="preview" />
      </div>
      <p className="eyebrow">M8 · FOUNDATION</p>
      <h1>Design system</h1>
      <p>
        Component examples only. No Room, backend request or cryptographic
        operation.
      </p>
      <ButtonLink href="/app/rooms">Open app shell</ButtonLink>
      <Card className="specimen">
        <h2>Identity</h2>
        <div className="button-row">
          <KLogo size={16} />
          <KLogo size={24} />
          <KLogo size={32} />
          <Brand />
        </div>
        <p className="caption mt-4">
          P01 / P04 · Light stem, two gray branches.
        </p>
      </Card>
      <Card className="specimen">
        <h2>Color</h2>
        <div className="swatches">
          {swatches.map(([label, variable, value]) => (
            <div className="swatch" key={variable}>
              <div
                className="swatch-color"
                style={{ background: `var(${variable})` }}
              />
              <span>{label}</span>
              <code>{value}</code>
            </div>
          ))}
        </div>
        <p className="caption mt-6">
          The success swatch is a color specimen, not a verification verdict.
        </p>
      </Card>
      <Card className="specimen">
        <h2>Typography</h2>
        <div className="type-specimens">
          <p className="font-serif text-3xl">
            Compute together. Reveal nothing.
          </p>
          <p className="font-sans">
            Your private collaborations, in one place.
          </p>
          <p className="font-mono text-sm">RoomState · metadata reference</p>
        </div>
      </Card>
      <Card className="specimen">
        <h2>Buttons</h2>
        <div className="button-row">
          <Button variant="primary" onClick={() => setOpen(true)}>
            Open example dialog
          </Button>
          <Button onClick={() => setState("empty")}>Reset examples</Button>
          <Button variant="ghost" onClick={() => setState("error")}>
            Show error example
          </Button>
          <Button disabled>Unavailable action</Button>
          <Button loading>Loading example</Button>
        </div>
      </Card>
      <Card className="specimen">
        <h2>Statuses</h2>
        <div className="button-row">
          {(
            [
              "unavailable",
              "unknown",
              "not-assessed",
              "pending",
              "blocked",
              "error",
              "preview",
            ] as Status[]
          ).map((status) => (
            <Badge key={status} status={status} />
          ))}
        </div>
        <p className="caption mt-4">
          Visual specimens. No verification, finality or authorization is
          implied.
        </p>
      </Card>
      <Card className="specimen">
        <h2>Fields</h2>
        <TextField
          id="example-field"
          label="Example field"
          placeholder="Interface example"
          hint="Local presentation only; this field is never submitted."
        />
        <div className="mt-6">
          <TextField
            id="disabled-field"
            label="Unavailable field"
            disabled
            hint="Workspace service required."
          />
        </div>
      </Card>
      <Card className="specimen">
        <h2>System states</h2>
        <div
          className="segmented-control"
          role="group"
          aria-label="Example state"
        >
          {(
            [
              "empty",
              "loading",
              "blocked",
              "error",
              "unavailable",
            ] as ViewState[]
          ).map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={state === value}
              onClick={() => setState(value)}
            >
              {value[0].toUpperCase() + value.slice(1)}
            </button>
          ))}
        </div>
        <StatusView state={state} />
      </Card>
      <Dialog open={open} onClose={() => setOpen(false)} title="Example dialog">
        <p>
          This dialog demonstrates keyboard focus containment and Escape
          dismissal.
        </p>
        <TextField id="dialog-example" label="Example input" />
        <div className="button-row mt-6">
          <Button onClick={() => setOpen(false)}>Close example</Button>
        </div>
      </Dialog>
    </main>
  );
}

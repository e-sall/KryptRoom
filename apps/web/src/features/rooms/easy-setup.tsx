"use client";
import { useId, useRef, useState } from "react";
import { Badge, Button, Card, TextField } from "@/components/ui";
import { useRoomsPreview } from "./preview-context";
import {
  emptyDraft,
  previewGate,
  setupSteps,
  validateStep,
} from "./preview-model";
import { ExampleBadge } from "./room-details";

export function Readiness() {
  const reasonId = useId();
  const { step, setStep, draft } = useRoomsPreview();
  return (
    <div className="inspector-content readiness">
      <p className="eyebrow">ROOM READINESS</p>
      <h2>Setup checklist</h2>
      <p className="caption">
        Configure at your own pace. Draft fields are not service
        acknowledgments.
      </p>
      <ol>
        {setupSteps.map((label, index) => (
          <li key={label}>
            <button
              type="button"
              onClick={() => setStep(index)}
              aria-current={step === index ? "step" : undefined}
            >
              <span className="step-number">{index + 1}</span>
              <span>
                {label}
                <small>
                  {index === 0 && draft.name
                    ? "Example identity entered · not created"
                    : "Authority unavailable"}
                </small>
              </span>
            </button>
          </li>
        ))}
      </ol>
      <Badge status="blocked" />
      <p className="caption" id={reasonId}>
        {previewGate().reason}
      </p>
      <Button disabled aria-describedby={reasonId}>
        Run Computation
      </Button>
    </div>
  );
}
export function EasySetup() {
  const { draft, setDraft, step, setStep } = useRoomsPreview();
  const [validation, setValidation] = useState<{
    step: number;
    message: string | null;
  }>({ step: 0, message: null });
  const error = validation.step === step ? validation.message : null;
  function setError(message: string | null) {
    setValidation({ step, message });
  }
  const [notice, setNotice] = useState("");
  const formRef = useRef<HTMLFormElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  function field(key: keyof typeof draft, value: string) {
    setDraft({ ...draft, [key]: value });
    setError(null);
    setNotice("");
  }
  function move(next: number, validate: boolean) {
    const message = validate ? validateStep(step, draft) : null;
    setError(message);
    setNotice("");
    if (message) {
      formRef.current
        ?.querySelector<HTMLInputElement>(
          step === 0
            ? "#room-name"
            : step === 1
              ? "#organization"
              : "#source-ref",
        )
        ?.focus();
      return;
    }
    setStep(next);
    heading.current?.focus();
  }
  const titles = [
    "A space for private collaboration.",
    "Bring your partners in.",
    "Your data stays yours.",
    "Define what can be revealed.",
  ];
  return (
    <section className="easy-setup">
      <nav className="setup-steps" aria-label="Setup steps">
        {setupSteps.map((label, index) => (
          <button
            key={label}
            type="button"
            aria-current={step === index ? "step" : undefined}
            onClick={() => move(index, false)}
          >
            <span className="step-number">{index + 1}</span>
            {label}
          </button>
        ))}
      </nav>
      <Card className="setup-card">
        <p className="eyebrow">
          0{step + 1} / {setupSteps[step].toUpperCase()}
        </p>
        <h2 ref={heading} tabIndex={-1}>
          {titles[step]}
        </h2>
        <p className="caption">
          Example values only. Fields stay in this preview’s memory until reload
          or exit. Nothing is sent or saved.
        </p>
        <form
          ref={formRef}
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            if (step < 3) move(step + 1, true);
          }}
        >
          {error && (
            <p className="form-error" id="setup-error" role="alert">
              {error}
            </p>
          )}
          {step === 0 && (
            <>
              <TextField
                id="room-name"
                label="Room name"
                required
                maxLength={80}
                value={draft.name}
                onChange={(e) => field("name", e.target.value)}
                aria-invalid={!!error}
                hint={
                  error ??
                  "3–80 characters. Use a fictional collaboration name."
                }
                autoComplete="off"
              />
              <div className="field">
                <label htmlFor="room-description">Description (optional)</label>
                <textarea
                  id="room-description"
                  maxLength={280}
                  rows={3}
                  value={draft.description}
                  onChange={(e) => field("description", e.target.value)}
                  aria-describedby="description-hint"
                />
                <p id="description-hint" className="caption">
                  {draft.description.length}/280 · No sensitive information.
                </p>
              </div>
              <div className="policy-row">
                <span>Initial visibility</span>
                <strong>Restricted</strong>
              </div>
              <p className="caption">
                Explore identity first, then complete prerequisites
                progressively. No Room has been created.
              </p>
              <Button disabled>Create Room</Button>
            </>
          )}
          {step === 1 && (
            <>
              <div className="policy-row">
                <span>
                  Example Organization A<small>Room owner · fictional</small>
                </span>
                <ExampleBadge>Owner</ExampleBadge>
              </div>
              <TextField
                id="organization"
                label="Organization name (optional)"
                value={draft.organization}
                maxLength={80}
                onChange={(e) => field("organization", e.target.value)}
                autoComplete="off"
                aria-invalid={!!error}
                hint={
                  error ??
                  "Leave invitations for later, or enter an example organization."
                }
              />
              <TextField
                id="organization-email"
                label="Invite by organization email"
                type="email"
                value={draft.email}
                maxLength={120}
                onChange={(e) => field("email", e.target.value)}
                placeholder="partner@example.invalid"
                autoComplete="off"
                aria-invalid={!!error}
              />
              <Button disabled>Send invitation</Button>
              <p className="caption">
                Invitation service unavailable. No invitation is sent and no
                participant is added.
              </p>
              <details className="example-statuses">
                <summary>Invitation status examples</summary>
                <p className="caption">
                  Fixed display examples, unrelated to your draft.
                </p>
                {["Pending", "Accepted", "Blocked", "Unavailable"].map((s) => (
                  <ExampleBadge key={s}>{s}</ExampleBadge>
                ))}
              </details>
            </>
          )}
          {step === 2 && (
            <>
              <div className="field">
                <label htmlFor="source-owner">
                  Owning organization · example
                </label>
                <select
                  id="source-owner"
                  value={draft.owner}
                  onChange={(e) => field("owner", e.target.value)}
                >
                  <option>Example Organization A</option>
                  <option>Example Organization B</option>
                </select>
              </div>
              <TextField
                id="source-ref"
                label="Opaque example reference (optional)"
                value={draft.source}
                maxLength={56}
                onChange={(e) => field("source", e.target.value)}
                placeholder="example-source-a"
                autoComplete="off"
                aria-invalid={!!error}
                hint={
                  error ??
                  "Only example-* aliases. No file paths, URLs, credentials, raw rows or uploads."
                }
              />
              <div className="policy-row">
                <span>
                  {draft.owner}
                  <small>Local connector · not contacted</small>
                </span>
                <Badge status="unavailable" />
              </div>
              <div className="protected-note">
                <h3>Protected connection</h3>
                <p className="caption">
                  Each organization manages its source on its own KryptNode.
                  This preview reads no files and uploads no raw dataset to the
                  Control Plane.
                </p>
              </div>
              <Button disabled>Connect data source</Button>
              <details className="example-statuses">
                <summary>Connection status examples</summary>
                {[
                  "Awaiting connection",
                  "Invitation pending",
                  "Blocked",
                  "Unavailable",
                ].map((s) => (
                  <ExampleBadge key={s}>{s}</ExampleBadge>
                ))}
              </details>
            </>
          )}
          {step === 3 && (
            <>
              <div className="field">
                <label htmlFor="disclosure">
                  Output disclosure · draft preference only
                </label>
                <select
                  id="disclosure"
                  value={draft.disclosure}
                  onChange={(e) => field("disclosure", e.target.value)}
                >
                  <option value="deny">Deny by default</option>
                  <option value="request-aggregate">
                    Request aggregate-only review
                  </option>
                </select>
              </div>
              <p className="caption">
                A preference grants nothing. Any future disclosure needs a
                separate, precise, server-authorized policy. Matched
                identifiers, joined rows and model parameters remain private.
              </p>
              <div className="policy-row">
                <span>
                  Computation approval
                  <small>Participating organizations approve access</small>
                </span>
                <strong>Required</strong>
              </div>
              <div className="policy-row">
                <span>
                  Access authorization
                  <small>No authenticated participant context</small>
                </span>
                <Badge status="unavailable" />
              </div>
              <div className="policy-row">
                <span>Proof & provenance</span>
                <Badge status="not-assessed" />
              </div>
              <Button disabled>Save Room policy</Button>
              <Button
                onClick={() => {
                  const invalid = [0, 1, 2]
                    .map((i) => validateStep(i, draft))
                    .find(Boolean);
                  setNotice(
                    invalid
                      ? `Draft incomplete: ${invalid}`
                      : "Example fields reviewed. No Room or policy was saved; execution remains blocked.",
                  );
                }}
              >
                Review example fields
              </Button>
            </>
          )}
          <p role="status" className="caption">
            {notice}
          </p>
          <div className="setup-navigation">
            <Button disabled={step === 0} onClick={() => move(step - 1, false)}>
              Back
            </Button>
            {step < 3 && (
              <Button variant="primary" type="submit">
                Continue preview
              </Button>
            )}
          </div>
        </form>
        <Button
          variant="ghost"
          onClick={() => {
            setDraft({ ...emptyDraft });
            setStep(0);
            setError(null);
            setNotice("Example fields cleared.");
          }}
        >
          Reset example fields
        </Button>
      </Card>
    </section>
  );
}

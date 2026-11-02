import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
  InputHTMLAttributes,
  ReactNode,
} from "react";
import Link from "next/link";
import { Icon } from "./icon";

export type ButtonVariant = "primary" | "secondary" | "ghost";
export function Button({
  variant = "secondary",
  loading = false,
  disabled,
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  loading?: boolean;
}) {
  return (
    <button
      {...props}
      type={props.type ?? "button"}
      className={`button button-${variant} ${className}`}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
    >
      {loading && <span className="spinner" aria-hidden="true" />}
      {children}
    </button>
  );
}
export function ButtonLink({
  href,
  children,
  variant = "secondary",
}: {
  href: string;
  children: ReactNode;
  variant?: ButtonVariant;
}) {
  return (
    <Link prefetch={false} href={href} className={`button button-${variant}`}>
      {children}
    </Link>
  );
}

/** Presentation only. No success verdicts are inferred or offered in PR1. */
export type Status =
  | "unavailable"
  | "unknown"
  | "not-assessed"
  | "pending"
  | "blocked"
  | "error"
  | "preview";
const statusLabels: Record<Status, string> = {
  unavailable: "Unavailable",
  unknown: "Unknown",
  "not-assessed": "Not assessed",
  pending: "Pending",
  blocked: "Blocked",
  error: "Error",
  preview: "Interface preview",
};
export function Badge({ status }: { status: Status }) {
  return (
    <span className={`badge badge-${status}`}>
      <span className="badge-dot" aria-hidden="true" />
      {statusLabels[status]}
    </span>
  );
}
export function Card({
  className = "",
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div {...props} className={`card ${className}`}>
      {children}
    </div>
  );
}
export function TextField({
  label,
  hint,
  id,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  hint?: string;
  id: string;
}) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        {...props}
        id={id}
        aria-describedby={hint ? `${id}-hint` : undefined}
      />
      {hint && (
        <p id={`${id}-hint`} className="caption">
          {hint}
        </p>
      )}
    </div>
  );
}
export type ViewState =
  | "empty"
  | "loading"
  | "blocked"
  | "error"
  | "unavailable";
const stateCopy: Record<ViewState, { title: string; description: string }> = {
  empty: {
    title: "Nothing here yet",
    description: "This interface example contains no room data.",
  },
  loading: {
    title: "Loading interface example",
    description: "Indeterminate preview. No computation is running.",
  },
  blocked: {
    title: "Action unavailable",
    description:
      "This is a blocked-state example. No permission decision has been received.",
  },
  error: {
    title: "Unable to load this example",
    description:
      "This is an error-state example. No private diagnostic data is displayed.",
  },
  unavailable: {
    title: "A space for your collaborations",
    description:
      "Rooms will appear here when an authenticated workspace service is connected.",
  },
};
export function StatusView({
  state,
  title,
  description,
  action,
}: {
  state: ViewState;
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  const copy = stateCopy[state];
  return (
    <div
      className={`status-view status-view-${state}`}
      role={state === "error" ? "alert" : "status"}
      aria-live="polite"
    >
      <span className="status-icon" aria-hidden="true">
        {state === "loading" ? (
          <span className="spinner" />
        ) : (
          <Icon
            name={
              state === "unavailable" || state === "empty" ? "rooms" : "info"
            }
          />
        )}
      </span>
      <h2>{title ?? copy.title}</h2>
      <p>{description ?? copy.description}</p>
      {action}
    </div>
  );
}

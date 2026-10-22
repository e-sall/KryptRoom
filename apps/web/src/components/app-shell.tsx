"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Brand, KLogo } from "./brand";
import { Icon } from "./icon";
import { Badge, Button } from "./ui";
import { Dialog } from "./dialog";
import {
  findModule,
  modules,
  moduleHref,
  workspaceConnection,
} from "@/lib/navigation";

function Inspector({ moduleId }: { moduleId: string }) {
  const current = findModule(moduleId);
  return (
    <div className="inspector-content">
      <p className="eyebrow">CONTEXT</p>
      <h2>Workspace details</h2>
      <p className="inspector-intro">
        A persistent space for private collaboration.
      </p>
      <dl>
        <div>
          <dt>Current view</dt>
          <dd>{current?.title ?? "Workspace"}</dd>
        </div>
        <div>
          <dt>Room</dt>
          <dd>No room selected</dd>
        </div>
        <div>
          <dt>Connection</dt>
          <dd>
            <Badge status="unavailable" />
          </dd>
        </div>
        <div>
          <dt>Implementation</dt>
          <dd>{current?.milestone ?? "PR 1 · Foundation"}</dd>
        </div>
      </dl>
      <div className="inspector-note">
        <Icon name="info" />
        <p>{workspaceConnection.reason}</p>
      </div>
      <p className="caption">
        Access and disclosure decisions will come from the authenticated
        service.
      </p>
    </div>
  );
}

export function AppShell({
  children,
  inspector,
  contextLabel = "No room selected",
  preview = false,
  pageHeader,
  activeModule,
  graphHref,
}: {
  children: ReactNode;
  inspector?: ReactNode;
  contextLabel?: string;
  preview?: boolean;
  pageHeader?: ReactNode;
  activeModule?: string;
  graphHref?: string;
}) {
  const pathname = usePathname();
  const moduleId = activeModule ?? pathname.split("/")[2] ?? "rooms";
  const current = findModule(moduleId);
  const [panel, setPanel] = useState<"details" | "navigation" | null>(null);
  const mainRef = useRef<HTMLElement>(null);
  const previousPath = useRef(pathname);
  useEffect(() => {
    if (preview || previousPath.current !== pathname) {
      mainRef.current?.focus({ preventScroll: true });
      previousPath.current = pathname;
    }
  }, [pathname, preview]);
  const navLink = (item: (typeof modules)[number], compact = false) => (
    <Link
      key={item.id}
      href={
        preview && item.id === "rooms" ? "/preview/rooms" : preview && item.id === "graph" && graphHref ? graphHref : moduleHref(item.id)
      }
      className="nav-link"
      aria-current={moduleId === item.id ? "page" : undefined}
      aria-label={compact ? item.label : undefined}
      title={compact ? item.label : undefined}
      onClick={() => setPanel(null)}
    >
      <Icon name={item.icon} />
      <span>{item.label}</span>
    </Link>
  );
  return (
    <div className={`app-frame${preview ? " rooms-preview-frame" : ""}`}>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <aside className="sidebar" aria-label="Workspace sidebar">
        <Brand compact />
        <div className="sidebar-divider" />
        <p className="eyebrow sidebar-label">WORKSPACE</p>
        <nav aria-label="Workspace navigation">
          {navLink(modules[0], true)}
          <div className="nav-section-label">EXPLORE</div>
          {modules.slice(1).map((item) => navLink(item, true))}
        </nav>
        <div className="sidebar-footer">
          <span className="workspace-avatar" aria-hidden="true">
            KR
          </span>
          <div>
            <strong>Workspace</strong>
            <span>Interface preview</span>
          </div>
        </div>
        <Link
          href="/design-system"
          className="foundation-link"
          aria-label="Design system"
        >
          <Icon name="info" />
          <span>Design system</span>
        </Link>
      </aside>
      <div className="app-body">
        <header className="topbar">
          <div className="mobile-brand">
            <Link href="/" aria-label="KryptRoom home">
              <KLogo />
            </Link>
          </div>
          <nav aria-label="Breadcrumb">
            <ol className="breadcrumbs">
              <li>
                <Link href={preview ? "/preview/rooms" : "/app/rooms"}>
                  {preview ? "Design preview" : "Workspace"}
                </Link>
              </li>
              <li aria-hidden="true">/</li>
              <li aria-current="page">{current?.label ?? "Workspace"}</li>
            </ol>
          </nav>
          {preview ? (
            <span className="badge badge-preview">SYNTHETIC PREVIEW</span>
          ) : (
            <Badge status="preview" />
          )}
        </header>
        {pageHeader && (
          <div className="workspace-page-header">{pageHeader}</div>
        )}
        <div className="workspace-grid">
          <main
            id="main-content"
            ref={mainRef}
            tabIndex={-1}
            className="workspace-main"
          >
            {children}
            <div className="mobile-details-preview">
              <p className="eyebrow">CONTEXT</p>
              <p>{contextLabel}</p>
              <Button
                onClick={() => setPanel("details")}
                aria-haspopup="dialog"
              >
                Workspace details <Icon name="arrow" />
              </Button>
            </div>
          </main>
          <aside className="context-inspector" aria-label="Context inspector">
            {inspector ?? <Inspector moduleId={moduleId} />}
          </aside>
        </div>
      </div>
      <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
        {[modules[0], modules[1], modules[7]].map((item) => navLink(item))}
        <button
          className="nav-link"
          type="button"
          aria-haspopup="dialog"
          onClick={() => setPanel("navigation")}
          aria-label="More navigation"
        >
          <Icon name="menu" />
          <span>More</span>
        </button>
      </nav>
      <Dialog
        open={panel === "details"}
        onClose={() => setPanel(null)}
        title="Workspace details"
        className="bottom-sheet"
      >
        {inspector ?? <Inspector moduleId={moduleId} />}
      </Dialog>
      <Dialog
        open={panel === "navigation"}
        onClose={() => setPanel(null)}
        title="Navigation"
        className="bottom-sheet"
      >
        <nav className="sheet-navigation" aria-label="All modules">
          {modules.map((item) => navLink(item))}
          <Link href="/design-system" onClick={() => setPanel(null)}>
            Design system
          </Link>
        </nav>
      </Dialog>
    </div>
  );
}

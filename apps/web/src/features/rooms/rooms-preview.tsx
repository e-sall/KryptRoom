"use client";
import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import {
  Button,
  ButtonLink,
  Card,
  StatusView,
  TextField,
  type ViewState,
} from "@/components/ui";
import { useRoomsPreview } from "./preview-context";
import { exampleRooms, filterRooms } from "./preview-model";
import { ExampleBadge, MiniHistory, RoomDetails } from "./room-details";
import { EasySetup, Readiness } from "./easy-setup";

export function RoomsPreview({
  screen = "home",
  roomId,
}: {
  screen?: "home" | "detail" | "setup" | "workspace";
  roomId?: string;
}) {
  const state = useRoomsPreview();
  const [scenario, setScenario] = useState<"normal" | ViewState>("normal");
  const rooms = filterRooms(state.query, state.status);
  const selected =
    screen === "home"
      ? (rooms.find((room) => room.id === state.selected) ?? rooms[0])
      : exampleRooms.find((room) => room.id === roomId);
  const visibleRoom =
    scenario === "normal" && screen !== "setup" ? selected : undefined;
  const inspector =
    screen === "setup" ? (
      <Readiness />
    ) : visibleRoom ? (
      <RoomDetails room={visibleRoom} />
    ) : (
      <div className="inspector-content">
        <h2>No example selected</h2>
        <p className="caption">
          {scenario === "normal"
            ? "Choose an example collaboration."
            : `Example ${scenario} state. No Room metadata displayed.`}
        </p>
      </div>
    );
  function expand(id: string) {
    state.setSelected(id);
    state.setExpanded(
      state.expanded.includes(id)
        ? state.expanded.filter((item) => item !== id)
        : [...state.expanded, id],
    );
  }
  const header = (
    <>
      <div className="preview-boundary">
        <strong>Synthetic design preview</strong>
        <p>
          No real Rooms, invitations, connections or permissions. Use fictional
          input only.
        </p>
        <Link href="/app/rooms">Exit to application</Link>
      </div>
      <div className="page-heading">
        <div>
          <h1>
            {screen === "home"
              ? "Rooms"
              : screen === "setup"
                ? "Create a Room"
                : screen === "workspace"
                  ? "Workspace unavailable"
                  : selected?.name}
          </h1>
          <p className="page-description">
            {screen === "home"
              ? "Your private collaborations, in one place."
              : screen === "setup"
                ? "Start simply. Complete prerequisites at your own pace."
                : "Illustrative collaboration · no authenticated service"}
          </p>
        </div>
        {screen === "home" ? (
          <ButtonLink href="/preview/rooms/new" variant="primary">
            Create Room preview
          </ButtonLink>
        ) : (
          <ButtonLink href="/preview/rooms">All example Rooms</ButtonLink>
        )}
      </div>
      {screen === "home" && (
        <>
          <div className="rooms-toolbar">
            <TextField
              label="Search Rooms"
              id="room-search"
              value={state.query}
              onChange={(e) => state.setQuery(e.target.value)}
              placeholder="Search rooms…"
              type="search"
            />
            <div className="field">
              <label htmlFor="room-status">Status</label>
              <select
                id="room-status"
                value={state.status}
                onChange={(e) => state.setStatus(e.target.value)}
              >
                <option value="all">All statuses</option>
                {["Active", "Setup required", "Ready"].map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </div>
            <div
              className="segmented-control"
              role="group"
              aria-label="Room view"
            >
              {(["list", "cards"] as const).map((view) => (
                <button
                  key={view}
                  type="button"
                  aria-pressed={state.view === view}
                  onClick={() => state.setView(view)}
                >
                  {view === "list" ? "List" : "Cards"}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </>
  );
  return (
    <AppShell
      preview
      pageHeader={header}
      inspector={inspector}
      contextLabel={
        screen === "setup"
          ? "Setup checklist · not authorized"
          : (visibleRoom?.name ?? "No example selected")
      }
    >
      {screen === "home" && (
        <>
          <div className="section-bar">
            <span>YOUR COLLABORATIONS</span>
            <span role="status">
              {scenario === "normal" ? rooms.length : 0} example Rooms
            </span>
          </div>
          {scenario === "normal" && rooms.length > 0 ? (
            <div className={`rooms-${state.view}`}>
              {state.view === "list" && (
                <div className="room-columns" aria-hidden="true">
                  <span>ROOM</span>
                  <span>PARTICIPANTS</span>
                  <span>STATUS / ACTIVITY</span>
                  <span>STATE</span>
                </div>
              )}
              {rooms.map((room) => (
                <Card
                  key={room.id}
                  className={`room-item ${visibleRoom?.id === room.id ? "room-selected" : ""}`}
                >
                  <button
                    type="button"
                    className="room-select"
                    aria-label={`${state.view === "list" ? "Expand" : "Select"} ${room.name}`}
                    aria-expanded={
                      state.view === "list"
                        ? state.expanded.includes(room.id)
                        : undefined
                    }
                    aria-controls={
                      state.view === "list" ? `expansion-${room.id}` : undefined
                    }
                    aria-pressed={
                      state.view === "cards"
                        ? visibleRoom?.id === room.id
                        : undefined
                    }
                    onClick={() =>
                      state.view === "list"
                        ? expand(room.id)
                        : state.setSelected(room.id)
                    }
                  >
                    <span className="room-name">
                      <strong>{room.name}</strong>
                      <small>{room.summary}</small>
                    </span>
                    <span className="room-participants">
                      {room.organizations.length} organizations
                    </span>
                    <span className="room-status">
                      <ExampleBadge>{room.status}</ExampleBadge>
                      <small>{room.activity}</small>
                    </span>
                    <span className="room-state">
                      {room.states.at(-1)?.id ?? "—"}
                      <span aria-hidden="true">
                        {" "}
                        {state.view === "list" &&
                        state.expanded.includes(room.id)
                          ? "−"
                          : "+"}
                      </span>
                    </span>
                  </button>
                  {state.view === "list" &&
                    state.expanded.includes(room.id) && (
                      <div
                        className="room-expansion"
                        id={`expansion-${room.id}`}
                      >
                        <MiniHistory room={room} />
                        <div>
                          <p className="eyebrow">ROOM SNAPSHOT · EXAMPLE</p>
                          <p>
                            Latest state: {room.states.at(-1)?.id ?? "None"}
                          </p>
                          <p className="caption">
                            {room.organizations.join(" · ")}
                          </p>
                          <ButtonLink href={`/preview/rooms/${room.id}`}>
                            View Room details
                          </ButtonLink>
                          <ButtonLink
                            href={`/preview/rooms/${room.id}/workspace`}
                          >
                            Open Workspace
                          </ButtonLink>
                        </div>
                      </div>
                    )}
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <StatusView
                state={scenario === "normal" ? "empty" : scenario}
                title={
                  scenario === "normal"
                    ? "No matching example Rooms"
                    : undefined
                }
                description={
                  scenario === "empty"
                    ? "Empty synthetic collection. This says nothing about real Rooms."
                    : undefined
                }
                action={
                  <Button
                    onClick={() => {
                      setScenario("normal");
                      state.setQuery("");
                      state.setStatus("all");
                    }}
                  >
                    Reset example view
                  </Button>
                }
              />
            </Card>
          )}
          <details className="scenario-controls">
            <summary>Preview system states</summary>
            <div
              className="segmented-control"
              role="group"
              aria-label="Preview system states"
            >
              {(
                [
                  "normal",
                  "empty",
                  "loading",
                  "blocked",
                  "error",
                  "unavailable",
                ] as const
              ).map((s) => (
                <button
                  key={s}
                  type="button"
                  aria-pressed={scenario === s}
                  onClick={() => setScenario(s)}
                >
                  {s}
                </button>
              ))}
            </div>
            <p className="caption">
              Display examples only, not service responses.
            </p>
          </details>
        </>
      )}
      {screen === "detail" && selected && (
        <Card className="detail-page">
          <RoomDetails room={selected} links={false} />
          <div className="button-row">
            <ButtonLink href={`/preview/rooms/${selected.id}/workspace`}>
              Open Workspace
            </ButtonLink>
            <ButtonLink href="/preview/rooms/new">
              Explore Easy Setup
            </ButtonLink>
          </div>
        </Card>
      )}
      {screen === "workspace" && (
        <Card>
          <StatusView
            state="unavailable"
            title="Graph Workspace is reserved for PR3"
            description="Navigation works, but no state graph, computation, result or proof service is implemented here."
            action={
              <ButtonLink href={`/preview/rooms/${roomId}`}>
                Back to Room details
              </ButtonLink>
            }
          />
        </Card>
      )}
      {screen === "setup" && <EasySetup />}
    </AppShell>
  );
}

import { useId } from "react";
import { Badge, ButtonLink } from "@/components/ui";
import type { ExampleRoom } from "./preview-model";

export function ExampleBadge({ children }: { children: string }) {
  return <span className="badge badge-preview">Example · {children}</span>;
}
export function MiniHistory({ room }: { room: ExampleRoom }) {
  const title = useId();
  if (!room.states.length)
    return (
      <p className="caption">No example states yet. Setup is incomplete.</p>
    );
  const positions = room.states.map((_, i) =>
    i === 0 ? { x: 12, y: 65 } : { x: 156, y: i === 1 ? 25 : 104 },
  );
  return (
    <figure className="mini-history">
      <figcaption className="eyebrow">STATE HISTORY · SYNTHETIC</figcaption>
      <svg viewBox="0 0 300 160" role="img" aria-labelledby={title}>
        <title id={title}>
          Illustrative lineage for {room.name}:{" "}
          {room.states
            .map(
              (s) =>
                `${s.id} ${s.label}, parents ${s.parent_state_ids.join(", ") || "none"}`,
            )
            .join("; ")}
          . Not a runtime record.
        </title>
        {room.states.flatMap((state, index) =>
          state.parent_state_ids.map((parent) => {
            const start =
              positions[room.states.findIndex((s) => s.id === parent)];
            const end = positions[index];
            return (
              <path
                key={`${parent}-${state.id}`}
                d={`M${start.x + 104} ${start.y + 18} C140 ${start.y + 18} 132 ${end.y + 18} ${end.x} ${end.y + 18}`}
                fill="none"
                stroke="var(--kr-blue)"
                strokeWidth="1.3"
              />
            );
          }),
        )}
        {room.states.map((state, index) => (
          <g
            key={state.id}
            transform={`translate(${positions[index].x} ${positions[index].y})`}
          >
            <rect
              width={index === 0 ? 104 : 132}
              height="36"
              rx="8"
              fill={
                index === room.states.length - 1
                  ? "var(--kr-blue-muted)"
                  : "var(--kr-selected)"
              }
              stroke="var(--kr-blue)"
            />
            <text x="10" y="22" fill="var(--kr-text-primary)" fontSize="11">
              {state.id} · {state.label}
            </text>
          </g>
        ))}
      </svg>
      <p className="caption">
        P03 illustrative topology, not M1–M7 lineage or proof.
      </p>
    </figure>
  );
}
export function RoomDetails({
  room,
  links = true,
}: {
  room: ExampleRoom;
  links?: boolean;
}) {
  return (
    <div className="room-details">
      <p className="eyebrow">SELECTED ROOM · EXAMPLE</p>
      <h2>{room.name}</h2>
      <p className="caption">
        {room.organizations.length} organizations · Private collaboration
      </p>
      <ExampleBadge>{room.status}</ExampleBadge>
      <MiniHistory room={room} />
      <dl className="room-facts">
        <div>
          <dt>Participants · fictional</dt>
          <dd>{room.organizations.join(" · ")}</dd>
        </div>
        <div>
          <dt>Latest example state</dt>
          <dd>{room.states.at(-1)?.id ?? "None"}</dd>
        </div>
        <div>
          <dt>Activity · illustrative</dt>
          <dd>{room.activity}</dd>
        </div>
        <div>
          <dt>Access / disclosure authority</dt>
          <dd>
            <Badge status="unavailable" />
          </dd>
        </div>
      </dl>
      {links && (
        <div className="room-links">
          <ButtonLink href={`/preview/rooms/${room.id}`}>
            View Room details
          </ButtonLink>
          <ButtonLink href={`/preview/rooms/${room.id}/workspace`}>
            Open Workspace
          </ButtonLink>
        </div>
      )}
    </div>
  );
}

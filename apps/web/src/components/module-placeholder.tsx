import { Badge, Button, ButtonLink, Card, StatusView } from "./ui";
import { Icon } from "./icon";
import type { Module } from "@/lib/navigation";

export function ModulePlaceholder({ module }: { module: Module }) {
  const rooms = module.id === "rooms";
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            {rooms ? "YOUR WORKSPACE" : "WORKSPACE MODULE"}
          </p>
          <h1>{module.title}</h1>
          <p className="page-description">{module.description}</p>
        </div>
        {rooms && (
          <div className="unavailable-action">
            <Button
              variant="primary"
              disabled
              aria-describedby="create-unavailable"
            >
              <Icon name="plus" />
              Create Room
            </Button>
            <span id="create-unavailable" className="caption">
              Workspace service required
            </span>
          </div>
        )}
      </div>
      <div className="section-bar">
        <span>{rooms ? "COLLABORATIONS" : "MODULE STATUS"}</span>
        <Badge status="unavailable" />
      </div>
      <Card className="placeholder-card">
        <StatusView
          state="unavailable"
          title={rooms ? undefined : `${module.title} is not connected`}
          description={
            rooms
              ? undefined
              : `This module is reserved for ${module.milestone}. Select an authenticated Room after the workspace service is available.`
          }
        />
        <div className="placeholder-footer">
          <span className="caption">{module.milestone}</span>
          <span className="caption">No live data</span>
        </div>
      </Card>
      <div className="boundary-note">
        <Icon name="info" />
        <p>
          This is the application foundation. No data is uploaded and no private
          computation is started here.
        </p>
      </div>
      {rooms && (
        <ButtonLink href="/preview/rooms">
          Explore synthetic Rooms preview
        </ButtonLink>
      )}
    </>
  );
}

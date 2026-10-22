import { Button, ButtonLink, Card, StatusView } from "@/components/ui";
export const metadata = { title: "Create Room unavailable" };
export default function Page() {
  return (
    <>
      <h1>Create a Room</h1>
      <Card>
        <StatusView
          state="unavailable"
          title="Room creation service unavailable"
          description="Authentication, persistence, invitation and local connector services are not implemented. No Room can be created here."
          action={<Button disabled>Create Room</Button>}
        />
      </Card>
      <ButtonLink href="/preview/rooms/new">
        Explore synthetic Easy Setup
      </ButtonLink>
    </>
  );
}

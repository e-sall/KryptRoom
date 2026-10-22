"use client";
import { Button, StatusView } from "@/components/ui";
export default function ErrorBoundary({ reset }: { reset: () => void }) {
  return (
    <main className="standalone-page">
      <h1>Interface unavailable</h1>
      <StatusView
        state="error"
        title="The interface could not load"
        description="Try loading the interface again. No operation has been requested by this page."
        action={<Button onClick={reset}>Try again</Button>}
      />
    </main>
  );
}

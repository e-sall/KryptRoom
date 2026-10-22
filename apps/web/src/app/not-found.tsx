import { ButtonLink } from "@/components/ui";
export default function NotFound() {
  return (
    <main className="standalone-page">
      <p className="eyebrow">KRYPTROOM · 404</p>
      <h1>Page not found</h1>
      <p>This route is not part of the current application.</p>
      <ButtonLink href="/app/rooms">Back to workspace</ButtonLink>
    </main>
  );
}

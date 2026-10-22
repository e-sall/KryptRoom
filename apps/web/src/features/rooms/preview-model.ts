/** Presentation models only: NOT backend DTOs or authorization decisions. */
export type ExampleStatus = "Active" | "Setup required" | "Ready";
export type ExampleState = Readonly<{
  id: string;
  label: string;
  parent_state_ids: readonly string[];
}>;
export type ExampleRoom = Readonly<{
  demo: true;
  id: string;
  name: string;
  summary: string;
  status: ExampleStatus;
  organizations: readonly string[];
  activity: string;
  states: readonly ExampleState[];
}>;
// Synthetic, fixed presentation fixtures. No participant records, commitments or results.
export const exampleRooms: readonly ExampleRoom[] = [
  {
    demo: true,
    id: "supply-chain",
    name: "Supply Chain Collaboration",
    summary: "Private Join · Analytics",
    status: "Active",
    organizations: ["Example Organization A", "Example Organization B"],
    activity: "2h ago · example",
    states: [
      { id: "S1", label: "Initial", parent_state_ids: [] },
      { id: "S2", label: "Private Join", parent_state_ids: ["S1"] },
      { id: "S3", label: "Analytics", parent_state_ids: ["S1"] },
    ],
  },
  {
    demo: true,
    id: "research",
    name: "Research Partnership",
    summary: "Onboarding in progress",
    status: "Setup required",
    organizations: [
      "Example Organization A",
      "Example Organization B",
      "Example Organization C",
    ],
    activity: "Yesterday · example",
    states: [],
  },
  {
    demo: true,
    id: "insights",
    name: "Joint Insights Room",
    summary: "PSI Cardinality",
    status: "Ready",
    organizations: ["Example Organization A", "Example Organization B"],
    activity: "Oct 18 · example",
    states: [
      { id: "S1", label: "Initial", parent_state_ids: [] },
      { id: "S2", label: "PSI", parent_state_ids: ["S1"] },
    ],
  },
];
export function filterRooms(query: string, status: string) {
  const search = query.trim().toLocaleLowerCase();
  return exampleRooms.filter(
    (room) =>
      (status === "all" || room.status === status) &&
      `${room.name} ${room.summary} ${room.organizations.join(" ")}`
        .toLocaleLowerCase()
        .includes(search),
  );
}
export const setupSteps = [
  "Room Identity",
  "Participants",
  "Protected Data Connections",
  "Security & Policies",
] as const;
export type SetupDraft = {
  name: string;
  description: string;
  organization: string;
  email: string;
  source: string;
  owner: string;
  disclosure: "deny" | "request-aggregate";
};
export const emptyDraft: SetupDraft = {
  name: "",
  description: "",
  organization: "",
  email: "",
  source: "",
  owner: "Example Organization A",
  disclosure: "deny",
};
export function validateStep(step: number, draft: SetupDraft): string | null {
  if (
    step === 0 &&
    (draft.name.trim().length < 3 || draft.name.trim().length > 80)
  )
    return "Enter a Room name between 3 and 80 characters.";
  if (step === 0 && draft.description.length > 280)
    return "Keep the description within 280 characters.";
  if (
    step === 1 &&
    (draft.organization || draft.email) &&
    (!draft.organization.trim() ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(draft.email))
  )
    return "Enter an organization name and a valid example email, or leave both empty to complete later.";
  if (
    step === 2 &&
    draft.source &&
    !/^example-[a-z0-9-]{1,48}$/.test(draft.source)
  )
    return "Use an example-only reference such as example-source-a. Do not enter a path, URL or data.";
  return null;
}
/** Completion of a UI draft never grants permission. No execution callback exists. */
export function previewGate() {
  return {
    allowed: false as const,
    reason:
      "Workspace service, authenticated access and authoritative approvals are unavailable. No operation can run.",
  };
}

import type { IconName } from "@/components/icon";

export type Module = {
  id: string;
  label: string;
  title: string;
  description: string;
  icon: IconName;
  milestone: string;
};
export const modules = [
  {
    id: "rooms",
    label: "Rooms",
    title: "Rooms",
    description: "Your private collaborations, in one place.",
    icon: "rooms",
    milestone: "PR 2 · Rooms & Setup",
  },
  {
    id: "graph",
    label: "Graph",
    title: "State Graph",
    description: "Encrypted RoomState lineage.",
    icon: "graph",
    milestone: "PR 3 · Graph Workspace",
  },
  {
    id: "participants",
    label: "Participants",
    title: "Participants",
    description: "The organizations in a collaboration.",
    icon: "users",
    milestone: "PR 2 · Rooms & Setup",
  },
  {
    id: "data",
    label: "Data & Artifacts",
    title: "Data & Artifacts",
    description: "References to protected, participant-owned data.",
    icon: "data",
    milestone: "PR 2 · Rooms & Setup",
  },
  {
    id: "computations",
    label: "Computations",
    title: "Computations",
    description: "Private computation, within an authorized Room.",
    icon: "compute",
    milestone: "PR 4 · Computations & Results",
  },
  {
    id: "results",
    label: "Results",
    title: "Results",
    description: "Only the results you are authorized to receive.",
    icon: "results",
    milestone: "PR 4 · Computations & Results",
  },
  {
    id: "proofs",
    label: "Proofs & Provenance",
    title: "Proofs & Provenance",
    description: "Evidence, verification and public anchoring.",
    icon: "proof",
    milestone: "PR 5 · Proofs & Activity",
  },
  {
    id: "activity",
    label: "Activity",
    title: "Activity",
    description: "The history of your workspace.",
    icon: "activity",
    milestone: "PR 5 · Proofs & Activity",
  },
  {
    id: "settings",
    label: "Settings",
    title: "Settings",
    description: "Workspace preferences and access.",
    icon: "settings",
    milestone: "PR 2 · Rooms & Setup",
  },
] as const satisfies readonly Module[];
export const moduleHref = (id: string) => `/app/${id}`;
export function findModule(id: string): Module | undefined {
  return modules.find((item) => item.id === id);
}

/** Explicit boundary, not an API adapter or a simulated server response. */
export const workspaceConnection = Object.freeze({
  status: "unavailable" as const,
  reason:
    "The workspace API is not connected. No Room, computation or result has been loaded.",
});

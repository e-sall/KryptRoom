import { graphFixture } from "@/features/graph/fixtures";
import { buildGraph } from "@/features/graph/model";

/** Presentation vocabulary from P05 restored V1, never a runtime event feed. */
export const demoScenes = Object.freeze([
  { name: "Organizations", heading: "Two organizations", description: "Separate environments. Shared computation goal.", note: "Organization A and Organization B are fictional participants, not customers or connected nodes." },
  { name: "Protected Inputs", heading: "Protected inputs", description: "Inputs remain protected. No private records shown.", note: "These lines represent protected inputs. No dataset, identifier, secret share or key is loaded into this demonstration." },
  { name: "Private Computation", heading: "Private computation", description: "A protected operation is illustrated across participating parties.", note: "Scene navigation does not run PSI, MPC or FHE. Protocol choice and permissions belong to the separately validated runtime." },
  { name: "State Creation", heading: "A new state emerges", description: "S4 connects to its parent states. Persistent lineage is preserved.", note: "The preloaded S4 illustrates a reusable protected state. This replay creates, writes and deletes nothing." },
  { name: "Authorized Result", heading: "Authorized result", description: "Only policy-authorized outputs are available for disclosure.", note: "An output type is illustrated, not a grant or a disclosed value. Computation permission is separate from reveal permission." },
  { name: "Proof & Provenance", heading: "Traceable state", description: "Evidence can be inspected. Verification is not assumed.", note: "A commitment identifies content; it is not a general proof of correct private computation. No proof or chain record is supplied here." },
  { name: "Explore the State", heading: "Explore the state", description: "Inspect S4, its parents and its presentation metadata.", note: "These are the existing synthetic Supply Chain states, not historical M1–M7 acceptance artifacts." },
].map((scene) => Object.freeze(scene)));
export const demoRoomId = "supply-chain";
export const demoGraph = buildGraph(graphFixture(demoRoomId));
export const initialDemoScene = 3; // Restored V1 opens on its signature S4 scene.
export function boundedScene(index: number) { return Math.max(0, Math.min(demoScenes.length - 1, index)); }

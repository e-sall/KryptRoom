export const collaborationSteps = Object.freeze([
  { title: "Create Room", concept: "Protected collaboration", text: "Define a shared purpose. Each organization keeps control of its own environment.", detail: "A Room coordinates a collaboration; it is not a central warehouse of raw datasets." },
  { title: "Invite Participants", concept: "Distinct organizations", text: "Agree who participates and what the collaboration may produce.", detail: "Participant identity, approvals and production coordination remain future integration work." },
  { title: "Connect Data", concept: "Cryptographic layers", text: "Reference protected inputs where they belong. Do not expose raw records to other parties.", detail: "The appropriate cryptographic mechanism protects an operation. Encryption at rest alone is not encrypted computation." },
  { title: "Run Computation", concept: "Persistent state", text: "Evolve a protected RoomState. Reveal only explicitly authorized outputs.", detail: "Protected artifacts stay protected and can support subsequent authorized computations. A result does not imply permission to reveal it." },
].map((step) => Object.freeze(step)));

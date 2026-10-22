"use client";
import { createContext, useContext, useState, type ReactNode } from "react";
import { emptyDraft, type SetupDraft } from "./preview-model";

function usePreviewState() {
  const [view, setView] = useState<"list" | "cards">("list");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [selected, setSelected] = useState("supply-chain");
  const [expanded, setExpanded] = useState<string[]>([]);
  const [draft, setDraft] = useState<SetupDraft>({ ...emptyDraft });
  const [step, setStep] = useState(0);
  return {
    view,
    setView,
    query,
    setQuery,
    status,
    setStatus,
    selected,
    setSelected,
    expanded,
    setExpanded,
    draft,
    setDraft,
    step,
    setStep,
  };
}
const Context = createContext<ReturnType<typeof usePreviewState> | null>(null);
export function RoomsPreviewProvider({ children }: { children: ReactNode }) {
  const state = usePreviewState();
  return <Context.Provider value={state}>{children}</Context.Provider>;
}
export function useRoomsPreview() {
  const state = useContext(Context);
  if (!state)
    throw new Error("Rooms preview must remain inside its isolated provider");
  return state;
}

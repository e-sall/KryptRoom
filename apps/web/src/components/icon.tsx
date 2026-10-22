import type { SVGProps } from "react";

export type IconName =
  | "rooms"
  | "graph"
  | "activity"
  | "settings"
  | "users"
  | "data"
  | "compute"
  | "results"
  | "proof"
  | "arrow"
  | "close"
  | "menu"
  | "info"
  | "plus";
const paths: Record<IconName, string> = {
  rooms: "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z",
  graph: "M3 9h5v6H3zM16 2h5v6h-5zM16 16h5v6h-5zM8 12h4V5h4M12 12v7h4",
  activity: "M3 12h4l3-7 4 14 3-7h4",
  settings:
    "M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1zM15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0",
  users:
    "M15 7a3 3 0 1 1-6 0 3 3 0 0 1 6 0M5 21v-3a7 7 0 0 1 14 0v3M19 4a3 3 0 0 1 0 6M21 14l1 5",
  data: "M4 4h16v16H4zM4 10h16M10 10v10",
  compute: "M8 4h8v16H8zM4 8h4M4 16h4M16 8h4M16 16h4M11 8h2M11 12h2M11 16h2",
  results: "M4 3v18h17M8 17v-5M13 17V7M18 17v-8",
  proof: "m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6zM8 12l3 3 5-6",
  arrow: "M4 12h16m-6-6 6 6-6 6",
  close: "m6 6 12 12M18 6 6 18",
  menu: "M4 6h16M4 12h16M4 18h16",
  info: "M12 17v-5M12 7v1M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0",
  plus: "M12 5v14M5 12h14",
};
export function Icon({
  name,
  ...props
}: SVGProps<SVGSVGElement> & { name: IconName }) {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      <path d={paths[name]} />
    </svg>
  );
}

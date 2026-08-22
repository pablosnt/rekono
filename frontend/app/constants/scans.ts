export const stages = [
  { label: "OSINT", value: 1, icon: "i-lucide-rss" },
  { label: "Enumeration", value: 2, icon: "i-lucide-network" },
  // { label: "Vulnerabilities", value: 3, icon: "i-lucide-bug" },
  { label: "Services", value: 4, icon: "i-lucide-server" },
  { label: "Exploitation", value: 5, icon: "i-lucide-flame" },
];

export const timeUnits = ["Weeks", "Days", "Hours", "Minutes"];

export const executionStatuses = [
  { color: "warning", icon: "i-lucide-loader", value: "Running" },
  { color: "success", icon: "i-lucide-circle-check", value: "Completed" },
  { color: "error", icon: "i-lucide-circle-x", value: "Error" },
  { color: "neutral", icon: "i-lucide-ban", value: "Cancelled" },
  { color: "neutral", icon: "i-lucide-skip-forward", value: "Skipped" },
  { color: "info", icon: "i-lucide-clock", value: "Requested" },
];

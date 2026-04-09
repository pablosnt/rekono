export const findingTypes = [
  { value: "OSINT", icon: "i-lucide-rss" },
  { value: "Host", icon: "i-lucide-server" },
  { value: "Port", icon: "i-lucide-ethernet-port" },
  { value: "Path", icon: "i-lucide-slash" },
  { value: "Technology", icon: "i-lucide-layers" },
  { value: "Credential", icon: "i-lucide-key" },
  { value: "Vulnerability", icon: "i-lucide-bug" },
  { value: "Exploit", icon: "i-lucide-flame" },
];

export const triageStatuses = [
  { value: "Untriaged", color: "neutral", icon: "i-lucide-circle-help" },
  { value: "True Positive", color: "success", icon: "i-lucide-circle-alert" },
  {
    value: "False Positive",
    color: "error",
    icon: "i-lucide-circle-x",
  },
  { value: "Won't Fix", color: "warning", icon: "i-lucide-circle-minus" },
];

export const pathTypes = [
  { value: "Endpoint", icon: "i-lucide-globe" },
  { value: "Share", icon: "i-lucide-folder-open" },
];

export const osintDataTypes = [
  { value: "IP", icon: "i-lucide-server" },
  { value: "Domain", icon: "i-lucide-globe" },
  { value: "VHOST", icon: "i-lucide-globe" },
  { value: "URL", icon: "i-lucide-link" },
  { value: "Email", icon: "i-lucide-mail" },
  { value: "ASN", icon: "i-lucide-network" },
  { value: "Username", icon: "i-lucide-user" },
  { value: "Password", icon: "i-lucide-key" },
];

export const hostOS = [
  { value: "Linux", icon: "simple-icons:linux", color: "linux" },
  { value: "Windows", icon: "lineicons:microsoft", color: "info" },
  { value: "MacOS", icon: "lineicons:apple-brand", color: "neutral" },
  { value: "iOS", icon: "lineicons:apple-brand", color: "neutral" },
  { value: "Android", icon: "lineicons:android-original", color: "success" },
  { value: "Solaris", icon: "simple-icons:oracle", color: "error" },
  { value: "FreeBSD", icon: "simple-icons:freebsd", color: "error" },
  { value: "Other", icon: "i-lucide-server", color: "neutral" },
];

export const portStatuses = [
  { value: "Open", color: "success", icon: "i-lucide-square-check" },
  { value: "Open - Filtered", color: "warning", icon: "i-lucide-brick-wall" },
  { value: "Filtered", color: "warning", icon: "i-lucide-brick-wall-shield" },
  { value: "Closed", color: "error", icon: "i-lucide-square-x" },
];

export const portProtocols = ["TCP", "UDP"];

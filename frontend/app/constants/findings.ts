export const findingTypes = [
  {
    value: "OSINT",
    plural: "OSINT",
    icon: "i-lucide-rss",
    color: "primary",
    iconClass: "text-primary",
    iconBgClass: "bg-primary/10",
    accentClass: "bg-primary",
    isTriageable: true,
  },
  {
    value: "Host",
    plural: "Hosts",
    icon: "i-lucide-server",
    color: "slate",
    iconClass: "text-slate-500 dark:text-slate-400",
    iconBgClass: "bg-slate-500/10",
    accentClass: "bg-slate-500",
    isTriageable: false,
  },
  {
    value: "Port",
    plural: "Ports",
    icon: "i-lucide-ethernet-port",
    color: "cyan",
    iconClass: "text-cyan-500",
    iconBgClass: "bg-cyan-500/10",
    accentClass: "bg-cyan-500",
    isTriageable: false,
  },
  {
    value: "Path",
    plural: "Paths",
    icon: "i-lucide-slash",
    color: "teal",
    iconClass: "text-teal-500",
    iconBgClass: "bg-teal-500/10",
    accentClass: "bg-teal-500",
    isTriageable: false,
  },
  {
    value: "Technology",
    plural: "Technologies",
    icon: "i-lucide-layers",
    color: "amber",
    iconClass: "text-amber-500",
    iconBgClass: "bg-amber-500/10",
    accentClass: "bg-amber-500",
    isTriageable: false,
  },
  {
    value: "Credential",
    plural: "Credentials",
    icon: "i-lucide-key",
    color: "orange",
    iconClass: "text-orange-500",
    iconBgClass: "bg-orange-500/10",
    accentClass: "bg-orange-500",
    isTriageable: true,
  },
  {
    value: "Vulnerability",
    plural: "Vulnerabilities",
    icon: "i-lucide-bug",
    color: "error",
    iconClass: "text-error",
    iconBgClass: "bg-error/10",
    accentClass: "bg-error",
    isTriageable: true,
  },
  {
    value: "Exploit",
    plural: "Exploits",
    icon: "i-lucide-flame",
    color: "rose",
    iconClass: "text-rose-600",
    iconBgClass: "bg-rose-600/10",
    accentClass: "bg-rose-600",
    isTriageable: true,
  },
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
  { value: "Linux", icon: "simple-icons:linux", color: "amber" },
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

export const severities = [
  { value: "Info", color: "neutral", icon: "i-lucide-chevrons-down" },
  { value: "Low", color: "info", icon: "i-lucide-chevron-down" },
  { value: "Medium", color: "warning", icon: "i-lucide-chevron-minus" },
  { value: "High", color: "orange", icon: "i-lucide-chevron-up" },
  { value: "Critical", color: "error", icon: "i-lucide-chevrons-up" },
];

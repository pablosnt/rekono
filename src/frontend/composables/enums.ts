export function useEnums() {
  const stages = {
    OSINT: {
      id: 1,
      color: "green",
      icon: "mdi-search-web",
    },
    Enumeration: {
      id: 2,
      color: "purple",
      icon: "mdi-server-network",
    },
    // There are no configurations in this stage yet
    // Vulnerabilities: {
    //     id: 3,
    //     color: 'orange',
    //     icon: 'mdi-bug'
    // },
    Services: {
      id: 4,
      color: "blue",
      icon: "mdi-layers-triple",
    },
    Exploitation: {
      id: 5,
      color: "red",
      icon: "mdi-bomb",
    },
  };
  const intensities = {
    Sneaky: {
      id: 1,
      color: "green",
    },
    Low: {
      id: 2,
      color: "blue",
    },
    Normal: {
      id: 3,
      color: "gray",
    },
    Hard: {
      id: 4,
      color: "orange",
    },
    Insane: {
      id: 5,
      color: "red",
    },
  };
  const wordlists = ["Subdomain", "Endpoint"];
  const timeUnits = ["Weeks", "Days", "Hours", "Minutes"];
  const roles = {
    Admin: {
      icon: "mdi-account-tie",
      color: "blue",
    },
    Auditor: {
      icon: "mdi-account-cowboy-hat",
      color: "red",
    },
    Reader: {
      icon: "mdi-account-eye",
      color: "green",
    },
  };
  const notificationScopes = [
    "Disabled",
    "Only my executions",
    "All executions",
  ];
  const notificationPlatforms = ["e-Mail", "Telegram"];
  const targets = {
    "Private IP": { icon: "mdi-ip" },
    "Public IP": { icon: "mdi-ip" },
    Network: { icon: "mdi-network" },
    "IP range": { icon: "mdi-ip-network" },
    Domain: { icon: "mdi-dns" },
  };
  const findings = {
    OSINT: { icon: "mdi-search-web" },
    Host: { icon: "mdi-server" },
    Port: { icon: "mdi-plus-network" },
    Path: { icon: "mdi-routes" },
    Credential: { icon: "mdi-key-chain" },
    Technology: { icon: "mdi-layers-triple" },
    Vulnerability: { icon: "mdi-bug" },
    Exploit: { icon: "mdi-bomb" },
  };
  const reportFormats = {
    json: { icon: "mdi-code-json" },
    xml: { icon: "mdi-xml" },
    pdf: { icon: "mdi-file-document" },
  };
  const reportStatuses = {
    Ready: { color: "green" },
    Pending: { color: "orange" },
    Error: { color: "red" },
  };
  const alertItems = {
    OSINT: { filter: null, monitor: null, icon: findings.OSINT.icon },
    Host: { filter: "address", monitor: null, icon: findings.Host.icon },
    "Open Port": { filter: null, monitor: null, icon: findings.Port.icon },
    Service: { filter: "name", monitor: null, icon: findings.Port.icon },
    Technology: {
      filter: "name",
      monitor: null,
      icon: findings.Technology.icon,
    },
    Credential: { filter: null, monitor: null, icon: findings.Credential.icon },
    Vulnerability: {
      filter: null,
      monitor: null,
      icon: findings.Vulnerability.icon,
    },
    CVE: {
      filter: "cve",
      monitor: "trending",
      icon: findings.Vulnerability.icon,
    },
  };
  const alertModes = {
    New: { icon: "mdi-new-box" },
    Filter: { icon: "mdi-filter" },
    Monitor: { icon: "mdi-radar" },
  };
  const statuses = {
    Requested: { color: "grey", icon: "mdi-pause-circle" },
    Skipped: { color: "grey", icon: "mdi-skip-next-circle" },
    Running: { color: "yellow", icon: "mdi-play-circle" },
    Cancelled: { color: "red", icon: "mdi-close-circle" },
    Error: { color: "red", icon: "mdi-alert-circle" },
    Completed: { color: "green", icon: "mdi-check-circle" },
  };

  return {
    stages,
    intensities,
    wordlists,
    timeUnits,
    roles,
    notificationScopes,
    notificationPlatforms,
    targets,
    findings,
    reportFormats,
    reportStatuses,
    alertItems,
    alertModes,
    statuses,
  };
}

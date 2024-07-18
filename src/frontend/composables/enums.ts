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
    osint: {
      icon: "mdi-search-web",
    },
    host: {
      icon: "mdi-server",
    },
    port: {
      icon: "mdi-plus-network",
    },
    path: {
      icon: "mdi-routes",
    },
    credential: {
      icon: "mdi-key-chain",
    },
    technology: {
      icon: "mdi-layers-triple",
    },
    vulnerability: {
      icon: "mdi-bug",
    },
    exploit: {
      icon: "mdi-bomb",
    },
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
  };
}

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

  return { stages, intensities, wordlists, timeUnits };
}

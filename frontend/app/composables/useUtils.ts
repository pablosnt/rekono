export default function () {
  function firstUpper(value: string) {
    return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
  }

  const stageOptions = [
    { label: "OSINT", value: 1, icon: "i-lucide-globe" },
    { label: "Enumeration", value: 2, icon: "i-lucide-network" },
    { label: "Vulnerabilities", value: 3, icon: "i-lucide-bug" },
    { label: "Services", value: 4, icon: "i-lucide-server" },
    { label: "Exploitation", value: 5, icon: "i-lucide-flame" },
  ];

  return { firstUpper, stageOptions };
}

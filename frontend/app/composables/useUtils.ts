export default function () {
  function firstUpper(value: string) {
    return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
  }

  const stageOptions = [
    { label: "OSINT", value: 1 },
    { label: "Enumeration", value: 2 },
    { label: "Vulnerabilities", value: 3 },
    { label: "Services", value: 4 },
    { label: "Exploitation", value: 5 },
  ];

  return { firstUpper, stageOptions };
}

export function useVulnerabilities() {
  function cweReference(cwe) {
    return `https://cwe.mitre.org/data/definitions/${cwe.split("-")[1]}.html`;
  }

  return { cweReference };
}

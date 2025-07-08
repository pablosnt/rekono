export function useVulnerabilities() {
  function cweReference(cwe: string): string {
    return `https://cwe.mitre.org/data/definitions/${cwe.split("-")[1]}.html`;
  }

  return { cweReference };
}

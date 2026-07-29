export function formatCount(n: number): string {
  if (n >= 1_000_000) return `${parseFloat((n / 1_000_000).toFixed(1))}M`;
  if (n >= 1_000) return `${parseFloat((n / 1_000).toFixed(1))}K`;
  return String(n);
}

export function firstUpper(value: string) {
  return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
}

export function truncateText(
  text: string,
  maxLength: number = 20,
  truncateWithSpaces: boolean = false,
): string {
  return text.length <= maxLength || (!truncateWithSpaces && text.includes(" "))
    ? text
    : `${text.slice(0, maxLength)}...`;
}

export function duration(
  startDateString: string,
  endDateString: string,
): string {
  const ms =
    new Date(endDateString).getTime() - new Date(startDateString).getTime();
  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  parts.push(`${seconds}s`);
  return parts.join(" ");
}

const ACRONYMS = new Set([
  "API",
  "HTTP",
  "URL",
  "JSON",
  "XML",
  "HTML",
  "CSS",
  "JS",
  "TS",
  "OSINT",
  "CVE",
  "IP",
  "ID",
  "EDB",
]);

export function smartLowerCase(text: string): string {
  return text.replaceAll(/\b\w+\b/gu, (match) =>
    ACRONYMS.has(match.toUpperCase())
      ? match.toUpperCase()
      : match.toLowerCase(),
  );
}

export function copyLink() {
  const url = useRequestURL();
  navigator.clipboard?.writeText(`${url.origin}${url.pathname}`).then(() => {
    useNuxtApp()
      .vueApp.runWithContext(() => useToast())
      .add({ title: "Link copied to clipboard", color: "success" });
  });
}

export function copyText(text: string, message?: string) {
  navigator.clipboard?.writeText(text).then(() => {
    useNuxtApp()
      .vueApp.runWithContext(() => useToast())
      .add({
        title: message || `${text} copied to clipboard`,
        color: "success",
      });
  });
}

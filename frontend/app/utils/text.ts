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

export function smartLowerCase(text: string): string {
  return text.replace(
    /\b(?!API|HTTP|URL|JSON|XML|HTML|CSS|JS|TS|OSINT|CVE|IP)\w+/g,
    (match) => match.toLowerCase(),
  );
}

export function copyLink() {
  const url = useRequestURL();
  const toast = useToast();
  navigator.clipboard.writeText(`${url.origin}${url.pathname}`);
  toast.add({ title: "Link copied to clipboard", color: "success" });
}

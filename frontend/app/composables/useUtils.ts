export default function () {
  function firstUpper(value: string) {
    return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
  }

  function truncateText(
    text: string,
    maxLength: number = 20,
    truncateWithSpaces: boolean = false,
  ): string {
    return text.length <= maxLength ||
      (!truncateWithSpaces && text.includes(" "))
      ? text
      : `${text.slice(0, maxLength)}...`;
  }

  function formatRelativeDatetime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffTime / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    const diffWeeks = Math.floor(diffDays / 7);
    const diffMonths = Math.floor(diffDays / 30);
    const diffYears = Math.floor(diffDays / 365);
    const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
    if (Math.abs(diffYears) >= 1) {
      return rtf.format(-diffYears, "year");
    } else if (Math.abs(diffMonths) >= 1) {
      return rtf.format(-diffMonths, "month");
    } else if (Math.abs(diffWeeks) >= 1) {
      return rtf.format(-diffWeeks, "week");
    } else if (Math.abs(diffDays) >= 1) {
      return rtf.format(-diffDays, "day");
    } else if (Math.abs(diffHours) >= 1) {
      return rtf.format(-diffHours, "hour");
    } else if (Math.abs(diffMinutes) >= 1) {
      return rtf.format(-diffMinutes, "minute");
    } else {
      return rtf.format(-diffSeconds, "second");
    }
  }

  function smartLowerCase(text: string): string {
    return text.replace(
      /\b(?!API|HTTP|URL|JSON|XML|HTML|CSS|JS|TS|OSINT|CVE|IP)\w+/g,
      (match) => match.toLowerCase(),
    );
  }

  return {
    firstUpper,
    truncateText,
    formatRelativeDatetime,
    smartLowerCase,
  };
}

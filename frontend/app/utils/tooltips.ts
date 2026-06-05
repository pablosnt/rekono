function keyPair(key: string, value: string): string {
  return `<div style="display:flex;justify-content:space-between;gap:20px;padding:2px 0"><span>${key}</span><strong>${value}</strong></div>`;
}

export function metricsPercentage(count: number, total: number): string {
  return total > 0 ? ` (${((count / total) * 100).toPrecision(3)}%)` : "";
}

export function metricsTooltip(
  keyPairs: Record<string, string | number>,
  title?: string,
): string {
  const titleHtml = title
    ? `<div style="font-weight:700;font-size:14px;padding-bottom:6px;margin-bottom:2px;margin-top:4px;border-bottom:1px solid currentColor;opacity:0.9">${title}</div>`
    : "";
  return `<div style="padding:10px 14px;min-width:180px;font-size:13px;line-height:1.8">${titleHtml}${Object.keys(
    keyPairs,
  )
    .map((key) => keyPair(key, keyPairs[key]))
    .join("")}</div>`;
}

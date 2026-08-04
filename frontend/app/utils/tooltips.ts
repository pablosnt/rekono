function keyPair(key: string, value: string | number): HTMLElement {
  const row = document.createElement("div");
  row.style.cssText =
    "display:flex;justify-content:space-between;gap:20px;padding:2px 0";
  const keyEl = document.createElement("span");
  keyEl.textContent = String(key);
  const valueEl = document.createElement("strong");
  valueEl.textContent = String(value);
  row.append(keyEl, valueEl);
  return row;
}

export function metricsPercentage(count: number, total: number): string {
  return total > 0 ? ` (${((count / total) * 100).toPrecision(3)}%)` : "";
}

export function metricsTooltip(
  keyPairs: Record<string, string | number>,
  title?: string,
): HTMLElement {
  const container = document.createElement("div");
  container.style.cssText =
    "padding:10px 14px;min-width:180px;font-size:13px;line-height:1.8";
  if (title) {
    const titleEl = document.createElement("div");
    titleEl.style.cssText =
      "font-weight:700;font-size:14px;padding-bottom:6px;margin-bottom:2px;margin-top:4px;border-bottom:1px solid currentColor;opacity:0.9";
    titleEl.textContent = title;
    container.append(titleEl);
  }
  for (const key of Object.keys(keyPairs)) {
    container.append(keyPair(key, keyPairs[key]));
  }
  return container;
}

import type { Finding } from "~/types/models";

export function getExposureWindow(finding: Finding) {
  return finding.executions
    .filter((e) => Boolean(e.end))
    .map((e) => new Date(e.end).toDateString())
    .filter(
      (value, index, self) => index === self.findIndex((d) => d === value),
    )
    .map((d) => {
      return {
        date: new Date(d),
        tools: finding.executions
          .filter((e) => Boolean(e.end) && new Date(e.end).toDateString() === d)
          .map((e) => e.configuration?.tool.name)
          .filter(
            (value, index, self) =>
              index === self.findIndex((d) => d === value),
          ),
      };
    })
    .sort((a, b) => a.date.getTime() - b.date.getTime());
}

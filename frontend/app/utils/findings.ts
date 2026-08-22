import type { Finding, OSINT } from "~/types/models";
import type { DropdownAction } from "~/types/crud";

export function getFindingDropdownActions(
  finding: Finding,
  fixVerb: string,
  unfixVerb: string,
  isTriageable: boolean,
  onFix: CallableFunction,
  onRestore: CallableFunction,
  onTriage: CallableFunction,
): DropdownAction[] {
  const actions = [];
  if (!finding.is_fixed) {
    actions.push({
      label: fixVerb,
      icon: fixVerb === "Fix" ? "i-lucide-check-circle" : "i-lucide-eye-off",
      color: fixVerb === "Fix" ? "success" : undefined,
      onSelect: () => onFix(finding),
    });
  } else if (!finding.auto_fixed) {
    actions.push({
      label: unfixVerb,
      icon: fixVerb === "Fix" ? "i-lucide-rotate-ccw" : "i-lucide-eye",
      color: fixVerb === "Fix" ? undefined : "success",
      onSelect: () => onRestore(finding),
    });
  }
  if (isTriageable && !finding.is_fixed) {
    actions.push({
      label: "Triage",
      icon: "i-lucide-shield-check",
      onSelect: () => onTriage(finding),
    });
  }
  return actions;
}

export function getOSINTDropdownActions(
  finding: OSINT,
  api: typeof useApi,
): DropdownAction {
  return {
    label: "Create target",
    icon: "i-lucide-locate-fixed",
    color: "error",
    onSelect: () => {
      api
        .create(`${finding.id}/target/`, {}, {}, "Target")
        .then((response) =>
          navigateTo(`/projects/${response.project}/targets/${response.id}`),
        );
    },
  };
}

export function getExposureWindow(finding: Finding) {
  return finding.executions
    .filter((e) => Boolean(e.end))
    .map((e) => new Date(e.end).toDateString())
    .filter(
      (value, index, self) => index === self.findIndex((v) => v === value),
    )
    .map((d) => {
      return {
        date: new Date(d),
        tools: finding.executions
          .filter((e) => Boolean(e.end) && new Date(e.end).toDateString() === d)
          .map((e) => e.configuration?.tool.name)
          .filter(
            (value, index, self) =>
              index === self.findIndex((v) => v === value),
          ),
      };
    })
    .toSorted((a, b) => a.date.getTime() - b.date.getTime());
}

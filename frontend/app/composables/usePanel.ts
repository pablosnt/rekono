export function usePanel() {
  const panelRefresh = useState("panel-refresh", () => 0);
  const projectHasActiveFindings = useState(
    "project-active-findings",
    () => false,
  );

  function refreshPanelCounts() {
    panelRefresh.value++;
  }

  return { refreshPanelCounts, panelRefresh, projectHasActiveFindings };
}

export function usePanel() {
  const panelRefresh = useState("panel-refresh", () => 0);

  function refreshPanelCounts() {
    panelRefresh.value++;
  }

  return { refreshPanelCounts, panelRefresh };
}

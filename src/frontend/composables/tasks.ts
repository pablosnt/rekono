export function useTasks() {
  const dates = useDates();

  function getTitle(task) {
    const executable =
      task.configuration !== null
        ? `${task.configuration.tool.name} - ${task.configuration.name}`
        : task.process.name;
    task.title =
      task.start !== null
        ? `${executable} - ${new Date(new Date(task.start).toISOString().split("T")[0]).toISOString().split("T")[0]}`
        : executable;
    return task.title;
  }

  function getStatus(task) {
    const statuses = {};
    for (let i = 0; i < task.executions.length; i++) {
      const status = task.executions[i].status;
      if (!statuses[status]) {
        statuses[status] = 1;
      } else {
        statuses[status] = statuses[status] + 1;
      }
    }
    task.status = statuses.Running
      ? "Running"
      : statuses.Cancelled
        ? "Cancelled"
        : statuses.Error
          ? "Error"
          : (statuses.Completed &&
                statuses.Completed === task.executions.length) ||
              (statuses.Completed &&
                statuses.Skipped &&
                statuses.Completed + statuses.Skipped ===
                  task.executions.length)
            ? "Completed"
            : statuses.Skipped
              ? "Skipped"
              : "Requested";
    const finishedExecutions =
      (statuses.Error || 0) +
      (statuses.Completed || 0) +
      (statuses.Skipped || 0) +
      (statuses.Cancelled || 0);
    task.progress =
      task.executions.length > 0
        ? Math.ceil((finishedExecutions / task.executions.length) * 100)
        : 0;
    return task.status;
  }

  return { getTitle, getStatus };
}

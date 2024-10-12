export function useTasks() {
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

  function getDuration(task) {
    const start = new Date(task.start);
    const end = new Date(task.end);
    const seconds = Math.floor((end.getTime() - start.getTime()) / 1000);
    const fields = [
      { value: Math.floor(seconds / (3600 * 24)), name: "d" },
      { value: Math.floor((seconds % (3600 * 24)) / 3600), name: "h" },
      { value: Math.floor((seconds % 3600) / 60), name: "m" },
      { value: Math.floor(seconds % 60), name: "s" },
    ];
    task.duration = "";
    for (let i = 0; i < fields.length; i++) {
      if (fields[i].value > 0) {
        task.duration = task.duration + `${fields[i].value} ${fields[i].name} `;
      }
    }
    task.duration = task.duration.trim();
    return task.duration;
  }

  return { getTitle, getStatus, getDuration };
}

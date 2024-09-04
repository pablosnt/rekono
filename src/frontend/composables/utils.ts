export function useUtils() {
  function getTaskTitle(task) {
    const executable = task.process
      ? task.process.name
      : `${task.configuration.tool.name} - ${task.configuration.name}`;
    return task.start !== null
      ? `${executable} - ${new Date(new Date(task.start).toISOString().split("T")[0]).toISOString().split("T")[0]}`
      : executable;
  }

  return { getTaskTitle };
}

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

  return { getTitle };
}

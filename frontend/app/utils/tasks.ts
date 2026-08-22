import type { Task } from "~/types/models";

export function getTaskName(task: Task, includeTarget?: boolean) {
  const scanner = task.process
    ? task.process.name
    : `${task.configuration?.tool.name} (${task.configuration?.name})`;
  const target_port = task.target_port
    ? `:${task.target_port.port}${task.target_port.path ? (task.target_port.path[0] === "/" ? task.target_port.path : `/${task.target_port.path}`) : ""}`
    : "";
  const target = `${task.target.target}${target_port}`;
  const text = includeTarget ? `${scanner} - ${target}` : scanner;
  return task.start
    ? `${text} - ${new Date(task.start).toLocaleString()}`
    : text;
}

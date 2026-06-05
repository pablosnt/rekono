import type { Project } from "~/types/models";

export function useCurrentProject() {
  const currentProject = useState<Project | null>(
    "current-project",
    () => null,
  );

  function setCurrentProject(project: Project | null) {
    currentProject.value = project;
  }

  return { currentProject, setCurrentProject };
}

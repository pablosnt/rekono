import type { Project } from "~/types/models";
import { useIntegrationsStore } from "~/store/integrations";

export function useCurrentProject() {
  const integrations = useIntegrationsStore();

  const currentProject = useState<Project | null>(
    "current-project",
    () => null,
  );
  const showDefectDojo = computed(() =>
    Boolean(
      currentProject.value?.defectdojo_sync &&
      integrations.defectdojo?.settings?.is_available,
    ),
  );

  function setCurrentProject(project: Project | null) {
    currentProject.value = project;
  }

  return { currentProject, showDefectDojo, setCurrentProject };
}

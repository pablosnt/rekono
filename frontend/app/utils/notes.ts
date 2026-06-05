import { hostOS } from "~/constants";
import type { Note } from "~/types/models";

export function getNoteRelatedEntity(
  note: Note,
): Record<string, string | undefined> | null {
  const route = useRoute();
  const baseTo = `/projects/${route.params.project_id}/`;
  for (const definition of [
    {
      entity: note.exploit,
      to: `${baseTo}exploits/${note.exploit?.id}`,
      label: note.exploit?.title,
      icon: "i-lucide-flame",
    },
    {
      entity: note.vulnerability,
      to: `${baseTo}vulnerabilities/${note.vulnerability?.id}`,
      label: note.vulnerability?.name,
      icon: "i-lucide-bug",
    },
    {
      entity: note.credential,
      to: `${baseTo}credentials/${note.credential?.id}`,
      icon: "i-lucide-key",
      label:
        note.credential?.username ||
        note.credential?.email ||
        `#${note.credential?.id}`,
    },
    {
      entity: note.technology,
      to: `${baseTo}technologies/${note.technology?.id}`,
      label: note.technology?.name,
      icon: "i-lucide-code",
    },
    {
      entity: note.path,
      to: `${baseTo}paths/${note.path?.id}`,
      label: note.path?.path,
      icon: "i-lucide-slash",
    },
    {
      entity: note.port,
      to: `${baseTo}ports/${note.port?.id}`,
      icon: getPortIcon(note.port?.port, note.port?.service),
      label: `${note.port?.host?.ip}:${note.port?.port}`,
    },
    {
      entity: note.host,
      to: `${baseTo}hosts/${note.host?.id}`,
      icon:
        hostOS.find((o) => o.value === note.host?.os_type)?.icon ||
        "i-lucide-server",
      label: note.host?.ip,
    },
    {
      entity: note.osint,
      to: `${baseTo}osint/${note.osint?.id}`,
      icon: "i-lucide-rss",
      label: note.osint?.data,
    },
    {
      entity: note.task,
      to: `${baseTo}scans/${note.task?.id}`,
      icon: "i-lucide-play",
      label: note.task?.process
        ? note.task.process.name
        : note.task?.configuration?.tool.name,
    },
    {
      entity: note.target,
      to: `${baseTo}targets/${note.target?.id}`,
      icon: note.target
        ? targetTypes.find((t) => t.value === note.target?.type)?.icon
        : "i-lucide-locate-fixed",
      label: note.target?.target,
    },
  ]) {
    if (definition.entity) {
      return {
        to: definition.to,
        icon: definition.icon,
        label: definition.label || "",
      };
    }
  }
  return null;
}

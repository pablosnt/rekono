import * as z from "zod";
import type { Project } from "~/types/models";

export function useProjectsConfig() {
  const validation = useValidation();

  const formFields = [
    {
      key: "name",
      label: "Name",
      type: "text",
      required: true,
      placeholder: "Enter project name",
    },
    {
      key: "description",
      label: "Description",
      type: "textarea",
      required: true,
      placeholder: "Enter project description",
    },
    {
      key: "tags",
      label: "Tags",
      type: "tags",
      required: false,
      placeholder: "Add project tags",
      icon: "i-lucide-tag",
    },
  ];

  const formSchema = z.object({
    name: validation.name(),
    description: validation.text("description"),
    tags: z.array(validation.name("tag", true, 100)).optional(),
  });

  const deleteMessage = (project: Project) =>
    buildDeleteMessage(
      "project",
      project.name,
      "Permanent deletion",
      "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
    );

  return { formFields, formSchema, deleteMessage };
}

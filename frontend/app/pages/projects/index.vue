<template>
  <CrudPage :config="config" @deleted="refreshPanelCounts()" />
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import { useUserStore } from "~/store/user";
import * as z from "zod";
import type { Project } from "~/types/models";

const userStore = useUserStore();
const validation = useValidation();
const options = useOptions();
const table = useTable();
const { refreshPanelCounts } = usePanel();
const userOptions = ref<FilterOption[]>([]);

onMounted(() => {
  options.users(userOptions, { role: "Admin", is_active: true });
});

// todo: add link to DefectDojo if sync is enabled
const config: CrudConfig<Project> = reactive({
  endpoint: "/api/projects/",
  entityName: "Project",
  entityNamePlural: "Projects",
  icon: "i-lucide-folder",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      accessorKey: "name",
      header: "Name",
      icon: "i-lucide-case-sensitive",
      cell: ({ row }) => table.valueCell(row.getValue("name")),
    },
    {
      accessorKey: "description",
      header: "Description",
      icon: "i-lucide-align-left",
      cell: ({ row }) => table.valueCell(row.getValue("description")),
    },
    {
      accessorKey: "tags",
      header: "Tags",
      icon: "i-lucide-tag",
      cell: ({ row }) =>
        h(resolveComponent("CrudTags"), { tags: row.getValue("tags") }),
    },
    {
      accessorKey: "targets",
      header: "Targets",
      icon: "i-lucide-locate-fixed",
      cell: ({ row }) => table.valueCell(row.getValue("targets").length),
    },
    {
      accessorKey: "owner",
      header: "Owner",
      icon: "i-lucide-user",
      cell: ({ row }) => table.usernameCell(row.getValue("owner")),
    },
  ] as CrudTableColumn<Project>[],
  tableColumnsVisibility: {
    id: false,
    description: false,
    owner: false,
  },
  itemLink: (project: Project) => `/projects/${project.id}`,
  searchable: true,
  searchPlaceholder: "Search projects...",
  filters: [
    {
      key: "tag",
      label: "Tag",
      icon: "i-lucide-tag",
      type: "text",
      placeholder: "Filter by tag...",
    },
    {
      key: "owner",
      label: "Owner",
      icon: "i-lucide-user",
      type: "select" as const,
      options: userOptions,
    },
  ],
  ordering: ["id", "name"],
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  formFields: [
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
  ],
  formSchema: z.object({
    name: validation.name(),
    description: validation.text("description"),
    tags: z.array(validation.name("tag", true, 100)).optional(),
  }),
  createForm: resolveComponent("ProjectsForm"),
  updateOnCreateModalOpen: true,
  onCreation: (data: Record<string, unknown>) =>
    navigateTo(
      data.targets.length == 0
        ? `/projects/${data.id}`
        : `/projects/${data.id}/targets`,
    ),
  deleteMessage: (project: Project) =>
    buildDeleteMessage(
      "project",
      project.name,
      "Permanent deletion",
      "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
    ),
  canRead: true,
  canCreate: userStore.is_admin,
  canEdit: (_project: Project) => userStore.is_admin,
  canDelete: (_project: Project) => userStore.is_admin,
});
</script>

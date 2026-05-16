<template>
  <CrudPage :config="config" @deleted="refreshPanelCounts()" />
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import { useUserStore } from "~/store/user";
import type { Project } from "~/types/models";
import { useIntegrationsStore } from "~/store/integrations";

const userStore = useUserStore();
const integrations = useIntegrationsStore();
const { formFields, formSchema, deleteMessage } = useProjectsConfig();
const options = useOptions();
const table = useTable();
const { refreshPanelCounts } = usePanel();
const userOptions = ref<FilterOption[]>([]);
const targetOptions = ref<FilterOption[]>([]);

onMounted(() => {
  options.users(userOptions, { role: "Admin", is_active: true });
  options.targets(targetOptions);
  integrations.fetchDefectDojo();
});

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
        h(resolveComponent("Tags"), { tags: row.getValue("tags") }),
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
    ...(integrations.defectdojo?.settings?.is_available
      ? [
          {
            accessorKey: "defectdojo",
            header: "DefectDojo",
            avatar: { src: integrations.defectdojo?.integration.icon },
            cell: ({ row }) =>
              row.original.defectdojo_sync?.product_id
                ? h(resolveComponent("DefectdojoLink"), {
                    entity: "product",
                    id: row.original.defectdojo_sync?.product_id,
                    size: "sm",
                  })
                : table.noDataCell,
          },
        ]
      : []),
  ] as CrudTableColumn<Project>[],
  tableColumnsVisibility: {
    id: false,
    description: false,
    owner: false,
    defectdojo: integrations.defectdojo.integration?.enabled,
  },
  itemLink: (project: Project) => `/projects/${project.id}`,
  searchable: true,
  searchPlaceholder: "Search projects...",
  filters: [
    {
      key: "target",
      label: "Target",
      icon: "i-lucide-locate-fixed",
      type: "select" as const,
      options: targetOptions,
    },
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
  formFields,
  formSchema,
  createForm: resolveComponent("ProjectsForm"),
  updateOnCreateModalOpen: true,
  onCreation: (data: Record<string, unknown>) =>
    navigateTo(
      data.targets.length == 0
        ? `/projects/${data.id}`
        : `/projects/${data.id}/targets`,
    ),
  deleteMessage: deleteMessage,
  canRead: true,
  canCreate: userStore.is_admin,
  canEdit: (_project: Project) => userStore.is_admin,
  canDelete: (_project: Project) => userStore.is_admin,
});
</script>

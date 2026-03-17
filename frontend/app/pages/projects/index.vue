<template>
  <CrudPage :config="config" />
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import { useUserStore } from "~/store/user";
import * as z from "zod";
import type { Project } from "~/types/models";

const userStore = useUserStore();
const validation = useValidation();
const backend = useBackend();
const userOptions = ref<FilterOption[]>([]);

onMounted(() => {
  backend.getUserOptions(userOptions, { role: "Admin", is_active: true });
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
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      accessorKey: "name",
      header: "Name",
      icon: "i-lucide-case-sensitive",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("name")),
    },
    {
      accessorKey: "description",
      header: "Description",
      icon: "i-lucide-align-left",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("description")),
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
      cell: ({ row }) =>
        h(
          "span",
          { class: "font-medium" },
          (row.getValue("targets") as Project["targets"]).length,
        ),
    },
    {
      accessorKey: "owner",
      header: "Owner",
      icon: "i-lucide-user",
      cell: ({ row }) => {
        const owner = row.getValue("owner") as Project["owner"];
        return h(
          "span",
          { class: "font-medium" },
          owner?.username ? `@${owner.username}` : "—",
        );
      },
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
  deleteMessage: (project: Project) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this project?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: project.name,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "error",
        icon: "i-lucide-triangle-alert",
        title: "Permanent deletion",
        description:
          "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
        class: "mt-4",
      },
    },
  ],
  canRead: true,
  canCreate: userStore.is_admin,
  canEdit: (_project: Project) => userStore.is_admin,
  canDelete: (_project: Project) => userStore.is_admin,
});
</script>

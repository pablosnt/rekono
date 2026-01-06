<template>
  <CrudPage :config="config" />
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import { useUserStore } from "~/store/user";
import * as z from "zod";
import type { Project } from "~/types/projects";

const userStore = useUserStore();
const validation = useValidation();
const utils = useUtils();
const userOptions = ref<FilterOption[]>([]);

onMounted(() => {
  if (userStore.is_admin) {
    utils.getUserOptions(userOptions, { role: "Admin" });
  }
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
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      accessorKey: "name",
      header: "Name",
      icon: "i-lucide-case-sensitive",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("name")),
      enableResizing: true,
    },
    {
      accessorKey: "description",
      header: "Description",
      icon: "i-lucide-align-left",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("description")),
      enableResizing: true,
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
      enableResizing: true,
    },
    {
      accessorKey: "owner",
      header: "Owner",
      icon: "i-lucide-user",
      cell: ({ row }) => {
        const owner = row.getValue("owner") as Project["owner"];
        return owner?.username ? `@${owner.username}` : "";
      },
      enableResizing: true,
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
    ...(userStore.is_admin
      ? [
          {
            key: "owner",
            label: "Owner",
            icon: "i-lucide-user",
            type: "select" as const,
            options: userOptions,
          },
        ]
      : [
          {
            key: "owner_username",
            label: "Owner",
            icon: "i-lucide-user",
            type: "text" as const,
            placeholder: "Filter by owner username...",
          },
        ]),
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

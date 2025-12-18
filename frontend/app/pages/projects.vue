<template>
  <MainPanel>
    <CrudPage :config="config" />
  </MainPanel>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn } from "~/types/crud";
import { useUserStore } from "~/store/user";
import * as z from "zod";

interface Project {
  id: number;
  name: string;
  description: string;
  owner: {
    id: number;
    username: string;
  } | null;
  targets: Array<number>;
  members: Array<number>;
  tags: Array<string>;
}

const userStore = useUserStore();
const validation = useValidation();
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
      cell: ({ row }) => {
        const tags = row.getValue("tags") as Project["tags"];
        if (!tags?.length) return "";
        return h(
          "div",
          { class: "flex flex-wrap gap-1 text-center" },
          tags
            .slice(0, 5)
            .map((tag) =>
              h(resolveComponent("UBadge"), {
                label: tag,
                color: "neutral",
                variant: "subtle",
              }),
            )
            .concat(
              tags.length > 5
                ? [
                    h(
                      "span",
                      { class: "text-sm text-muted" },
                      `+${tags.length - 5}`,
                    ),
                  ]
                : [],
            ),
        );
      },
    },
    {
      accessorKey: "targets",
      header: "Targets",
      icon: "i-lucide-locate-fixed",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("targets").length),
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
      type: "text",
      placeholder: "Filter by owner username...",
    },
    ...(userStore.is_admin
      ? [
          {
          key: "owner_id",
          label: "My projects",
            type: "boolean" as const,
          value: userStore.user,
          },
        ]
      : []),
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
      text: "Are you sure you want to delete this project?",
      class: "text-gray-900 dark:text-white",
    },
    {
      text: project.name,
      class: "font-bold text-lg text-center my-2 text-gray-900 dark:text-white",
    },
    {
      text: "All its data including assets, findings, and scans will be permanently deleted. This action can't be undone.",
      class:
        "text-sm text-red-600 bg-red-50 dark:bg-red-900/10 p-3 rounded border border-red-200 dark:border-red-800 mt-5",
    },
  ],
  canRead: true,
  canCreate: userStore.is_admin,
  canEdit: (_project: Project) => userStore.is_admin,
  canDelete: (_project: Project) => userStore.is_admin,
});
</script>

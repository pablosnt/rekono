<template>
  <MainPanel>
    <CrudPage :config="config" />
  </MainPanel>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig } from "~/types/crud";
import type { TableColumn } from "@nuxt/ui";
import { useUserStore } from "~/store/user";

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
      cell: ({ row }) => h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("name")),
      enableResizing: true,
    },
    {
      accessorKey: "description",
      header: "Description",
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
  ] as TableColumn<Project>[],
  tableColumnsVisibility: {
    id: false,
    description: false,
    owner: false,
  },
  searchable: true,
  searchPlaceholder: "Search projects...",
  filters: [
    {
      key: "tags",
      label: "Tag",
      type: "text",
      placeholder: "Filter by tag...",
    },
  ],
  ordering: ["id", "name"],
  defaultOrdering: "-id",
  // formFields: [
  //   {
  //     key: "name",
  //     label: "Name",
  //     type: "text",
  //     required: true,
  //     placeholder: "Enter project name",
  //   },
  //   {
  //     key: "description",
  //     label: "Description",
  //     type: "textarea",
  //     placeholder: "Enter project description",
  //   },
  // ],
  canRead: true,
  canCreate: userStore.is_admin,
  canEdit: (project: Project) => userStore.is_admin,
  canDelete: (project: Project) => userStore.is_admin,
  deleteMessage: (project: Project) =>
    `Are you sure you want to delete "${project.name}"? All associated data including targets findings, and executions will be permanently deleted.`,
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
});
</script>

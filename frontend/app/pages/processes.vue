<template>
  <CrudPage :config="config" />
  <!-- TODO: Customize the creation form, and the edition form to modify the process steps -->
  <!-- TODO: Add Run button to the actions (before the menu) to allow running the process -->
</template>

<script setup lang="ts">
import { h, resolveComponent } from "vue";
import type { CrudConfig, FilterOption } from "~/types/crud";
import * as z from "zod";
import { useUserStore } from "~/store/user";
import type { Process } from "~/types/processes";
import type { Tool } from "~/types/tools";

const userStore = useUserStore();
const validation = useValidation();
const utils = useUtils();
const api = useApi("/api/tools/");
const toolOptions = ref<FilterOption[]>([]);

onMounted(() => {
  api.list("", {}, true).then((response) => {
    toolOptions.value = (response.items as Tool[]).map((tool) => ({
      avatar: tool.icon ? { src: tool.icon } : undefined,
      label: tool.name,
      value: tool.id,
    }));
  });
});

const config: CrudConfig<Process> = reactive({
  endpoint: "/api/processes/",
  entityName: "Process",
  entityNamePlural: "Processes",
  icon: "i-lucide-workflow",
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
        h(
          "div",
          { class: "text-muted-foreground whitespace-pre-wrap py-1" },
          row.getValue("description"),
        ),
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
      accessorKey: "steps",
      header: "Steps",
      icon: "i-lucide-list",
      cell: ({ row }) => {
        const steps = (row.original as Process).steps;
        return h("span", {}, steps?.length || 0);
      },
    },
    {
      accessorKey: "owner",
      header: "Owner",
      icon: "i-lucide-user",
      cell: ({ row }) => {
        const owner = row.getValue("owner") as Process["owner"];
        return owner?.username ? `@${owner.username}` : "";
      },
      enableResizing: true,
    },
    {
      accessorKey: "likes",
      header: "Likes",
      icon: "i-lucide-thumbs-up",
      cell: ({ row }) => {
        const item = row.original as Process;
        return h(resolveComponent("CrudLikes"), {
          itemId: item.id,
          endpoint: "/api/processes/",
          liked: item.liked,
          count: item.likes,
          onUpdate: (liked: boolean, count: number) => {
            item.liked = liked;
            item.likes = count;
          },
        });
      },
    },
  ],
  tableColumnsVisibility: {
    id: false,
    owner: false,
  },
  searchable: true,
  searchPlaceholder: "Search processes...",
  get filters() {
    return [
      {
        key: "stage",
        label: "Stage",
        icon: "i-lucide-layers",
        type: "select" as const,
        options: utils.stageOptions,
      },
      {
        key: "tag",
        label: "Tag",
        icon: "i-lucide-tag",
        type: "text" as const,
        placeholder: "Filter by tag...",
      },
      {
        key: "tool",
        label: "Tool",
        icon: "i-lucide-wrench",
        type: "select" as const,
        options: toolOptions.value,
      },
      {
        key: "owner",
        label: "Owner",
        icon: "i-lucide-user",
        type: "text" as const,
        placeholder: "Filter by owner username...",
      },
      ...(userStore.is_admin
        ? [
            {
              key: "owner_id",
              label: "My processes",
              type: "boolean" as const,
              value: userStore.user,
            },
          ]
        : []),
    ];
  },
  ordering: ["id", "name", "owner", { id: "likes_count", label: "Likes" }],
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  formFields: [
    {
      key: "name",
      label: "Name",
      type: "text",
      required: true,
      placeholder: "Enter process name",
    },
    {
      key: "description",
      label: "Description",
      type: "textarea",
      required: true,
      placeholder: "Enter process description",
    },
    {
      key: "tags",
      label: "Tags",
      type: "tags",
      required: false,
      placeholder: "Add process tags",
      icon: "i-lucide-tag",
    },
  ],
  formSchema: z.object({
    name: validation.name("name", true, 100),
    description: validation.text("description", true),
    tags: z.array(validation.name("tag", true, 100)).optional(),
  }),
  deleteMessage: (process: Process) => [
    {
      text: "Are you sure you want to delete this process?",
      class: "text-gray-900 dark:text-white",
    },
    {
      text: process.name,
      class: "font-bold text-lg text-center my-2 text-gray-900 dark:text-white",
    },
  ],
  canRead: userStore.is_auditor,
  canCreate: userStore.is_auditor,
  canEdit: (process: Process) =>
    userStore.is_admin || userStore.isOwner(process, "owner"),
  canDelete: (process: Process) =>
    userStore.is_admin || userStore.isOwner(process, "owner"),
});
</script>

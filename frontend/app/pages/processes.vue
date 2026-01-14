<template>
  <div>
    <CrudPage :config="config">
      <template #actions="{ item }">
        <TasksRunButton :process="item" />
      </template>
    </CrudPage>
    <UModal v-model:open="processModalOpen" fullscreen>
      <template #header>
        <div class="flex items-center justify-between w-full">
          <p class="text-gray-900 dark:text-white font-bold text-lg">
            {{ selectedProcess ? selectedProcess.name : "" }}
          </p>
          <div class="flex items-center gap-2">
            <TasksRunButton :process="selectedProcess" />
            <UButton
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              @click="processModalOpen = false"
            />
          </div>
        </div>
      </template>
      <template #body>
        <ProcessStepsForm v-if="selectedProcess" :process="selectedProcess" />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { h, resolveComponent } from "vue";
import type { CrudConfig, FilterOption } from "~/types/crud";
import * as z from "zod";
import { useUserStore } from "~/store/user";
import type { Process } from "~/types/processes";

const userStore = useUserStore();
const validation = useValidation();
const utils = useUtils();
const toolOptions = ref<FilterOption[]>([]);
const userOptions = ref<FilterOption[]>([]);
const processModalOpen = ref(false);
const selectedProcess = ref();

onMounted(() => {
  utils.getToolOptions(toolOptions);
  if (userStore.is_auditor) {
    utils.getUserOptions(userOptions, { role: "Admin" });
    utils.getUserOptions(userOptions, { role: "Auditor" });
  }
});

const config: CrudConfig<Process> = reactive({
  endpoint: "/api/processes/",
  entityName: "Process",
  entityNamePlural: "Processes",
  icon: "i-lucide-workflow",
  createForm: resolveComponent("ProcessForm"),
  updateOnCreateModalOpen: true,
  editForm: resolveComponent("ProcessForm"),
  updateOnEditModalOpen: true,
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
  onItemClick: (item: Process) => {
    processModalOpen.value = true;
    selectedProcess.value = item;
  },
  searchable: true,
  searchPlaceholder: "Search processes...",
  filters: [
    {
      key: "tag",
      label: "Tag",
      icon: "i-lucide-tag",
      type: "text" as const,
      placeholder: "Filter by tag...",
    },
    {
      key: "stage",
      label: "Stage",
      icon: "i-lucide-layers",
      type: "select" as const,
      options: utils.stageOptions,
    },

    {
      key: "tool",
      label: "Tool",
      icon: "i-lucide-square-terminal",
      type: "select" as const,
      options: toolOptions,
    },
    ...(userStore.is_auditor
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
  formFullscreen: true,
  deleteMessage: (process: Process) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this process?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: process.name,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
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

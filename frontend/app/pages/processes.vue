<template>
  <div>
    <CrudPage :config="config">
      <template #actions="{ item }">
        <TasksButton :process="item" />
      </template>
    </CrudPage>
    <UModal v-model:open="processModalOpen" fullscreen>
      <template #header>
        <div class="flex items-center justify-between w-full">
          <h2 class="text-gray-900 dark:text-white font-bold text-lg">
            {{ selectedProcess?.name }}
          </h2>
          <div class="flex items-center gap-2">
            <TasksButton :process="selectedProcess" />
            <UButton
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              aria-label="Close"
              @click="processModalOpen = false"
            />
          </div>
        </div>
      </template>
      <template #body>
        <LazyStepsForm v-if="selectedProcess" :process="selectedProcess" />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { h, resolveComponent } from "vue";
import type { CrudConfig, FilterOption } from "~/types/crud";
import * as z from "zod";
import { useUserStore } from "~/store/user";
import type { Process } from "~/types/models";
import { stages } from "~/constants";

const userStore = useUserStore();
const validation = useValidation();
const options = useOptions();
const table = useTable();
const toolOptions = ref<FilterOption[]>([]);
const userOptions = ref<FilterOption[]>([]);
const processModalOpen = ref(false);
const selectedProcess = ref();

onMounted(() => {
  options.tools(toolOptions);
  options.users(userOptions, { role: "Admin", is_active: true });
  options.users(userOptions, { role: "Auditor", is_active: true });
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
      cell: ({ row }) =>
        table.valueCell(
          row.getValue("description"),
          "text-muted-foreground whitespace-pre-wrap py-1",
        ),
    },
    {
      accessorKey: "tags",
      header: "Tags",
      icon: "i-lucide-tag",
      cell: ({ row }) =>
        h(resolveComponent("Tags"), { tags: row.getValue("tags") }),
    },
    {
      accessorKey: "steps",
      header: "Steps",
      icon: "i-lucide-list",
      cell: ({ row }) =>
        table.valueCell(formatCount(row.original.steps?.length || 0)),
    },
    {
      accessorKey: "owner",
      header: "Owner",
      icon: "i-lucide-user",
      cell: ({ row }) => table.usernameCell(row.getValue("owner")),
    },
    {
      accessorKey: "likes",
      header: "Likes",
      icon: "i-lucide-thumbs-up",
      cell: ({ row }) =>
        h(resolveComponent("Likes"), {
          itemId: row.original.id,
          endpoint: "/api/processes/",
          liked: row.original.liked,
          count: row.original.likes,
          onUpdate: (liked: boolean, count: number) => {
            row.original.liked = liked;
            row.original.likes = count;
          },
        }),
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
      options: stages,
    },

    {
      key: "tool",
      label: "Tool",
      icon: "i-lucide-square-terminal",
      type: "select" as const,
      options: toolOptions,
    },
    {
      key: "owner",
      label: "Owner",
      icon: "i-lucide-user",
      type: "select" as const,
      options: userOptions,
    },
    {
      key: "like",
      label: "Favourites",
      icon: "i-lucide-heart",
      type: "checkbox" as const,
    },
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
  createForm: resolveComponent("ProcessesForm"),
  updateOnCreateModalOpen: true,
  editForm: resolveComponent("ProcessesForm"),
  updateOnEditModalOpen: true,
  deleteMessage: (process: Process) =>
    buildDeleteMessage("process", process.name),
  canRead: userStore.is_auditor,
  canCreate: userStore.is_auditor,
  canEdit: (process: Process) =>
    userStore.is_admin || userStore.isOwner(process),
  canDelete: (process: Process) =>
    userStore.is_admin || userStore.isOwner(process),
});
</script>

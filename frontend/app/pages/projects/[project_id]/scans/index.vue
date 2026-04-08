<template>
  <CrudPage ref="page" :config="config" @fetched="onFetched">
    <template #create-button>
      <TasksButton :project="{ id: parseInt(route.params.project_id) }" />
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import type { Task } from "~/types/models";
import { useUserStore } from "~/store/user";
import {
  stages,
  intensities,
  targetTypes,
  executionStatuses,
} from "~/constants";

definePageMeta({ layout: "project" });
const userStore = useUserStore();
const route = useRoute();
const options = useOptions();
const api = useApi("/api/tasks/");
const table = useTable();
const page = ref();
const refresh = ref<ReturnType<typeof setTimeout> | null>(null);
const targetOptions = ref<FilterOption[]>([]);
const executorOptions = ref<FilterOption[]>([]);
const toolOptions = ref<FilterOption[]>([]);
const configurationOptions = ref<FilterOption[]>([]);
const processOptions = ref<FilterOption[]>([]);

function onFetched(items: Task[]) {
  if (
    items.some(
      (task) =>
        task.status === "Running" ||
        task.status === "Requested" ||
        task.executions.length === 0,
    )
  ) {
    refresh.value = setTimeout(() => {
      page.value?.fetch();
    }, 10000);
  } else if (refresh.value) {
    clearTimeout(refresh.value);
    refresh.value = null;
  }
}

onMounted(() => {
  options.targets(targetOptions, { project: route.params.project_id });
  options.users(executorOptions, { is_active: true, role: "Admin" });
  options.users(executorOptions, { is_active: true, role: "Auditor" });
  options.tools(toolOptions);
  options.configurations(configurationOptions, { ordering: "-tool" });
  options.processes(processOptions);
});

onUnmounted(() => {
  if (refresh.value) {
    clearInterval(refresh.value);
  }
});

const config: CrudConfig<Task> = reactive({
  endpoint: "/api/tasks/",
  entityName: "Scan",
  entityNamePlural: "Scans",
  icon: "i-lucide-play",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      id: "scanner",
      header: "Scanner",
      icon: "i-lucide-terminal",
      cell: ({ row }) => {
        const task = row.original as Task;
        return task.process
          ? table.valueCell(task.process.name)
          : table.toolCell(task.configuration?.tool, task.configuration);
      },
    },
    {
      id: "target",
      header: "Target",
      icon: "i-lucide-locate-fixed",
      cell: ({ row }) => {
        const task = row.original as Task;
        let label = task.target?.target;
        if (task.target_port) {
          label += `:${task.target_port.port}`;
          if (task.target_port.path) {
            label +=
              task.target_port.path[0] === "/"
                ? task.target_port.path
                : `/${task.target_port.path}`;
          }
        }
        return table.linkCell(
          `/projects/${route.params.project_id}/targets/${task.target?.id}`,
          targetTypes.find((t) => t.value === task.target?.type)?.icon ||
            "i-lucide-locate-fixed",
          label,
        );
      },
    },
    {
      id: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const task = row.original as Task;
        const status = executionStatuses.find((s) => s.value === task.status);
        return task.status === "Running"
          ? h(resolveComponent("UProgress"), {
              status: true,
              modelValue: task.progress,
              max: 100,
              color: "warning",
            })
          : table.badgeCell(status?.value, status?.icon, status.color);
      },
    },
    {
      accessorKey: "intensity",
      header: "Intensity",
      icon: "i-lucide-gauge",
      cell: ({ row }) => {
        const intensityValue = row.getValue("intensity") as string;
        return table.badgeCell(
          intensityValue,
          undefined,
          intensities.find((i) => i.label === intensityValue)?.color ||
            "neutral",
        );
      },
    },
    {
      accessorKey: "executor",
      header: "Executor",
      icon: "i-lucide-user",
      cell: ({ row }) => table.usernameCell(row.getValue("executor")),
    },
    {
      accessorKey: "start",
      header: "Start",
      icon: "i-lucide-play-circle",
      cell: ({ row }) => {
        const start = row.getValue("start") as Task["start"];
        return table.valueCell(
          start ? new Date(start).toLocaleString() : undefined,
        );
      },
    },
    {
      accessorKey: "end",
      header: "End",
      icon: "i-lucide-stop-circle",
      cell: ({ row }) => {
        const end = row.getValue("end") as Task["end"];
        return table.valueCell(
          end ? new Date(end).toLocaleString() : undefined,
        );
      },
    },
    {
      id: "duration",
      header: "Duration",
      icon: "i-lucide-timer",
      cell: ({ row }) =>
        table.valueCell(
          row.original.start && row.original.end
            ? duration(row.original.start, row.original.end)
            : undefined,
        ),
    },
    {
      id: "scheduled",
      header: "Scheduled",
      icon: "i-lucide-calendar-clock",
      cell: ({ row }) =>
        table.valueCell(
          !row.original.start && row.original.scheduled_at
            ? new Date(row.original.scheduled_at).toLocaleString()
            : undefined,
        ),
    },
    {
      id: "repeat",
      header: "Monitor",
      icon: "i-lucide-repeat",
      cell: ({ row }) =>
        table.valueCell(
          row.original.repeat_in && row.original.repeat_time_unit
            ? `Every ${row.original.repeat_in} ${row.original.repeat_time_unit}`
            : undefined,
        ),
    },
  ] as CrudTableColumn<Task>[],
  tableColumnsVisibility: {
    id: false,
    executor: false,
    end: false,
    scheduled: false,
  },
  itemLink: (item: Task) =>
    `/projects/${route.params.project_id}/scans/${item.id}`,
  searchable: true,
  searchPlaceholder: "Search scans...",
  filters: [
    {
      key: "target",
      label: "Target",
      icon: "i-lucide-locate-fixed",
      type: "select" as const,
      options: targetOptions,
    },
    {
      key: "process",
      label: "Process",
      icon: "i-lucide-workflow",
      type: "select" as const,
      options: processOptions,
    },
    {
      key: "executed_tool",
      label: "Tool",
      icon: "i-lucide-square-terminal",
      type: "select" as const,
      options: toolOptions,
    },
    {
      key: "executed_configuration",
      label: "Configuration",
      icon: "i-lucide-terminal",
      type: "select" as const,
      options: configurationOptions,
    },
    {
      key: "stage",
      label: "Stage",
      icon: "i-lucide-layers",
      type: "select" as const,
      options: stages,
    },
    {
      key: "intensity",
      label: "Intensity",
      icon: "i-lucide-gauge",
      type: "select" as const,
      options: intensities,
    },
    {
      key: "executor",
      label: "Executor",
      icon: "i-lucide-user",
      type: "select" as const,
      options: executorOptions,
    },
  ],
  defaultFilters: { project: route.params.project_id as string },
  ordering: [
    "id",
    { id: "target", label: "Target" },
    { id: "process", label: "Process" },
    { id: "configuration__tool", label: "Tool" },
    { id: "configuration", label: "Configuration" },
    { id: "start", label: "Start" },
    { id: "end", label: "End" },
  ],
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  tableCopyId: true,
  customDropdownActions: (task: Task) => {
    if (!userStore.is_auditor) return [];
    const actions = [];
    if (task.progress === 100) {
      actions.push({
        label: "Repeat",
        icon: "i-lucide-play",
        color: "success",
        onSelect: () => {
          api
            .create(`${task.id}/repeat/`, {}, {}, "Scan")
            .then((response) =>
              navigateTo(
                `/projects/${route.params.project_id}/scans/${response.id}`,
              ),
            );
        },
      });
    }
    return actions;
  },
  deleteMessage: (task: Task) =>
    buildDeleteMessage(
      "scan",
      getTaskName(task, true),
      undefined,
      undefined,
      "cancel",
    ),
  deleteVerb: "Cancel",
  deleteIcon: "i-lucide-x",
  canRead: userStore.is_auditor,
  canCreate: userStore.is_auditor,
  canEdit: false,
  canDelete: (task: Task) => userStore.is_auditor && task.progress !== 100,
});
</script>

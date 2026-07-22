<template>
  <div>
    <CrudPage
      ref="page"
      :config="config"
      :on-create="() => tasksButton?.open()"
      @fetched="onFetched"
    >
      <template #create-button>
        <TasksButton
          ref="tasksButton"
          :project="{ id: parseInt(route.params.project_id) }"
        />
      </template>
    </CrudPage>
    <ReportsButton
      v-model:open="showReportModal"
      :task-id="selectedTask?.id"
      only-modal
    />
    <NotesButton
      v-if="selectedTask"
      ref="notesButton"
      :task="selectedTask?.id"
    />
  </div>
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

const userStore = useUserStore();
const route = useRoute();
const options = useOptions();
const api = useApi("/api/tasks/");
const table = useTable();
const { refreshPanelCounts, projectHasActiveFindings } = usePanel();
const page = ref();
const tasksButton = ref();
const notesButton = ref();
const showReportModal = ref(false);
const selectedTask = ref();
const refresh = ref<ReturnType<typeof setTimeout> | null>(null);
const targetOptions = ref<FilterOption[]>([]);
const executorOptions = ref<FilterOption[]>([]);
const toolOptions = ref<FilterOption[]>([]);
const configurationOptions = ref<FilterOption[]>([]);
const processOptions = ref<FilterOption[]>([]);
const runningTasks = ref(0);

function onFetched(items: Task[]) {
  const count = items.filter(
    (task) =>
      task.status !== "Cancelled" &&
      (!task.scheduled_at || new Date(task.scheduled_at) <= new Date()) &&
      (task.status === "Running" ||
        task.status === "Requested" ||
        task.executions.length === 0),
  ).length;
  if (count < runningTasks.value) {
    refreshPanelCounts();
  }
  runningTasks.value = count;
  if (count > 0) {
    if (refresh.value) clearTimeout(refresh.value);
    refresh.value = setTimeout(() => {
      page.value?.fetch();
    }, 5000);
  } else if (refresh.value) {
    clearTimeout(refresh.value);
    refresh.value = null;
  }
}

onMounted(() => {
  options.targets(targetOptions, { project: route.params.project_id });
  options.users(executorOptions, {
    is_active: true,
    role: "Admin",
    project: route.params.project_id,
  });
  options.users(executorOptions, {
    is_active: true,
    role: "Auditor",
    project: route.params.project_id,
  });
  options.tools(toolOptions, { ordering: "-liked,-id" });
  options.configurations(configurationOptions, { ordering: "-tool" });
  options.processes(processOptions, { ordering: "-liked,-id" });
});

onUnmounted(() => {
  if (refresh.value) clearTimeout(refresh.value);
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
      cell: ({ row }) =>
        row.original.process
          ? table.valueCell(row.original.process.name)
          : table.toolCell(
              row.original.configuration?.tool,
              row.original.configuration,
            ),
    },
    {
      id: "target",
      header: "Target",
      icon: "i-lucide-locate-fixed",
      cell: ({ row }) => {
        let label = row.original.target?.target;
        if (row.original.target_port) {
          label += `:${row.original.target_port.port}`;
          if (row.original.target_port.path) {
            label +=
              row.original.target_port.path[0] === "/"
                ? row.original.target_port.path
                : `/${row.original.target_port.path}`;
          }
        }
        return table.linkCell(
          `/projects/${route.params.project_id}/targets/${row.original.target?.id}`,
          targetTypes.find((t) => t.value === row.original.target?.type)
            ?.icon || "i-lucide-locate-fixed",
          undefined,
          label,
        );
      },
    },
    {
      id: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const status = executionStatuses.find(
          (s) => s.value === row.original.status,
        );
        return row.original.status === "Running"
          ? h(resolveComponent("UProgress"), {
              status: true,
              modelValue: row.original.progress,
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
            : row.original.status === "Running" && row.original.start
              ? duration(row.original.start, new Date().toISOString())
              : undefined,
        ),
    },
    {
      id: "scheduled",
      header: "Scheduled",
      icon: "i-lucide-calendar-clock",
      cell: ({ row }) =>
        table.valueCell(
          row.original.scheduled_at
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
    "target",
    "process",
    { id: "configuration__tool", label: "Tool" },
    "configuration",
    "start",
    "end",
  ],
  defaultOrdering: "-end",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  tableCopyId: true,
  customDropdownActions: (task: Task) => [
    ...(task.progress === 100
      ? [
          ...(userStore.is_auditor
            ? [
                {
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
                },
              ]
            : []),
          ...(projectHasActiveFindings.value
            ? [
                {
                  label: "Generate a report",
                  icon: "i-lucide-file-text",
                  onSelect: (t: Task) => {
                    selectedTask.value = t;
                    showReportModal.value = true;
                  },
                },
              ]
            : []),
        ]
      : []),
    {
      label: "Take note",
      icon: "i-lucide-notebook",
      onSelect: () => {
        selectedTask.value = task;
        return nextTick(() => notesButton.value?.createNote());
      },
    },
  ],
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
  canRead: true,
  canCreate: userStore.is_auditor,
  canEdit: false,
  canDelete: (task: Task) => userStore.is_auditor && task.progress !== 100,
});
</script>

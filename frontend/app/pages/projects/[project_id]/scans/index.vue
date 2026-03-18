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

definePageMeta({ layout: "project" });
const userStore = useUserStore();
const route = useRoute();
const backend = useBackend();
const utils = useUtils();
const api = useApi("/api/tasks/");
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
  backend.getTargetOptions(targetOptions, {
    project: route.params.project_id as string,
  });
  backend.getUserOptions(executorOptions, { is_active: true, role: "Auditor" });
  backend.getToolOptions(toolOptions);
  backend.getConfigurationOptions(configurationOptions, { ordering: "-tool" });
  backend.getProcessOptions(processOptions);
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
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      id: "scanner",
      header: "Scanner",
      icon: "i-lucide-terminal",
      cell: ({ row }) => {
        const task = row.original as Task;
        if (task.process) {
          return h("span", { class: "font-medium" }, task.process.name);
        } else {
          return h("div", { class: "flex items-center gap-2" }, [
            task.configuration?.tool.icon
              ? h(resolveComponent("UAvatar"), {
                  src: task.configuration?.tool.icon,
                  size: "2xs",
                })
              : h(resolveComponent("UIcon"), {
                  name: "i-lucide-square-terminal",
                  class: "w-4 h-4 text-muted-foreground shrink-0",
                }),
            h(
              "span",
              { class: "font-medium" },
              `${task.configuration?.tool.name}: ${task.configuration?.name}`,
            ),
          ]);
        }
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
        return h(
          "a",
          {
            class:
              "flex items-center gap-2 font-medium hover:text-primary hover:underline",
            href: `/projects/${route.params.project_id}/targets/${task.target?.id}`,
          },
          [
            h(resolveComponent("UIcon"), {
              class: "w-4 h-4 text-muted-foreground shrink-0",
              name:
                backend.targetTypes.find((t) => t.value === task.target?.type)
                  ?.icon || "i-lucide-locate-fixed",
            }),
            h("span", { class: "font-medium" }, label),
          ],
        );
      },
    },
    {
      id: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const task = row.original as Task;
        const status = backend.executionStatuses.find(
          (s) => s.value === task.status,
        );
        return task.status === "Running"
          ? h(resolveComponent("UProgress"), {
              status: true,
              modelValue: task.progress,
              max: 100,
              color: "warning",
            })
          : h(
              resolveComponent("UBadge"),
              { variant: "subtle", color: status.color },
              [
                h(resolveComponent("UIcon"), {
                  name: status.icon,
                  class: "text-lg",
                }),
                h("span", { class: "font-medium" }, status.value),
              ],
            );
      },
    },
    {
      accessorKey: "intensity",
      header: "Intensity",
      icon: "i-lucide-gauge",
      cell: ({ row }) => {
        const intensityValue = row.getValue("intensity") as string;
        const intensity = backend.intensities.find(
          (i) => i.label === intensityValue,
        );
        return h(
          resolveComponent("UBadge"),
          {
            color: intensity?.color || "neutral",
            variant: "subtle",
            class: "font-medium",
          },
          { default: () => intensityValue },
        );
      },
    },
    {
      accessorKey: "executor",
      header: "Executor",
      icon: "i-lucide-user",
      cell: ({ row }) => {
        const executor = row.getValue("executor") as Task["executor"];
        return h(
          "span",
          { class: "font-medium" },
          executor?.username ? `@${executor.username}` : "—",
        );
      },
    },
    {
      accessorKey: "start",
      header: "Start",
      icon: "i-lucide-play-circle",
      cell: ({ row }) => {
        const start = row.getValue("start") as Task["start"];
        return h(
          "span",
          { class: "font-medium" },
          start ? new Date(start).toLocaleString() : "—",
        );
      },
    },
    {
      accessorKey: "end",
      header: "End",
      icon: "i-lucide-stop-circle",
      cell: ({ row }) => {
        const end = row.getValue("end") as Task["end"];
        return h(
          "span",
          { class: "font-medium" },
          end ? new Date(end).toLocaleString() : "—",
        );
      },
    },
    {
      id: "duration",
      header: "Duration",
      icon: "i-lucide-timer",
      cell: ({ row }) => {
        const task = row.original as Task;
        return h(
          "span",
          { class: "font-medium tabular-nums" },
          task.start && task.end ? utils.duration(task.start, task.end) : "—",
        );
      },
    },
    {
      id: "scheduled",
      header: "Scheduled",
      icon: "i-lucide-calendar-clock",
      cell: ({ row }) => {
        const task = row.original as Task;
        return h(
          "span",
          { class: "font-medium" },
          !task.start && task.scheduled_at
            ? new Date(task.scheduled_at).toLocaleString()
            : "—",
        );
      },
    },
    {
      id: "repeat",
      header: "Monitor",
      icon: "i-lucide-repeat",
      cell: ({ row }) => {
        const task = row.original as Task;
        return h(
          "span",
          { class: "font-medium" },
          task.repeat_in && task.repeat_time_unit
            ? `Every ${task.repeat_in} ${task.repeat_time_unit}`
            : "—",
        );
      },
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
      valueKey: "id",
      labelKey: "target",
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
      options: backend.stages,
    },
    {
      key: "intensity",
      label: "Intensity",
      icon: "i-lucide-gauge",
      type: "select" as const,
      options: backend.intensities,
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
  deleteMessage: (task: Task) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to cancel this scan?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: backend.getTaskName(task, true),
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
  deleteVerb: "Cancel",
  deleteIcon: "i-lucide-x",
  canRead: userStore.is_auditor,
  canCreate: userStore.is_auditor,
  canEdit: false,
  canDelete: (task: Task) => userStore.is_auditor && task.progress !== 100,
});
</script>

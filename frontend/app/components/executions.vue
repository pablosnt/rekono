<template>
  <div>
    <CrudPage
      ref="page"
      :config="config"
      :disable-url-sync="disableUrlSync"
      @fetched="(items) => onExecutions(items)"
    >
      <template #actions="{ item }">
        <UTooltip v-if="item.has_report" text="Download report">
          <UButton
            icon="i-lucide-download"
            variant="ghost"
            size="xl"
            aria-label="Download execution report"
            @click="api.download(`${item.id}/report/`)"
          />
        </UTooltip>
      </template>
    </CrudPage>
    <LazyUSlideover
      v-model:open="outputOpen"
      inset
      portal
      :ui="{ content: 'sm:max-w-5xl' }"
    >
      <template #header="{ close }">
        <div class="flex items-center gap-3">
          <div
            class="size-10 rounded-lg bg-muted flex items-center justify-center shrink-0"
          >
            <UAvatar
              v-if="selectedExecution.configuration?.tool.icon"
              :src="selectedExecution.configuration.tool.icon"
              :alt="selectedExecution.configuration.tool.name"
            />
            <UIcon
              v-else
              name="i-lucide-square-terminal"
              class="text-xl text-primary"
            />
          </div>
          <div class="min-w-0">
            <h1 class="text-xl font-bold font-mono tracking-tight truncate">
              {{ selectedExecution.configuration?.tool.name }}
            </h1>
            <p class="text-sm text-muted">
              {{ selectedExecution.configuration.name }}
            </p>
          </div>
        </div>
        <div class="absolute top-5 right-5">
          <div class="flex items-center gap-1">
            <UTooltip
              v-if="selectedExecution.has_report"
              text="Download report"
            >
              <UButton
                icon="i-lucide-download"
                variant="ghost"
                size="xl"
                aria-label="Download report"
                @click="api.download(`${selectedExecution.id}/report/`)"
              />
            </UTooltip>
            <UButton
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              aria-label="Close"
              @click="close"
            />
          </div>
        </div>
      </template>
      <template #body>
        <pre
          class="font-mono text-sm whitespace-pre-wrap break-all bg-neutral-950 text-neutral-100 p-4 rounded-lg overflow-auto h-full leading-relaxed"
          >{{ selectedExecution?.output_plain }}</pre
        >
      </template>
    </LazyUSlideover>
  </div>
</template>

<script setup lang="ts">
import { stages, executionStatuses } from "~/constants";
import type { Execution, Finding } from "~/types/models";
import type { CrudConfig, FilterOption } from "~/types/crud";
import { useIntegrationsStore } from "~/store/integrations";

const props = defineProps<{
  task?: number;
  finding?: Finding;
  findingType?: string;
  disableUrlSync?: boolean;
}>();
const emit = defineEmits<{
  fetched: [items: Execution[]];
  finished: [count: number];
}>();

const api = useApi("/api/executions/");
const table = useTable();
const route = useRoute();
const options = useOptions();
const integrations = useIntegrationsStore();
const { showDefectDojo } = useCurrentProject();
const { refreshPanelCounts } = usePanel();
const page = ref();
const selectedExecution = ref();
const runningExecutions = ref(0);
const outputOpen = ref(false);
const toolOptions = ref<FilterOption[]>([]);

const config: CrudConfig<Execution> = reactive({
  endpoint: "/api/executions/",
  entityName: "Execution",
  entityNamePlural: "Executions",
  headerHideTitle: true,
  icon: "i-lucide-square-terminal",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      id: "tool",
      header: "Tool",
      icon: "i-lucide-square-terminal",
      cell: ({ row }) =>
        table.toolCell(
          row.original.configuration.tool,
          undefined,
          props.task
            ? undefined
            : `/projects/${route.params.project_id}/scans/${row.original.task}`,
        ),
    },
    {
      accessorKey: "configuration",
      header: "Configuration",
      icon: "i-lucide-file-code-corner",
      cell: ({ row }) => table.valueCell(row.original.configuration.name),
    },
    {
      id: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const status = executionStatuses.find(
          (s) => s.value === row.original.status,
        );
        const isRunning = row.original.status === "Running";
        return h(
          resolveComponent("UTooltip"),
          {
            text: row.original.status,
            content: { side: "right", sideOffset: 8, collisionPadding: 8 },
          },
          {
            default: () =>
              h(resolveComponent("UIcon"), {
                name: status?.icon,
                class: `text-lg text-${status?.color}${isRunning ? " animate-spin" : ""}`,
                "aria-label": row.original.status,
              }),
          },
        );
      },
    },
    {
      accessorKey: "start",
      header: "Start",
      icon: "i-lucide-play-circle",
      cell: ({ row }) => {
        const start = row.getValue("start") as Execution["start"];
        return table.valueCell(
          start ? new Date(start).toLocaleString() : undefined,
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
      id: "skipped",
      header: "Skipped",
      icon: "i-lucide-skip-forward",
      cell: ({ row }) => table.valueCell(row.original.skipped_reason),
    },
    ...(showDefectDojo.value
      ? [
          {
            accessorKey: "defectdojo",
            header: "DefectDojo",
            avatar: { src: integrations.defectdojo?.integration.icon },
            cell: ({ row }) =>
              row.original.defectdojo_test_id
                ? h(resolveComponent("DefectdojoLink"), {
                    entity: "test",
                    id: row.original.defectdojo_test_id,
                    size: "sm",
                  })
                : table.noDataCell,
          },
        ]
      : []),
  ],
  tableColumnsVisibility: {
    skipped: false,
    id: false,
  },
  pageSizeOptions: [24, 50, 100],
  onItemClick: (item: Execution) => {
    if (item.output_plain) {
      selectedExecution.value = item;
      outputOpen.value = true;
    }
  },
  searchable: true,
  searchPlaceholder: "Search executions...",
  filters: [
    {
      key: "tool",
      label: "Tool",
      icon: "i-lucide-square-terminal",
      type: "select" as const,
      options: toolOptions,
    },
    {
      key: "stage",
      label: "Stage",
      icon: "i-lucide-layers",
      type: "select" as const,
      options: stages,
    },
    {
      key: "status",
      label: "Status",
      icon: "i-lucide-activity",
      type: "select" as const,
      options: executionStatuses,
      labelKey: "value",
    },
  ],
  defaultFilters: props.task
    ? { task: props.task }
    : { [props.findingType.toLowerCase()]: props.finding.id },
  defaultOrdering: "-start,id",
  emptyMessage: `No executions yet.${props.task ? " The task may still be waiting to be processed" : ""}`,
  tableCopyId: false,
  canRead: true,
  canCreate: false,
  canEdit: false,
  canDelete: false,
});

function onExecutions(data: Execution[]) {
  emit("fetched", data);
  const count = data.filter(
    (e) => e.status === "Running" || e.status === "Requested",
  ).length;
  if (count < runningExecutions.value) {
    emit("finished", runningExecutions.value - count);
    refreshPanelCounts();
  }
  runningExecutions.value = count;
}

onMounted(() => {
  options.tools(toolOptions);
  integrations.fetchDefectDojo();
});

defineExpose({ page });
</script>

<template>
  <div class="w-full">
    <!-- TODO: Add scan's items to the breadcrum -->
    <!-- TODO: Here and on target, we are getting entity's data twice. We should find a way to solve it -->
    <UPageCard v-if="task" variant="naked" class="mb-10">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div
            class="size-10 rounded-lg bg-muted flex items-center justify-center shrink-0"
          >
            <UAvatar
              v-if="task.configuration?.tool.icon"
              :src="task.configuration.tool.icon"
            />
            <UIcon
              v-else
              :name="
                task.process ? 'i-lucide-workflow' : 'i-lucide-square-terminal'
              "
              class="text-xl text-highlighted text-primary"
            />
          </div>
          <div class="min-w-0">
            <h1 class="text-xl font-bold font-mono tracking-tight truncate">
              {{
                task.process ? task.process.name : task.configuration?.tool.name
              }}
            </h1>
            <p v-if="task.configuration" class="text-sm text-muted">
              {{ task.configuration.name }}
            </p>
            <p v-else-if="task.process" class="text-sm text-muted">Process</p>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <UProgress
            v-if="task.status === 'Running'"
            class="w-64"
            :model-value="task.progress"
            :max="100"
            color="warning"
            status
          />
          <UBadge
            v-else
            :color="
              backend.executionStatuses.find((s) => s.value === task.status)
                .color
            "
          >
            <UIcon
              :name="
                backend.executionStatuses.find((s) => s.value === task.status)
                  .icon
              "
              class="text-lg"
            />
            <span>{{ task.status }}</span>
          </UBadge>
          <template v-if="userStore.is_auditor">
            <UTooltip v-if="task.progress !== 100" text="Cancel">
              <UButton
                icon="i-lucide-x"
                color="error"
                variant="solid"
                @click="cancelOpen = true"
              />
            </UTooltip>
            <UTooltip v-else text="Repeat">
              <UButton
                icon="i-lucide-play"
                color="success"
                variant="solid"
                @click="repeatScan"
              />
            </UTooltip>
          </template>
          <!-- todo: add entry for taking a note -->
          <UDropdownMenu
            v-if="userStore.is_auditor"
            :items="[
              task.progress === 100
                ? {
                    label: 'Generate a report',
                    icon: 'i-lucide-file-text',
                    color: 'info',
                    onSelect: () => (reportOpen = true),
                  }
                : {},
            ]"
          >
            <UButton icon="i-lucide-plus" variant="solid" color="info" />
          </UDropdownMenu>
          <UDropdownMenu
            v-if="task.notes.length + task.reports.length > 0"
            :items="
              [
                task.reports.length > 0
                  ? {
                      label: `${task.reports.length} Reports`,
                      icon: 'i-lucide-file-text',
                      color: 'neutral',
                      to: `/projects/${$route.params.project_id}/reports?target=${task.target.id}&task=${task.id}`,
                    }
                  : {},
                task.notes.length > 0
                  ? {
                      label: `${task.notes.length} Notes`,
                      icon: 'i-lucide-notebook',
                      color: 'neutral',
                      to: `/projects/${$route.params.project_id}/notes?target=${task.target.id}&task=${task.id}`,
                    }
                  : {},
              ].filter((i) => Object.keys(i).length > 0)
            "
          >
            <UButton icon="i-lucide-link" variant="solid" color="neutral" />
          </UDropdownMenu>
          <!-- TODO: Links to OSINT, credentials, assets and vulnerabilities, at task and execution level -->
        </div>
      </div>
      <USeparator />
      <div class="flex flex-wrap justify-around items-center gap-4">
        <div>
          <p class="text-xs text-muted uppercase tracking-wider mb-1.5">
            Target
          </p>
          <NuxtLink
            :to="`/projects/${route.params.project_id}/targets/${task.target.id}`"
            class="flex items-center gap-1.5 font-medium hover:text-primary transition-colors"
          >
            <UIcon
              :name="
                backend.targetTypes.find((t) => t.value === task?.target.type)
                  .icon
              "
            />
            <span
              >{{ task.target.target
              }}{{
                task.target_port
                  ? `:${task.target_port.port}${task.target_port.path ? (task.target_port.path[0] === "/" ? task.target_port.path : `/${task.target_port.path}`) : ""}`
                  : ""
              }}</span
            >
          </NuxtLink>
        </div>
        <div>
          <p class="text-xs text-muted uppercase tracking-wider mb-1.5">
            Intensity
          </p>
          <UBadge
            :color="
              backend.intensities.find((i) => i.label === task?.intensity)
                ?.color || 'neutral'
            "
            variant="subtle"
          >
            {{ task.intensity }}
          </UBadge>
        </div>
        <div v-if="task.executor">
          <p class="text-xs text-muted uppercase tracking-wider mb-1.5">
            Executor
          </p>
          <p class="font-medium">
            @{{ task.executor?.username || task.executor?.email }}
          </p>
        </div>
        <div>
          <p class="text-xs text-muted uppercase tracking-wider mb-1.5">
            {{ !task.start && task.scheduled_at ? "Scheduled" : "Started" }}
          </p>
          <p class="font-medium">
            {{
              task.start
                ? new Date(task.start).toLocaleString()
                : task.scheduled_at
                  ? new Date(task.scheduled_at).toLocaleString()
                  : "—"
            }}
          </p>
        </div>
        <div v-if="task.start">
          <p class="text-xs text-muted uppercase tracking-wider mb-1.5">
            Duration
          </p>
          <p class="font-medium">
            {{
              task.start && task.end
                ? utils.duration(task.start, task.end)
                : task.status === "Running" && task.start
                  ? utils.duration(task.start, new Date().toISOString())
                  : "—"
            }}
          </p>
        </div>
      </div>
    </UPageCard>

    <CrudPage ref="executionsPage" :config="config">
      <template #actions="{ item }">
        <UTooltip v-if="item.has_report" text="Download report">
          <UButton
            icon="i-lucide-download"
            variant="ghost"
            size="xl"
            @click="executionsApi.download(`${item.id}/report/`)"
          />
        </UTooltip>
      </template>
    </CrudPage>

    <CrudDeleteModal
      :open="cancelOpen"
      :item="task"
      :config="{
        entityName: 'Scan',
        deleteMessage: () => [
          {
            component: h(
              'p',
              { class: 'text-gray-900 dark:text-white font-medium' },
              'Are you sure you want to cancel this scan?',
            ),
          },
          {
            component: resolveComponent('UAlert'),
            props: {
              color: 'neutral',
              variant: 'subtle',
              description: backend.getTaskName(task, true),
              ui: { root: 'text-center font-bold' },
              class: 'mt-4',
            },
          },
        ],
        deleteVerb: 'Cancel',
        deleteIcon: 'i-lucide-x',
      }"
      :api="tasksApi"
      @open="(open) => (cancelOpen = open)"
      @deleted="fetchTask()"
    />

    <ReportsButton
      v-if="task"
      v-model:open="reportOpen"
      :target-id="task.target.id"
      :task-id="task.id"
      only-modal
    />

    <USlideover v-model:open="outputOpen" inset portal>
      <template #header="{ close }">
        <div class="flex items-center gap-3">
          <div
            class="size-10 rounded-lg bg-muted flex items-center justify-center shrink-0"
          >
            <UAvatar
              v-if="selectedExecution.configuration?.tool.icon"
              :src="selectedExecution.configuration.tool.icon"
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
                @click="
                  executionsApi.download(`${selectedExecution.id}/report/`)
                "
              />
            </UTooltip>
            <UButton
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              @click="close"
            />
          </div>
        </div>
      </template>
      <template #body>
        <!-- TODO: Make the body bigger -->
        <!-- TODO: Format the plain_output text with a terminal style -->
        <Placeholder class="w-300" />
      </template>
    </USlideover>
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import { useUserStore } from "~/store/user";
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import type { Task, Execution } from "~/types/models";

definePageMeta({ layout: "project" });

const route = useRoute();
const tasksApi = useApi("/api/tasks/");
const executionsApi = useApi("/api/executions/");
const userStore = useUserStore();
const backend = useBackend();
const utils = useUtils();
const cancelOpen = ref(false);
const reportOpen = ref(false);
const task = ref<Task | null>(null);
const outputOpen = ref(false);
const selectedExecution = ref<Execution | null>(null);
const executionsPage = ref();
const refresh = ref<ReturnType<typeof setTimeout> | null>(null);
const toolOptions = ref<FilterOption[]>([]);

function repeatScan() {
  tasksApi
    .create(`${route.params.scan_id}/repeat/`, {}, {}, "Scan")
    .then((response: Task) =>
      navigateTo(`/projects/${route.params.project_id}/scans/${response.id}`),
    );
}

function fetchTask() {
  tasksApi.get(`${route.params.scan_id}/`).then((response: Task) => {
    task.value = response;
    if (response.status === "Running" || response.status === "Requested" || response.executions.length === 0) {
      if (refresh.value) clearTimeout(refresh.value);
      refresh.value = setTimeout(() => {
        fetchTask();
        executionsPage.value?.fetch();
      }, 10000);
    }
  });
}

onMounted(() => {
  fetchTask();
  backend.getToolOptions(toolOptions);
});

onUnmounted(() => {
  if (refresh.value) clearTimeout(refresh.value);
});

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
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      id: "tool",
      header: "Tool",
      icon: "i-lucide-square-terminal",
      cell: ({ row }) => {
        const execution = row.original as Execution;
        return h("div", { class: "flex items-center gap-2" }, [
          execution.configuration?.tool.icon
            ? h(resolveComponent("UAvatar"), {
                src: execution.configuration.tool.icon,
                size: "sm",
              })
            : h(resolveComponent("UIcon"), {
                name: "i-lucide-square-terminal",
                class: "text-2xl text-muted-foreground text-primary shrink-0",
              }),
          h(
            "span",
            { class: "font-medium" },
            execution.configuration?.tool.name,
          ),
        ]);
      },
    },
    {
      accessorKey: "configuration",
      header: "Configuration",
      icon: "i-lucide-file-code-corner",
      cell: ({ row }) => {
        const execution = row.original as Execution;
        return h(
          "span",
          { class: "font-medium" },
          execution.configuration.name,
        );
      },
    },
    {
      id: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const execution = row.original as Execution;
        const status = backend.executionStatuses.find(
          (s) => s.value === execution.status,
        );
        const isRunning = execution.status === "Running";
        return h(
          resolveComponent("UTooltip"),
          { text: execution.status },
          {
            default: () =>
              h(resolveComponent("UButton"), {
                icon: isRunning ? "i-lucide-loader" : status?.icon,
                loading: isRunning,
                color: status?.color,
                class: "text-lg",
                variant: "ghost",
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
        return h(
          "span",
          { class: "font-medium" },
          start ? new Date(start).toLocaleString() : "—",
        );
      },
    },
    {
      id: "duration",
      header: "Duration",
      icon: "i-lucide-timer",
      cell: ({ row }) => {
        const execution = row.original as Execution;
        return h(
          "span",
          { class: "font-medium tabular-nums" },
          execution.start && execution.end
            ? utils.duration(execution.start, execution.end)
            : execution.start
              ? utils.duration(execution.start, new Date().toISOString())
              : "—",
        );
      },
    },
    {
      id: "skipped",
      header: "Skipped",
      icon: "i-lucide-skip-forward",
      cell: ({ row }) => {
        const execution = row.original as Execution;
        return h(
          "span",
          { class: "font-medium" },
          execution.skipped_reason || "—",
        );
      },
    },
  ] as CrudTableColumn<Execution>[],
  tableColumnsVisibility: {
    skipped: false,
    id: false,
  },
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
      options: backend.stages,
    },
    {
      key: "status",
      label: "Status",
      icon: "i-lucide-activity",
      type: "select" as const,
      options: backend.executionStatuses,
      labelKey: "value",
    },
  ],
  defaultFilters: { task: route.params.scan_id as string },
  defaultOrdering: "start,id",
  emptyMessage:
    "No executions yet. The task may still be waiting to be processed",
  tableCopyId: false,
  canRead: true,
  canCreate: false,
  canEdit: false,
  canDelete: false,
});
</script>

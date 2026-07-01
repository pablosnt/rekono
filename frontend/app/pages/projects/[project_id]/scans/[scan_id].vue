<template>
  <div class="w-full">
    <UPageCard v-if="task" variant="outline" class="mb-10">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div
            class="size-10 rounded-lg bg-muted flex items-center justify-center shrink-0"
          >
            <UAvatar
              v-if="task.configuration?.tool.icon"
              :src="task.configuration.tool.icon"
              :alt="task.configuration.tool.name"
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
              executionStatuses.find((s) => s.value === task.status).color
            "
            size="xl"
          >
            <UIcon
              :name="
                executionStatuses.find((s) => s.value === task.status).icon
              "
              class="text-lg"
              :aria-label="task.status"
            />
            <span>{{ task.status }}</span>
          </UBadge>
          <template v-if="userStore.is_auditor">
            <UTooltip
              v-if="task.status === 'Running' || task.status === 'Requested'"
              text="Cancel"
            >
              <UButton
                icon="i-lucide-x"
                color="error"
                variant="subtle"
                aria-label="Cancel scan"
                @click="cancelOpen = true"
              />
            </UTooltip>
            <UTooltip v-else text="Repeat">
              <UButton
                icon="i-lucide-play"
                color="success"
                variant="subtle"
                aria-label="Repeat scan"
                @click="repeatScan"
              />
            </UTooltip>
          </template>
          <NotesDropdown
            :related-entity="task"
            entity-name="Task"
            :project="parseInt($route.params.project_id)"
            variant="subtle"
          />
          <ReportsDropdown
            v-if="task.progress === 100"
            :related-entity="task"
            entity-name="Task"
            :project="parseInt($route.params.project_id)"
            :can-create="task.progress === 100"
            color="neutral"
            variant="subtle"
          />
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
                targetTypes.find((t) => t.value === task?.target.type).icon
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
              intensities.find((i) => i.label === task?.intensity)?.color ||
              'neutral'
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
          <p class="font-medium">@{{ task.executor?.username }}</p>
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
                ? duration(task.start, task.end)
                : task.status === "Running" && task.start
                  ? duration(task.start, new Date().toISOString())
                  : "—"
            }}
          </p>
        </div>
      </div>
    </UPageCard>

    <FindingsCounterAll
      v-if="task"
      ref="findings"
      :task-id="task.id"
      :project-id="task.target.project"
      class="mb-8"
    />

    <Executions
      v-if="task"
      ref="executions"
      :task="route.params.scan_id"
      @finished="findings.fetch()"
    />

    <LazyCrudDeleteModal
      :open="cancelOpen"
      :item="task"
      :config="{
        entityName: 'Scan',
        deleteMessage: () =>
          buildDeleteMessage('scan', undefined, undefined, undefined, 'cancel'),
        deleteVerb: 'Cancel',
        deleteIcon: 'i-lucide-x',
      }"
      :api="tasksApi"
      @open="(open) => (cancelOpen = open)"
      @deleted="
        fetchTask();
        executions.page.fetch();
      "
    />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import type { FilterOption } from "~/types/crud";
import type { Task } from "~/types/models";
import { intensities, targetTypes, executionStatuses } from "~/constants";

const route = useRoute();
const tasksApi = useApi("/api/tasks/");
const userStore = useUserStore();
const options = useOptions();
const cancelOpen = ref(false);
const task = ref<Task | null>();
const executions = ref();
const findings = ref();
const refresh = ref<ReturnType<typeof setTimeout> | null>(null);
const toolOptions = ref<FilterOption[]>([]);

function repeatScan() {
  tasksApi
    .create(`${route.params.scan_id}/repeat/`, {}, {}, "Scan")
    .then((response: Task) => {
      return navigateTo(
        `/projects/${route.params.project_id}/scans/${response.id}`,
      );
    });
}

function processTask(data?: Task) {
  if (!data) return;
  task.value = data;
  if (
    data.status !== "Cancelled" &&
    (!data.scheduled_at || new Date(data.scheduled_at) <= new Date()) &&
    (data.status === "Running" ||
      data.status === "Requested" ||
      data.executions.length === 0)
  ) {
    if (refresh.value) clearTimeout(refresh.value);
    refresh.value = setTimeout(() => {
      fetchTask();
      executions.value?.page?.fetch();
    }, 5000);
  } else if (refresh.value) {
    clearTimeout(refresh.value);
    refresh.value = null;
  }
}

function fetchTask(initial: boolean = false) {
  (initial ? tasksApi.getOrError : tasksApi.get)(
    `${route.params.scan_id}/`,
  ).then((response: Task) => processTask(response));
}

onMounted(() => {
  fetchTask(true);
  options.tools(toolOptions);
});

onUnmounted(() => {
  if (refresh.value) clearTimeout(refresh.value);
});
</script>

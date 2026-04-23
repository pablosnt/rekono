<template>
  <CrudPage
    :config="{
      entityNamePlural: 'RQ queues',
      entityName: 'RQ queue',
      canRead: userStore.is_admin,
      canEdit: false,
      canDelete: false,
      canCreate: false,
    }"
  >
    <template #content>
      <UProgress :class="[loading ? 'visible' : 'invisible', 'mb-1']" />
      <UPageGrid
        v-if="queueStats && Object.keys(queueStats).length > 0"
        class="grid-cols-1 md:grid-cols-2 xl:grid-cols-4"
      >
        <UPageCard
          v-for="queue in queueStats"
          :key="queue.name"
          :title="firstUpper(queue.name)"
          :description="`${queue.workers} workers`"
          :icon="queue.icon"
          variant="subtle"
          spotlight
        >
          <template #leading>
            <UIcon :name="queue.icon" :class="['text-xl', queue.icon_class]" />
          </template>
          <div class="absolute top-4 right-4">
            <UButton
              v-if="queue.started_jobs > 0"
              :label="queue.started_jobs"
              variant="ghost"
              color="warning"
              size="xl"
              loading
            />
          </div>
          <div class="flex flex-wrap justify-between">
            <UButton
              v-if="queue.scheduled_jobs > 0"
              icon="i-lucide-calendar-check"
              :label="`Scheduled: ${queue.scheduled_jobs} jobs`"
              variant="ghost"
              color="neutral"
              size="sm"
              class="flex-1 min-w-fit"
            />
            <UButton
              v-if="queue.deferred_jobs + queue.jobs > 0"
              icon="i-lucide-pause"
              :label="`Waiting: ${queue.deferred_jobs + queue.jobs} jobs`"
              variant="ghost"
              color="neutral"
              size="sm"
              class="flex-1 min-w-fit"
            />
            <UButton
              v-if="queue.finished_jobs > 0"
              icon="i-lucide-check"
              :label="`Succeed: ${queue.finished_jobs} jobs`"
              variant="ghost"
              color="success"
              size="sm"
              class="flex-1 min-w-fit"
            />
            <UButton
              v-if="queue.failed_jobs > 0"
              icon="i-lucide-x"
              :label="`Failed: ${queue.failed_jobs} jobs`"
              variant="ghost"
              color="error"
              size="sm"
              class="flex-1 min-w-fit"
            />
          </div>
          <div v-if="queue.name === 'monitor' && monitor">
            <UFormField label="Monitor regularity in hours">
              <template v-if="monitor.last_monitor" #hint>
                <UTooltip
                  :text="`Last monitor was ${useTimeAgo(new Date(monitor.last_monitor)).value}`"
                  :content="{
                    side: 'top',
                    sideOffset: 8,
                    collisionPadding: 8,
                  }"
                >
                  <UButton
                    icon="i-lucide-clock"
                    size="sm"
                    variant="ghost"
                    color="neutral"
                  />
                </UTooltip>
              </template>
              <UInputNumber
                v-model="monitor.hour_span"
                class="w-full"
                :min="24"
                :max="168"
                required
                size="lg"
                @change="() => updateMonitor()"
              />
            </UFormField>
          </div>
        </UPageCard>
      </UPageGrid>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import { useTimeAgo } from "@vueuse/core";

const api = useApi("/api/");
const userStore = useUserStore();
const loading = ref(false);
const queueStats = ref<Array<Record<string, string | number>>>([]);
const monitor = ref();
const icons = {
  tasks: {
    icon: "i-lucide-scan-search",
    icon_class: "text-blue-500",
  },
  executions: {
    icon: "i-lucide-play-circle",
    icon_class: "text-green-500",
  },
  findings: {
    icon: "i-lucide-bug",
    icon_class: "text-red-500",
  },
  monitor: {
    icon: "i-lucide-radar",
    icon_class: "text-purple-500",
  },
};

function fetch() {
  loading.value = true;
  api
    .get("stats/rq/")
    .then((response) => {
      queueStats.value = Object.keys(response).map((queue) => {
        return {
          name: queue,
          icon: icons[queue]["icon"],
          icon_class: icons[queue]["icon_class"],
          jobs: response[queue].jobs,
          workers: response[queue].workers,
          finished_jobs: response[queue].finished_jobs,
          started_jobs: response[queue].started_jobs,
          deferred_jobs: response[queue].deferred_jobs,
          failed_jobs: response[queue].failed_jobs,
          scheduled_jobs: response[queue].scheduled_jobs,
        };
      });
    })
    .finally(() => {
      loading.value = false;
    });
}

function fetchMonitor() {
  api.get("monitor/1/").then((response) => {
    monitor.value = response;
  });
}

function updateMonitor() {
  api
    .update("monitor/1/", { hour_span: monitor.value.hour_span }, {})
    .then((response) => (monitor.value = response));
}

onMounted(() => {
  fetch();
  fetchMonitor();
});
</script>

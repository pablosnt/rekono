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
      <UProgress v-if="loading" />

      <UPageGrid
        v-if="queueStats && Object.keys(queueStats).length > 0"
        class="grid-cols-1 md:grid-cols-2 xl:grid-cols-4"
      >
        <UPageCard
          v-for="queue in queueStats"
          :key="queue.name"
          :title="utils.firstUpper(queue.name)"
          :description="`${queue.workers} workers`"
          :icon="queue.icon"
          variant="subtle"
          spotlight
        >
          <template #leading>
            <div class="flex items-center justify-end">
              <div class="w-25">
                <UIcon
                  :name="queue.icon"
                  :class="`${queue.icon_class} text-xl`"
                />
              </div>
              <div class="flex w-30 justify-end items-center gap-3">
                <UButton
                  v-if="queue.started_jobs > 0"
                  :label="queue.started_jobs"
                  variant="ghost"
                  color="warning"
                  loading
                />
              </div>
            </div>
          </template>
          <template #default>
            <div class="flex">
              <UButton
                icon="i-lucide-calendar-check"
                :label="`Scheduled: ${queue.scheduled_jobs}`"
                variant="ghost"
                color="neutral"
                size="sm"
              />
              <UButton
                icon="i-lucide-pause"
                :label="`Waiting: ${queue.deferred_jobs}`"
                variant="ghost"
                color="neutral"
                size="sm"
              />
            </div>
            <div class="text-center">
              <UButton
                v-if="queue.failed_jobs > 0"
                icon="i-lucide-x"
                :label="`${queue.failed_jobs}/${queue.jobs} jobs failed`"
                variant="ghost"
                color="error"
                size="sm"
              />
              <UButton
                v-else-if="queue.finished_jobs > 0"
                icon="i-lucide-check"
                :label="`${queue.finished_jobs} successful jobs`"
                variant="ghost"
                color="success"
                size="sm"
              />
            </div>
          </template>
        </UPageCard>
      </UPageGrid>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi("/api/stats/rq/");
const userStore = useUserStore();
const utils = useUtils();
const loading = ref(false);
const queueStats = ref<Array<Record<string, string | number>>>([]);
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
    .get("")
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

onMounted(() => {
  fetch();
});
</script>

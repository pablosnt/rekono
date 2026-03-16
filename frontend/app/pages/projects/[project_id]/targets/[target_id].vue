<template>
  <div>
    <CrudHeader
      :api="api"
      :config="{
        entityNamePlural: target?.target,
        headerIcon: target
          ? backend.targetTypes.find((t) => t.value === target.type)?.icon
          : undefined,
      }"
      title-size-class="text-3xl"
    >
      <template #header-actions>
        <TasksButton
          v-if="userStore.is_auditor"
          :project="{ id: parseInt($route.params.project_id) }"
          :target="{ id: parseInt($route.params.target_id) }"
        />
        <!-- todo: add entry for taking a note -->
        <UDropdownMenu
          v-if="userStore.is_auditor"
          :items="[
            {
              label: 'Generate a report',
              icon: 'i-lucide-file-text',
              color: 'info',
              onSelect: () => {
                showReportModal = true;
              },
            },
          ]"
        >
          <UButton icon="i-lucide-plus" variant="solid" color="info" />
        </UDropdownMenu>
        <UDropdownMenu
          v-if="
            target &&
            target?.tasks.length +
              target?.notes.length +
              target?.reports.length >
              0
          "
          :items="
            [
              target?.tasks.length > 0
                ? {
                    label: `${target?.tasks.length} Scans`,
                    icon: 'i-lucide-play',
                    color: 'neutral',
                    to: `/projects/${$route.params.project_id}/scans?target=${route.params.target_id}`,
                  }
                : {},
              target?.reports.length > 0
                ? {
                    label: `${target?.reports.length} Reports`,
                    icon: 'i-lucide-file-text',
                    color: 'neutral',
                    to: `/projects/${$route.params.project_id}/reports?target=${route.params.target_id}`,
                  }
                : {},
              target?.notes.length > 0
                ? {
                    label: `${target?.notes.length} Notes`,
                    icon: 'i-lucide-notebook',
                    color: 'neutral',
                    to: `/projects/${$route.params.project_id}/notes?target=${route.params.target_id}`,
                  }
                : {},
            ].filter((i) => Object.keys(i).length > 0)
          "
        >
          <UButton icon="i-lucide-link" variant="solid" color="neutral" />
        </UDropdownMenu>
        <ReportsButton
          v-model:open="showReportModal"
          :target-id="parseInt($route.params.target_id)"
          only-modal
        />
      </template>
    </CrudHeader>
    <div class="space-y-14">
      <TargetPorts />
      <HttpHeaders
        :target="parseInt($route.params.target_id)"
        :can-read="true"
        :can-edit="userStore.is_auditor"
        :can-delete="userStore.is_auditor"
        :can-create="userStore.is_auditor"
        :show-access-denied-error="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

definePageMeta({ layout: "project" });
const userStore = useUserStore();
const route = useRoute();
const backend = useBackend();
const api = useApi("/api/");
const target = ref();
const showReportModal = ref(false);

onMounted(() => {
  api.get(`targets/${route.params.target_id}/`).then((response) => {
    target.value = response;
  });
});
</script>

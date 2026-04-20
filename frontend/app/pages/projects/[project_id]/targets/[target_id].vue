<template>
  <div>
    <CrudHeader
      :api="api"
      :config="{
        entityNamePlural: target?.target,
        headerIcon: target
          ? targetTypes.find((t) => t.value === target.type)?.icon
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
        <UDropdownMenu
          v-if="userStore.is_auditor"
          :items="[
            {
              label: 'Generate a report',
              icon: 'i-lucide-file-text',
              color: 'neutral',
              onSelect: () => {
                showReportModal = true;
              },
            },
            {
              label: 'Take note',
              icon: 'i-lucide-notebook',
              color: 'neutral',
              onSelect: () => notesButton.createNote(),
            },
          ]"
        >
          <UButton icon="i-lucide-plus" variant="subtle" color="neutral" />
        </UDropdownMenu>
        <UDropdownMenu
          v-if="
            target &&
            target?.tasks.length +
              target?.notes.length +
              target?.reports.length >
              0
          "
          :items="[
            ...(target?.tasks.length > 0
              ? [
                  {
                    label: `${target?.tasks.length} Scans`,
                    icon: 'i-lucide-play',
                    color: 'neutral',
                    to: `/projects/${$route.params.project_id}/scans?target=${route.params.target_id}`,
                  },
                ]
              : []),
            ...(target?.reports.length > 0
              ? [
                  {
                    label: `${target?.reports.length} Reports`,
                    icon: 'i-lucide-file-text',
                    color: 'neutral',
                    to: `/projects/${$route.params.project_id}/reports?target=${route.params.target_id}`,
                  },
                ]
              : []),
            ...(target?.notes.length > 0
              ? [
                  {
                    label: `${target?.notes.length} Notes`,
                    icon: 'i-lucide-notebook',
                    color: 'neutral',
                    to: `/projects/${$route.params.project_id}/notes?target=${route.params.target_id}`,
                  },
                ]
              : []),
          ]"
        >
          <UButton icon="i-lucide-link" variant="subtle" color="neutral" />
        </UDropdownMenu>
        <ReportsButton
          v-model:open="showReportModal"
          :target-id="parseInt($route.params.target_id)"
          only-modal
        />
        <NotesButton
          ref="notesButton"
          :target="parseInt($route.params.target_id)"
        />
        <UDropdownMenu
          v-if="userStore.is_auditor"
          :items="[
            {
              label: 'Copy link',
              icon: 'i-lucide-copy',
              onSelect: copyLink,
            },
            {
              label: 'Delete',
              icon: 'i-lucide-trash',
              color: 'error',
              onSelect: () => (deleteOpen = true),
            },
          ]"
        >
          <UButton
            icon="i-lucide-more-horizontal"
            variant="subtle"
            color="neutral"
          />
        </UDropdownMenu>
        <CrudDeleteModal
          :open="deleteOpen"
          :item="target"
          :config="deleteConfig"
          :api="api"
          @open="(open) => (deleteOpen = open)"
          @deleted="navigateTo(`/projects/${$route.params.project_id}/targets`)"
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
import { targetTypes } from "~/constants";

definePageMeta({ layout: "project" });
const userStore = useUserStore();
const route = useRoute();
const api = useApi("/api/targets/");
const target = ref();
const notesButton = ref();
const showReportModal = ref(false);
const deleteOpen = ref(false);
const deleteConfig = {
  entityName: "Target",
  deleteMessage: () => buildDeleteMessage("target", target.value?.target),
};

onMounted(() => {
  api.get(`${route.params.target_id}/`).then((response) => {
    target.value = response;
  });
});
</script>

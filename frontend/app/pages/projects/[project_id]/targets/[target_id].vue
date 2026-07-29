<template>
  <div>
    <CrudHeader
      :api="api"
      :config="{
        entityNamePlural: target?.target,
        headerIcon: target
          ? targetTypes.find((t) => t.value === target.type)?.icon
          : undefined,
        headerHideTitle: !target,
      }"
      title-size-class="text-3xl"
      disable-url-sync
    >
      <template v-if="!target" #header-leading>
        <div class="sr-only" role="status">Loading target</div>
        <USkeleton aria-hidden="true" class="size-[30px]" />
        <USkeleton aria-hidden="true" class="h-9 w-64 max-w-full" />
      </template>
      <template #header-actions>
        <TasksButton
          v-if="userStore.is_auditor"
          :project="{ id: projectId }"
          :target="{ id: targetId }"
        />
        <UDropdownMenu
          :items="[
            ...(target?.tasks.length > 0 && projectHasActiveFindings
              ? [
                  {
                    label: 'Generate a report',
                    icon: 'i-lucide-file-text',
                    onSelect: () => {
                      showReportModal = true;
                    },
                  },
                ]
              : []),
            {
              label: 'Take note',
              icon: 'i-lucide-notebook',
              onSelect: () => notesButton.createNote(),
            },
          ]"
        >
          <UButton
            icon="i-lucide-plus"
            variant="subtle"
            color="neutral"
            aria-label="Target actions"
          />
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
                    label: pluralize(target?.tasks.length, 'Scan'),
                    icon: 'i-lucide-play',
                    to: `/projects/${$route.params.project_id}/scans?target=${route.params.target_id}`,
                  },
                ]
              : []),
            ...(target?.reports.length > 0
              ? [
                  {
                    label: pluralize(target?.reports.length, 'Report'),
                    icon: 'i-lucide-file-text',
                    to: `/projects/${$route.params.project_id}/reports?target=${route.params.target_id}`,
                  },
                ]
              : []),
            ...(target?.notes.length > 0
              ? [
                  {
                    label: pluralize(target?.notes.length, 'Note'),
                    icon: 'i-lucide-notebook',
                    to: `/projects/${$route.params.project_id}/notes?target=${route.params.target_id}`,
                  },
                ]
              : []),
            ...(showDefectDojo && target?.defectdojo_sync?.engagement_id
              ? [
                  {
                    label: 'DefectDojo',
                    avatar: {
                      src: integrations.defectdojo.integration?.icon,
                    },
                    to: `${integrations.defectdojo.settings.server}/engagement/${target.defectdojo_sync?.engagement_id}`,
                    target: '_blank',
                  },
                ]
              : []),
          ]"
        >
          <UButton
            icon="i-lucide-link"
            variant="subtle"
            color="neutral"
            aria-label="View target resources"
          />
        </UDropdownMenu>
        <ReportsButton
          v-model:open="showReportModal"
          :target-id="targetId"
          only-modal
        />
        <NotesButton ref="notesButton" :target="targetId" />
        <UDropdownMenu
          v-if="userStore.is_auditor"
          :items="[
            {
              label: 'Copy link',
              icon: 'i-lucide-copy',
              onSelect: copyLink,
            },
            {
              label: 'Copy target',
              icon: 'i-lucide-copy',
              onSelect: () => copyText(target?.target),
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
            aria-label="Target options"
          />
        </UDropdownMenu>
        <LazyCrudDeleteModal
          :open="deleteOpen"
          :item="target"
          :config="deleteConfig"
          :api="api"
          @open="(open) => (deleteOpen = open)"
          @deleted="navigateTo(`/projects/${$route.params.project_id}/targets`)"
        />
      </template>
    </CrudHeader>
    <div v-if="target" class="space-y-14">
      <FindingsCounterAll
        :target-id="targetId"
        :project-id="projectId"
        only-active
        show-empty
      />
      <TargetPorts />
      <HttpHeaders
        :target="targetId"
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
import { useIntegrationsStore } from "~/store/integrations";

const userStore = useUserStore();
const integrations = useIntegrationsStore();
const { showDefectDojo } = useCurrentProject();
const { projectHasActiveFindings } = usePanel();
const route = useRoute();
const targetId = route.params.target_id
  ? parseInt(route.params.target_id)
  : undefined;
const projectId = route.params.project_id
  ? parseInt(route.params.project_id)
  : undefined;
const api = useApi("/api/targets/");
const target = ref();
const notesButton = ref();
const showReportModal = ref(false);
const deleteOpen = ref(false);
const deleteConfig = {
  entityName: "Target",
  deleteMessage: () =>
    buildDeleteMessage(
      "target",
      target.value?.target,
      "Permanent deletion",
      "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
    ),
};

onMounted(() => {
  api
    .getOrError(`${route.params.target_id}/`)
    .then((response) => (target.value = response));
  integrations.fetchDefectDojo();
});
</script>

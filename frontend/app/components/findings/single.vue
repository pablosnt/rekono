<template>
  <div class="space-y-5">
    <UPageCard variant="subtle" :ui="{ header: 'w-full' }">
      <template #header>
        <div class="mb-4">
          <div class="flex flex-wrap justify-between w-full">
            <div class="flex items-center gap-2">
              <UIcon
                v-if="icon"
                :name="icon"
                :class="`text-${iconColor || 'neutral'} text-xl`"
              />
              <span class="text-base font-semibold text-xl text-highlighted">{{
                title
              }}</span>
              <UButton
                v-if="!disableTitleCopy"
                icon="i-lucide-copy"
                color="neutral"
                variant="ghost"
                size="xs"
                @click="copyText(title)"
              />
            </div>
            <div class="flex items-center gap-2">
              <FindingsUtilsStatus
                :finding="finding"
                :is-triageable="isTriageable"
                :fix-verb="fixVerb"
              />
              <!-- todo: DefectDojo link -->
              <!-- TODO: Add a badge with the number of existing notes to the Notes button everywhere. Only if greater than 0 -->
              <FindingsUtilsNotes
                :finding="finding"
                :entity-name="entityName"
              />
              <UDropdownMenu
                v-if="
                  (hacktricks &&
                    hacktricks.enabled &&
                    finding.hacktricks_link) ||
                  finding.reference ||
                  finding.defectdojo_id
                "
                :items="
                  [
                    finding.hacktricks_link && hacktricks.enabled
                      ? {
                          label: 'HackTricks',
                          avatar: { src: hacktricks.icon },
                          to: finding.hacktricks_link,
                          target: '_blank',
                        }
                      : {},
                    finding.reference
                      ? {
                          label: 'Reference',
                          icon: 'i-lucide-external-link',
                          to: finding.reference,
                          target: '_blank',
                        }
                      : {},
                  ].filter((i) => Object.keys(i).length > 0)
                "
                :content="{ align: 'end' }"
              >
                <UButton icon="i-lucide-link" color="neutral" variant="ghost" />
              </UDropdownMenu>
              <UDropdownMenu
                v-if="userStore.is_auditor && dropdownActions.length > 0"
                :items="dropdownActions"
                :content="{ align: 'end' }"
              >
                <UButton
                  icon="i-lucide-ellipsis"
                  color="neutral"
                  variant="ghost"
                />
              </UDropdownMenu>
            </div>
          </div>
          <slot name="description" />
        </div>
      </template>
      <div class="flex items-center justify-around flex-wrap">
        <!-- TODO: This is not responsive! -->
        <slot name="metadata" />
      </div>
      <slot name="post-metadata" />
    </UPageCard>
    <slot name="custom" />
    <UPageCard
      v-if="!finding.created_from_user_input"
      class="mt-5"
      title="Exposure Window"
      description="Executions detecting the finding"
      variant="outline"
    >
      <FindingsMetricsExposure class="mb-3" :finding="finding" />
      <Executions
        ref="executions"
        :finding="finding"
        :finding-type="entityName"
        @fetched="(items) => processExecutions(items)"
      />
    </UPageCard>
    <FindingsModalTriage
      v-if="isTriageable && userStore.is_auditor"
      :open="triageModalOpen"
      :api="api"
      :finding="finding"
      :entity-name="entityName"
      @open="(open) => (triageModalOpen = open)"
      @triaged="$emit('update')"
    />
    <FindingsModalFix
      v-if="userStore.is_auditor"
      :api="api"
      :fix-verb="fixVerb"
      :unfix-verb="unfixVerb"
      :finding="finding"
      :is-asset="isAsset"
      :entity-name="entityName"
      :open="fixModalOpen"
      @open="(open) => (fixModalOpen = open)"
      @switched="$emit('update')"
    />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import type { DropdownAction } from "~/types/crud";
import type { Execution, Finding } from "~/types/models";

const props = defineProps<{
  api: typeof useApi;
  icon?: string;
  iconColor?: string;
  title: string;
  finding: Finding;
  entityName: string;
  isTriageable?: boolean;
  isAsset?: boolean;
  fixVerb: string;
  disableTitleCopy?: boolean;
  customDropdownActions?: DropdownAction[];
}>();
defineEmits<{ update: [] }>();

const userStore = useUserStore();
const unfixVerb = computed(() =>
  props.fixVerb === "Fix" ? "Reopen" : "Restore",
);
const triageModalOpen = ref(false);
const fixModalOpen = ref(false);
const executions = ref();
const refresh = ref();
const hacktricks = ref();
const dropdownActions = computed(() => [
  ...getFindingDropdownActions(
    props.finding,
    props.fixVerb,
    unfixVerb.value,
    props.isTriageable,
    () => (fixModalOpen.value = true),
    () => (fixModalOpen.value = true),
    () => (triageModalOpen.value = true),
  ),
  ...(props.customDropdownActions || []),
]);

function processExecutions(items: Execution[]) {
  if (items.filter((e) => ["Running", "Requested"].includes(e.status))) {
    refresh.value = setTimeout(executions.value?.page?.fetch, 10000);
  }
}

onMounted(() => {
  useApi("/api/integrations/")
    .get("3/")
    .then((response) => (hacktricks.value = response));
});

onUnmounted(() => {
  if (refresh.value) clearTimeout(refresh.value);
});
</script>

<template>
  <div class="space-y-5">
    {{}}
    <UProgress :class="[loading ? 'visible' : 'invisible', 'mb-1']" />
    <template v-if="finding">
      <UPageCard
        variant="subtle"
        :ui="{ header: 'w-full', container: 'overflow-hidden' }"
      >
        <template #header>
          <div class="mb-4">
            <div
              class="flex flex-col gap-3 sm:flex-row sm:justify-between w-full"
            >
              <div class="flex items-center gap-2">
                <slot name="icon">
                  <UIcon
                    v-if="icon"
                    :name="icon"
                    :class="`text-${iconColor || 'neutral'} text-xl`"
                  />
                </slot>
                <h1
                  class="font-bold text-default truncate max-w-[300px] sm:max-w-none text-2xl"
                >
                  {{ title }}
                </h1>
                <UButton
                  v-if="!disableTitleCopy"
                  icon="i-lucide-copy"
                  color="neutral"
                  variant="ghost"
                  size="xs"
                  aria-label="Copy title"
                  @click="copyText(title)"
                />
              </div>
              <div class="flex items-center gap-2">
                <FindingsStatus
                  :finding="finding"
                  :is-triageable="isTriageable"
                  :fix-verb="fixVerb"
                />
                <NotesDropdown
                  :related-entity="finding"
                  :entity-name="entityName"
                  :project="finding.project"
                />
                <UDropdownMenu
                  v-if="
                    (integrations.hacktricks?.enabled &&
                      finding.hacktricks_link) ||
                    finding.reference
                  "
                  :items="[
                    ...(finding.hacktricks_link &&
                    integrations.hacktricks?.enabled
                      ? [
                          {
                            label: 'HackTricks',
                            avatar: { src: integrations.hacktricks?.icon },
                            to: finding.hacktricks_link,
                            target: '_blank',
                          },
                        ]
                      : []),
                    ...(finding.reference
                      ? [
                          {
                            label: 'Reference',
                            icon: 'i-lucide-external-link',
                            to: finding.reference,
                            target: '_blank',
                          },
                        ]
                      : []),
                  ]"
                  :content="{ align: 'end' }"
                >
                  <UButton
                    icon="i-lucide-link"
                    color="neutral"
                    variant="ghost"
                    aria-label="View references and links"
                  />
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
                    aria-label="More finding actions"
                  />
                </UDropdownMenu>
              </div>
            </div>
            <slot name="description" />
          </div>
        </template>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4 mx-10">
          <slot name="metadata" />
        </div>
        <slot name="post-metadata" />
      </UPageCard>
      <slot name="custom" />
      <UPageCard
        v-if="!finding.created_from_user_input"
        class="mt-5"
        :description="
          (executionsTotal ?? finding.executions.length) > 0
            ? `First detected ${useTimeAgo(finding.executions.map((e) => new Date(e.start)).sort((a, b) => a - b)[0]).value} across ${executionsTotal ?? finding.executions.length} executions${finding.is_fixed ? `. ${firstUpper(fixVerb)}ed ${useTimeAgo(new Date(finding.fixed_date)).value}` : ''}`
            : 'Executions where the finding was detected'
        "
        variant="outline"
        :ui="{ header: 'w-full', container: 'min-w-0' }"
      >
        <template #title>
          <h2
            class="font-bold text-default truncate max-w-[300px] sm:max-w-none text-2xl"
          >
            Exposure Window
          </h2>
        </template>
        <FindingsExposure class="mb-3" :finding="finding" />
        <Executions
          ref="executions"
          :finding="finding"
          :finding-type="entityName"
          disable-url-sync
          @fetched="processExecutions"
        />
      </UPageCard>
      <LazyFindingsModalTriage
        v-if="isTriageable && userStore.is_auditor"
        :open="triageModalOpen"
        :api="api"
        :finding="finding"
        :entity-name="entityName"
        @open="(open) => (triageModalOpen = open)"
        @triaged="$emit('update')"
      />
      <LazyFindingsModalFix
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";
import type { DropdownAction } from "~/types/crud";
import type { Execution, Finding } from "~/types/models";
import { useTimeAgo } from "@vueuse/core";

const props = defineProps<{
  api: typeof useApi;
  icon?: string;
  iconColor?: string;
  title: string;
  finding?: Finding;
  entityName: string;
  loading?: boolean;
  isTriageable?: boolean;
  isAsset?: boolean;
  fixVerb: string;
  disableTitleCopy?: boolean;
  customDropdownActions?: DropdownAction[];
}>();
defineEmits<{ update: [] }>();

const userStore = useUserStore();
const integrations = useIntegrationsStore();
const unfixVerb = computed(() =>
  props.fixVerb === "Fix" ? "Reopen" : "Restore",
);
const triageModalOpen = ref(false);
const fixModalOpen = ref(false);
const executions = ref();
const executionsTotal = ref();
const refresh = ref();
const dropdownActions = computed(() =>
  props.finding
    ? [
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
      ]
    : [],
);

function processExecutions(items: Execution[], total: number) {
  executionsTotal.value = total;
  const running = items.filter((e) =>
    ["Running", "Requested"].includes(e.status),
  ).length;
  if (running > 0) {
    if (refresh.value) clearTimeout(refresh.value);
    refresh.value = setTimeout(() => executions.value?.page?.fetch(), 5000);
  } else if (refresh.value) {
    clearTimeout(refresh.value);
    refresh.value = null;
  }
}

onMounted(integrations.fetchHackTricks);

onUnmounted(() => {
  if (refresh.value) clearTimeout(refresh.value);
});
</script>

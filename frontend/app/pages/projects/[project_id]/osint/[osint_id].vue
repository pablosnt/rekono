<template>
  <FindingsSingle
    v-if="osint"
    :icon="typeConfig?.icon"
    :api="api"
    :title="osint.data"
    :finding="osint"
    entity-name="OSINT"
    is-triageable
    fix-verb="Discard"
    :custom-dropdown-actions="
      userStore.is_auditor && ['IP', 'Domain'].includes(osint.data_type)
        ? [getOSINTDropdownActions(osint, api)]
        : []
    "
    @update="fetch()"
  >
    <template #metadata>
      <div v-if="osint.data_type" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Data type:</span>
        <span class="text-base">{{ osint.data_type }}</span>
      </div>
      <div v-if="osint.source" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Source:</span>
        <span class="text-base">{{ osint.source }}</span>
      </div>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
import { osintDataTypes } from "~/constants";
import { useUserStore } from "~/store/user";

definePageMeta({ layout: "project" });

const api = useApi("/api/osint/");
const route = useRoute();
const userStore = useUserStore();
const osint = ref();
const typeConfig = ref();

function fetch() {
  api.get(`${route.params.osint_id}/`).then((response) => {
    osint.value = response;
    typeConfig.value = osintDataTypes.find(
      (t) => t.value === osint.value.data_type,
    );
  });
}

onMounted(fetch);
</script>

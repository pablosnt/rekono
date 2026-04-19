<template>
  <FindingsSingle
    v-if="osint"
    :api="api"
    :title="osint.data"
    :finding="osint"
    entity-name="OSINT"
    is-triageable
    fix-verb="Discard"
    @update="fetch()"
  >
    <template #metadata>
      <div v-if="osint.data_type" class="flex items-center gap-2">
        <span class="text-muted">Data type:</span>
        <UBadge :icon="typeConfig?.icon" variant="subtle" color="neutral">{{
          osint.data_type
        }}</UBadge>
      </div>
      <div v-if="osint.source" class="flex items-center gap-2">
        <span class="text-muted">Source:</span>
        <span class="text-base">{{ osint.source }}</span>
      </div>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
import { osintDataTypes } from "~/constants";

definePageMeta({ layout: "project" });

const api = useApi("/api/osint/");
const route = useRoute();
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

<template>
  <FindingsSingle
    :loading="loading"
    :icon="pathType?.icon"
    :api="api"
    :title="path?.path || ''"
    :finding="path"
    entity-name="Path"
    is-asset
    fix-verb="Discard"
    @update="fetch()"
  >
    <template #metadata>
      <FindingsMetadataHost :host="path?.port?.host" />
      <FindingsMetadataPort :port="path?.port" />
      <div v-if="path?.type" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Type:</span>
        <span class="text-base">{{ path.type }}</span>
      </div>
      <div v-if="path?.status" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Status:</span>
        <span class="text-base">{{ path.status }}</span>
      </div>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
import { pathTypes } from "~/constants";

const api = useApi("/api/paths/");
const route = useRoute();
const path = ref();
const pathType = ref();
const loading = ref(true);

function fetch(initial: boolean = false) {
  loading.value = true;
  (initial ? api.getOrError : api.get)(`${route.params.path_id}/`)
    .then((response) => {
      path.value = response;
      pathType.value = pathTypes.find((t) => t.value === response.type);
    })
    .finally(() => {
      loading.value = false;
    });
}

onMounted(() => fetch(true));
</script>

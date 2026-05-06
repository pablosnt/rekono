<template>
  <FindingsSingle
    :loading="loading"
    :icon="port ? getPortIcon(port?.port, port?.service) : undefined"
    :api="api"
    :title="port?.port?.toString() || ''"
    :finding="port"
    entity-name="Port"
    is-asset
    fix-verb="Discard"
    disable-title-copy
    @update="fetch()"
  >
    <template #metadata>
      <FindingsMetadataHost :host="port?.host" />
      <div v-if="port?.service" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Service:</span>
        <span class="text-base">{{ port.service }}</span>
      </div>
      <div v-if="port?.protocol" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Protocol:</span>
        <span class="text-base">{{ port.protocol }}</span>
      </div>
      <div v-if="port?.status" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Status:</span>
        <div class="flex items-center gap-2">
          <UIcon :name="portStatus.icon" :class="`text-${portStatus.color}`" />
          <span class="text-base">{{ port.status }}</span>
        </div>
      </div>
    </template>
    <template #custom>
      <UPageCard
        v-if="port?.path.length > 0"
        title="Paths"
        variant="outline"
        :ui="{ root: 'overflow-x-auto' }"
      >
        <FindingsPaths :port="port.id" disable-url-sync />
      </UPageCard>
      <UPageCard
        v-if="port?.technology.length > 0"
        title="Technologies"
        variant="outline"
        :ui="{ root: 'overflow-x-auto' }"
      >
        <FindingsTechnologies :port="port.id" disable-url-sync />
      </UPageCard>
      <UPageCard
        title="Vulnerabilities"
        variant="outline"
        :ui="{ root: 'overflow-x-auto' }"
      >
        <FindingsVulnerabilities :port="port.id" disable-url-sync />
      </UPageCard>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
import { portStatuses } from "~/constants";

definePageMeta({ layout: "project" });

const api = useApi("/api/ports/");
const route = useRoute();
const port = ref();
const portStatus = ref();
const loading = ref(true);

function fetch() {
  loading.value = true;
  api
    .get(`${route.params.port_id}/`)
    .then((response) => {
      port.value = response;
      portStatus.value = portStatuses.find((s) => s.value === response.status);
    })
    .finally(() => {
      loading.value = false;
    });
}

onMounted(fetch);
</script>

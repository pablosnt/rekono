<template>
  <FindingsSingle
    v-if="port"
    :icon="getPortIcon(port.port, port.service)"
    :api="api"
    :title="port.port.toString()"
    :finding="port"
    entity-name="Port"
    is-asset
    fix-verb="Discard"
    @update="fetch()"
  >
    <template #metadata>
      <div v-if="port.host" class="flex items-center gap-2">
        <span class="text-muted">Host:</span>
        <a
          class="flex items-center gap-2 hover:text-primary hover:underline"
          :href="`/projects/${$route.params.project_id}/hosts/${port.host.id}`"
        >
          <UIcon
            :name="osConfig?.icon || 'i-lucide-server'"
            :class="`text-${osConfig?.color || 'neutral'}`"
          />
          <span class="text-base">{{ port.host.domain || port.host.ip }}</span>
        </a>
      </div>
      <div v-if="port.service" class="flex items-center gap-2">
        <span class="text-muted">Service:</span>
        <span class="text-base">{{ port.service }}</span>
      </div>
      <div v-if="port.protocol" class="flex items-center gap-2">
        <span class="text-muted">Protocol:</span>
        <span class="text-base">{{ port.protocol }}</span>
      </div>
      <div v-if="port.status" class="flex items-center gap-2">
        <span class="text-muted">Status:</span>
        <div class="flex items-center gap-2">
          <UIcon :name="portStatus.icon" :class="`text-${portStatus.color}`" />
          <span class="text-base">{{ port.status }}</span>
        </div>
      </div>
    </template>
    <template #custom>
      <UPageCard v-if="port.path.length > 0" title="Paths" variant="outline">
        <FindingsPaths :port="port.id" />
      </UPageCard>
      <UPageCard
        v-if="port.technology.length > 0"
        title="Technologies"
        variant="outline"
      >
        <FindingsTechnologies :port="port.id" />
      </UPageCard>
      <UPageCard title="Vulnerabilities" variant="outline">
        <FindingsVulnerabilities :port="port.id" />
      </UPageCard>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
import { portStatuses, hostOS } from "~/constants";

definePageMeta({ layout: "project" });

const api = useApi("/api/ports/");
const route = useRoute();
const port = ref();
const portStatus = ref();
const osConfig = ref();

function fetch() {
  api.get(`${route.params.port_id}/`).then((response) => {
    port.value = response;
    portStatus.value = portStatuses.find((s) => s.value === response.status);
    osConfig.value = hostOS.find((o) => o.value === response.host?.os_type);
  });
}

onMounted(fetch);
</script>

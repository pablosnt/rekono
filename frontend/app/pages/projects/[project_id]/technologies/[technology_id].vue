<template>
  <FindingsSingle
    v-if="technology"
    :api="api"
    :title="technology.name"
    :finding="technology"
    entity-name="Technology"
    is-asset
    fix-verb="Discard"
    @update="fetch()"
  >
    <template v-if="technology.description" #description>
      <span class="text-muted">{{ technology.description }}</span>
    </template>
    <template #metadata>
      <FindingsMetadataHost :host="technology.port?.host" />
      <FindingsMetadataPort :port="technology.port" />
      <div v-if="technology.version" class="flex items-center gap-2">
        <span class="text-muted">Version:</span>
        <span class="text-base">{{ technology.version }}</span>
        <UButton
          icon="i-lucide-copy"
          color="neutral"
          variant="ghost"
          size="xs"
          @click="copyText(technology.version)"
        />
      </div>
    </template>
    <template #custom>
      <UPageCard
        v-if="technology.credential.length > 0"
        title="Credentials"
        variant="outline"
      >
        <FindingsCredentials :technology="technology.id" />
      </UPageCard>
      <!-- TODO: Tables exceed page size when the window is small. Vulnerabilities is a good example -->
      <UPageCard
        v-if="technology.vulnerability.length > 0"
        title="Vulnerabilities"
        variant="outline"
      >
        <FindingsVulnerabilities :technology="technology.id" />
      </UPageCard>
      <UPageCard title="Exploits" variant="outline">
        <FindingsExploits :technology="technology.id" />
      </UPageCard>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
definePageMeta({ layout: "project" });

const api = useApi("/api/technologies/");
const route = useRoute();
const technology = ref();

function fetch() {
  api
    .get(`${route.params.technology_id}/`)
    .then((response) => (technology.value = response));
}

onMounted(fetch);
</script>

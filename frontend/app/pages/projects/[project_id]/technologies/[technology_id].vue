<template>
  <FindingsSingle
    :loading="loading"
    :api="api"
    :title="technology?.name || ''"
    :finding="technology"
    entity-name="Technology"
    is-asset
    fix-verb="Discard"
    @update="fetch()"
  >
    <template v-if="technology?.description" #description>
      <span class="text-muted">{{ technology.description }}</span>
    </template>
    <template #metadata>
      <FindingsMetadataHost :host="technology?.port?.host" />
      <FindingsMetadataPort :port="technology?.port" />
      <div v-if="technology?.version" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Version:</span>
        <span class="text-base">{{ technology.version }}</span>
        <UButton
          icon="i-lucide-copy"
          color="neutral"
          variant="ghost"
          size="xs"
          aria-label="Copy version"
          @click="copyText(technology.version)"
        />
      </div>
    </template>
    <template #custom>
      <UPageCard
        v-if="technology?.credential.length > 0"
        title="Credentials"
        variant="outline"
        :ui="{ header: 'w-full', container: 'min-w-0' }"
      >
        <FindingsCredentials :technology="technology.id" disable-url-sync />
      </UPageCard>
      <UPageCard
        v-if="technology?.vulnerability.length > 0"
        title="Vulnerabilities"
        variant="outline"
        :ui="{ header: 'w-full', container: 'min-w-0' }"
      >
        <FindingsVulnerabilities :technology="technology.id" disable-url-sync />
      </UPageCard>
      <UPageCard
        title="Exploits"
        variant="outline"
        :ui="{ header: 'w-full', container: 'min-w-0' }"
      >
        <FindingsExploits :technology="technology.id" disable-url-sync />
      </UPageCard>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
const api = useApi("/api/technologies/");
const route = useRoute();
const technology = ref();
const loading = ref(true);

function fetch() {
  loading.value = true;
  api
    .get(`${route.params.technology_id}/`)
    .then((response) => (technology.value = response))
    .finally(() => {
      loading.value = false;
    });
}

onMounted(fetch);
</script>

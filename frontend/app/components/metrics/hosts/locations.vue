<template>
  <UPageCard
    v-if="loading || locationHosts.length"
    title="Geolocation"
    class="w-full"
    variant="outline"
  >
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading size="xl" />
    </div>
    <template v-else-if="locationHosts.length">
      <FindingsHostsLocations :height="400" :hosts="locationHosts" />
    </template>
  </UPageCard>
</template>

<script setup lang="ts">
const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/hosts/");
const loading = ref(true);
const locationHosts = ref([]);

function fetch() {
  loading.value = true;
  const params = { latitude__isnull: false, longitude__isnull: false };
  api
    .list(
      "",
      props.project ? { project: props.project, ...params } : params,
      true,
    )
    .then((response) => (locationHosts.value = response.items))
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>

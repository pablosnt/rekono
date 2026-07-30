<template>
  <MetricsCard
    title="Geolocation"
    class="w-full"
    :loading="loading"
    :has-data="locationHosts.length > 0"
  >
    <FindingsHostsLocations :height="400" :hosts="locationHosts" />
  </MetricsCard>
</template>

<script setup lang="ts">
const props = defineProps<{ project?: number }>();

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

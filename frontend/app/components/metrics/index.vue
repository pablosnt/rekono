<template>
  <div class="space-y-8">
    <SkeletonMetrics
      v-if="loading && !hasFindings"
      title
      :height="500"
      :legend="findingTypes.length"
    />
    <template v-else-if="hasFindings">
      <MetricsEvolution :project="projectId" />
      <UTabs
        :items="tabs"
        class="w-full"
        :ui="{
          list: 'overflow-x-auto',
          trigger: 'min-w-38',
        }"
      >
        <template #hosts>
          <MetricsHosts :project="projectId" />
        </template>
        <template #ports>
          <LazyMetricsPorts :project="projectId" />
        </template>
        <template #technologies>
          <LazyMetricsTechnologies :project="projectId" />
        </template>
        <template #vulnerabilities>
          <LazyMetricsVulnerabilities :project="projectId" />
        </template>
        <template #exploits>
          <LazyMetricsExploits :project="projectId" />
        </template>
        <template #others>
          <LazyMetricsOthers :project="projectId" />
        </template>
        <template #triage>
          <LazyMetricsTriage :project="projectId" />
        </template>
      </UTabs>
    </template>
    <div v-else class="flex justify-center items-center mt-10">
      <UEmpty
        variant="subtle"
        icon="i-lucide-chart-bar"
        title="No findings, No metrics"
        :description="
          userStore.is_auditor
            ? 'Run some scan first and return here to see the findings metrics'
            : 'No findings were detected yet. Once some scan finds something, you will see it here'
        "
        size="xl"
      >
        <template v-if="userStore.is_auditor" #actions>
          <TasksButton
            label="Scan"
            not-rounded
            size="xl"
            :project="$route.params.project_id ? { id: projectId } : undefined"
          />
        </template>
      </UEmpty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { findingTypes } from "~/constants";
import { useUserStore } from "~/store/user";

const api = useApi();
const route = useRoute();
const projectId = route.params.project_id
  ? parseInt(route.params.project_id)
  : undefined;
const userStore = useUserStore();
const counts = reactive({
  hosts: { value: 0, loading: true },
  ports: { value: 0, loading: true },
  technologies: { value: 0, loading: true },
  paths: { value: 0, loading: true },
  osint: { value: 0, loading: true },
  credentials: { value: 0, loading: true },
  vulnerabilities: { value: 0, loading: true },
  exploits: { value: 0, loading: true },
});
const hasFindings = computed(() =>
  Object.values(counts).some((v) => v.value > 0),
);
const loading = computed(() => Object.values(counts).some((v) => v.loading));
const tabCountMap: Record<string, () => number> = {
  hosts: () => counts.hosts.value,
  ports: () => counts.ports.value,
  technologies: () => counts.technologies.value,
  vulnerabilities: () => counts.vulnerabilities.value,
  exploits: () => counts.exploits.value,
  others: () =>
    counts.osint.value + counts.paths.value + counts.credentials.value,
  triage: () =>
    counts.osint.value +
    counts.credentials.value +
    counts.vulnerabilities.value +
    counts.exploits.value,
};
const tabLoadingMap = {
  hosts: () => counts.hosts.loading,
  ports: () => counts.ports.loading,
  technologies: () => counts.technologies.loading,
  vulnerabilities: () => counts.vulnerabilities.loading,
  exploits: () => counts.exploits.loading,
  others: () =>
    counts.osint.loading && counts.paths.loading && counts.credentials.loading,
  triage: () =>
    counts.osint.loading &&
    counts.credentials.loading &&
    counts.vulnerabilities.loading &&
    counts.exploits.loading,
};
const allTabs = [
  { label: "Hosts", slot: "hosts", icon: "i-lucide-server" },
  { label: "Ports", slot: "ports", icon: "i-lucide-ethernet-port" },
  { label: "Technologies", slot: "technologies", icon: "i-lucide-layers" },
  { label: "Vulnerabilities", slot: "vulnerabilities", icon: "i-lucide-bug" },
  { label: "Exploits", slot: "exploits", icon: "i-lucide-flame" },
  { label: "Others", slot: "others", icon: "i-lucide-scan" },
  { label: "Triage", slot: "triage", icon: "i-lucide-shield-check" },
];
const tabs = computed(() =>
  allTabs.filter(
    (tab) => tabCountMap[tab.slot]() > 0 || tabLoadingMap[tab.slot](),
  ),
);

onMounted(() => {
  const params = route.params.project_id
    ? { project: route.params.project_id }
    : {};
  api
    .list("hosts/", params, false, 1, 1)
    .then((r) => {
      counts.hosts.value = r.total;
    })
    .finally(() => (counts.hosts.loading = false));
  api
    .list("ports/", params, false, 1, 1)
    .then((r) => {
      counts.ports.value = r.total;
    })
    .finally(() => (counts.ports.loading = false));
  api
    .list("technologies/", params, false, 1, 1)
    .then((r) => {
      counts.technologies.value = r.total;
    })
    .finally(() => (counts.technologies.loading = false));
  api
    .list("paths/", params, false, 1, 1)
    .then((r) => {
      counts.paths.value = r.total;
    })
    .finally(() => (counts.paths.loading = false));
  api
    .list("osint/", params, false, 1, 1)
    .then((r) => {
      counts.osint.value = r.total;
    })
    .finally(() => (counts.osint.loading = false));
  api
    .list("credentials/", params, false, 1, 1)
    .then((r) => {
      counts.credentials.value = r.total;
    })
    .finally(() => (counts.credentials.loading = false));
  api
    .list("vulnerabilities/", params, false, 1, 1)
    .then((r) => {
      counts.vulnerabilities.value = r.total;
    })
    .finally(() => (counts.vulnerabilities.loading = false));
  api
    .list("exploits/", params, false, 1, 1)
    .then((r) => {
      counts.exploits.value = r.total;
    })
    .finally(() => (counts.exploits.loading = false));
});
</script>

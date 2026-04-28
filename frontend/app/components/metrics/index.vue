<template>
  <div class="space-y-8">
    <template v-if="hasFindings">
      <MetricsEvolution :project="$route.params.project_id" />
      <UTabs :items="tabs" class="w-full">
        <template #hosts>
          <MetricsHosts :project="$route.params.project_id" />
        </template>
        <template #ports>
          <MetricsPorts :project="$route.params.project_id" />
        </template>
        <template #technologies>
          <MetricsTechnologies :project="$route.params.project_id" />
        </template>
        <template #vulnerabilities>
          <MetricsVulnerabilities :project="$route.params.project_id" />
        </template>
        <template #exploits>
          <MetricsExploits :project="$route.params.project_id" />
        </template>
        <template #others>
          <MetricsOthers :project="$route.params.project_id" />
        </template>
        <template #triage>
          <MetricsTriage :project="$route.params.project_id" />
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
        <template v-if="userStore.is_admin" #actions>
          <TasksButton
            label="Scan"
            not-rounded
            size="xl"
            :project="
              $route.params.project_id
                ? { id: parseInt($route.params.project_id) }
                : undefined
            "
          />
        </template>
      </UEmpty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const userStore = useUserStore();
const counts = inject(
  "projectCounts",
  reactive({
    hosts: 0,
    ports: 0,
    technologies: 0,
    paths: 0,
    osint: 0,
    credentials: 0,
    vulnerabilities: 0,
    exploits: 0,
  }),
);
const hasFindings = computed(() => Object.values(counts).some((v) => v > 0));
const tabCountMap: Record<string, () => number> = {
  hosts: () => counts.hosts,
  ports: () => counts.ports,
  technologies: () => counts.technologies,
  vulnerabilities: () => counts.vulnerabilities,
  exploits: () => counts.exploits,
  others: () => counts.osint + counts.paths + counts.credentials,
  triage: () =>
    counts.osint +
    counts.credentials +
    counts.vulnerabilities +
    counts.exploits,
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
  allTabs.filter((tab) => tabCountMap[tab.slot]() > 0),
);
</script>

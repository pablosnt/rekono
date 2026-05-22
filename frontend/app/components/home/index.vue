<template>
  <div>
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading size="xl" />
    </div>
    <div v-else>
      <UPageCTA
        :title="`Good ${greeting}, ${userStore.name}`"
        :description="description"
        variant="solid"
      >
        <template #links>
          <template v-if="userStore.is_admin">
            <HomeActionsScan
              v-if="targets > 0 || hasScans"
              :has-scans="hasScans"
            />
            <UButton
              label="Create Project"
              icon="i-lucide-plus"
              size="lg"
              :color="targets > 0 ? 'neutral' : 'primary'"
              :variant="targets > 0 ? 'outline' : 'solid'"
              @click="createProjectOpen = true"
            />
            <HomeActionsDocs v-if="targets === 0 && !hasScans" />
          </template>
          <template v-else-if="userStore.is_auditor">
            <HomeActionsScan
              v-if="targets > 0 || hasScans"
              :has-scans="hasScans"
            />
            <HomeActionsExploreProjects v-else-if="hasProjects" />
            <UButton
              label="Design Scans"
              icon="i-lucide-workflow"
              size="lg"
              :color="hasProjects ? 'neutral' : 'primary'"
              :variant="hasProjects ? 'outline' : 'solid'"
              to="/processes"
            />
            <HomeActionsDocs v-if="!hasProjects" />
          </template>
          <template v-else>
            <UButton
              v-if="hasFindings"
              label="View Metrics"
              icon="i-lucide-chart-bar"
              size="lg"
              to="/metrics"
            />
            <HomeActionsExploreProjects
              v-if="hasProjects"
              :color="hasFindings ? 'neutral' : 'primary'"
              :variant="hasFindings ? 'outline' : 'solid'"
            />
            <HomeActionsDocs v-if="!hasFindings" />
          </template>
        </template>
      </UPageCTA>
      <LazyCrudFormModal
        v-if="userStore.is_admin"
        :open="createProjectOpen"
        :api="projectsApi"
        :config="projectsConfig"
        @open="createProjectOpen = $event"
      />
      <div v-if="hasScans" class="mt-10 space-y-10">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <LazyHomeTopProjects @create="createProjectOpen = true" />
          <LazyHomeLatestScans :tasks="tasks" />
        </div>
        <LazyFindingsCounterAll only-active />
        <div
          v-if="hosts.length > 0 || vulnerabilities.length > 0"
          class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start"
        >
          <LazyHomeLatestHosts :hosts="hosts" />
          <LazyHomeLatestVulnerabilities :vulnerabilities="vulnerabilities" />
        </div>
      </div>
      <div v-else>
        <LazyHomeTools :tools="tools" />
        <LazyHomeFeatures />
        <LazyHomeIntegrations :integrations="integrations" />
        <LazyHomeCommunity v-once />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Host, Project, Task, Vulnerability } from "~/types/models";
import { useUserStore } from "~/store/user";

const api = useApi("/api/");
const projectsApi = useApi("/api/projects/");
const userStore = useUserStore();
const { formFields, formSchema } = useProjectsConfig();

const loading = ref(false);
const projects = useState<Project[]>("top-projects", () => []);
const hasProjects = computed(() => projects.value.length > 0);
const targets = ref(0);
const tasks = ref<Task[]>([]);
const hasScans = computed(() => tasks.value.length > 0);
const findings = reactive({
  hosts: 0,
  ports: 0,
  technologies: 0,
  paths: 0,
  osint: 0,
  credentials: 0,
  vulnerabilities: 0,
  exploits: 0,
});
const hasFindings = computed(() => Object.values(findings).some((f) => f > 0));
const hosts = ref<Host[]>([]);
const vulnerabilities = ref<Vulnerability[]>([]);
const tools = ref([]);
const integrations = ref([]);

const hour = new Date().getHours();
const greeting = hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening";
const description = computed(() => {
  if (loading.value) return "Welcome to Rekono";
  if (!hasProjects.value && !hasScans.value) {
    if (userStore.is_admin) {
      return "Rekono is your automated recon-to-report platform. It maps attack surfaces, uncovers vulnerabilities, and chains findings across your entire scope. Create your first project to define your targets and kick off the operation.";
    }
    if (userStore.is_auditor) {
      return "Rekono is your automated recon-to-report platform. It maps attack surfaces, uncovers vulnerabilities, and chains findings across your entire scope. Ask your admin to assign you to a project to launch your first scan.";
    }
    return "Rekono is your automated recon-to-report platform — mapping attack surfaces, uncovering vulnerabilities, and chaining findings across your entire scope. Your admin will add you to a project once one is ready to explore.";
  } else if (!hasScans.value) {
    if (userStore.is_auditor) {
      return "Targets are locked in. Run your first scan and let Rekono probe every host, port, and service while you plan the next move.";
    }
    return "Projects are scoped and targets are set, but no scans have run yet. Explore your projects to get familiar with the attack surface before the recon begins.";
  } else if (userStore.is_auditor) {
    return "Recon is live and findings are surfacing. Every scan peels back another layer, so keep the momentum and push deeper into the attack surface.";
  }
  return "Your team's recon is active. Dive into the latest findings, track open vulnerabilities, and explore the full picture of the attack surface.";
});

const createProjectOpen = ref(false);
const projectsConfig = reactive({
  endpoint: "/api/projects/",
  entityName: "Project",
  createForm: resolveComponent("ProjectsForm"),
  formFields,
  formSchema,
  onCreation: (data: Record<string, unknown>) =>
    navigateTo(
      (data.targets as number[]).length === 0
        ? `/projects/${data.id}`
        : `/projects/${data.id}/targets`,
    ),
});

async function fetch() {
  loading.value = true;
  api
    .get("tasks/latest/")
    .then(async (response) => {
      tasks.value = response;
      if (response.length > 0) {
        await Promise.all([
          api.get("hosts/latest/").then((r) => (hosts.value = r)),
          api
            .get("vulnerabilities/latest/")
            .then((r) => (vulnerabilities.value = r)),
          api
            .list("hosts/", {}, false, 1, 1)
            .then((r) => (findings.hosts = r.total)),
          api
            .list("ports/", {}, false, 1, 1)
            .then((r) => (findings.ports = r.total)),
          api
            .list("technologies/", {}, false, 1, 1)
            .then((r) => (findings.technologies = r.total)),
          api
            .list("paths/", {}, false, 1, 1)
            .then((r) => (findings.paths = r.total)),
          api
            .list("osint/", {}, false, 1, 1)
            .then((r) => (findings.osint = r.total)),
          api
            .list("credentials/", {}, false, 1, 1)
            .then((r) => (findings.credentials = r.total)),
          api
            .list("vulnerabilities/", {}, false, 1, 1)
            .then((r) => (findings.vulnerabilities = r.total)),
          api
            .list("exploits/", {}, false, 1, 1)
            .then((r) => (findings.exploits = r.total)),
        ]);
      } else {
        await Promise.all([
          api
            .list("tools/", { icon__isnull: false }, true)
            .then((r) => (tools.value = r.items)),
          api
            .list("integrations/", {}, true)
            .then((r) => (integrations.value = r.items)),
          api
            .list("targets/", {}, false, 1, 1)
            .then((r) => (targets.value = r.total)),
        ]);
      }
    })
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>

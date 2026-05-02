<template>
  <div>
    <UPageCTA
      :title="`Good ${greeting}, ${userStore.name}`"
      :description="description"
      variant="solid"
    >
      <template v-if="!loading" #links>
        <TasksButton
          v-if="userStore.is_auditor && hasProjects"
          size="lg"
          not-rounded
          :label="hasScans ? 'Run Scan' : 'Run First Scan'"
        />
        <UButton
          v-if="hasScans && !userStore.is_admin"
          label="View Metrics"
          icon="i-lucide-chart-bar"
          size="lg"
          to="/metrics"
        />
        <UButton
          v-if="!hasScans && userStore.is_auditor && !userStore.is_admin"
          label="Design Scan Processes"
          icon="i-lucide-workflow"
          size="lg"
          to="/processes"
        />
        <UButton
          v-if="userStore.is_admin"
          label="Create Project"
          icon="i-lucide-plus"
          size="lg"
          @click="createProjectOpen = true"
        />
        <UButton
          v-if="!userStore.is_auditor && hasProjects"
          label="Explore Projects"
          icon="i-lucide-folder"
          size="lg"
          to="/projects"
        />
        <!-- todo: update docs link -->
        <UButton
          v-if="
            !hasProjects || (hasProjects && !hasScans && !userStore.is_auditor)
          "
          label="Learn More"
          icon="i-simple-icons-readthedocs"
          color="neutral"
          variant="outline"
          size="lg"
          to="https://github.com/pablosnt/rekono/wiki"
          target="_blank"
        />
      </template>
    </UPageCTA>
    <template v-if="!loading">
      <div v-if="tasks.length > 0" class="mt-10 space-y-10">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <UPageCard variant="outline">
            <div class="flex items-center justify-between mb-4">
              <span class="text-base font-semibold text-highlighted"
                >Top Projects</span
              >
              <div class="flex items-center gap-2">
                <template v-if="userStore.is_admin">
                  <UButton
                    icon="i-lucide-plus"
                    @click="createProjectOpen = true"
                  />
                </template>
                <UButton
                  icon="i-lucide-external-link"
                  color="neutral"
                  variant="outline"
                  to="/projects"
                />
              </div>
            </div>
            <UTable
              :data="projects"
              :columns="projectColumns"
              :ui="{ tbody: '[&>tr]:cursor-pointer' }"
              @select="(_, row) => navigateTo(`/projects/${row.original.id}`)"
            />
          </UPageCard>
          <UPageCard variant="outline">
            <div class="flex items-center justify-between mb-4">
              <span class="text-base font-semibold text-highlighted"
                >Latest Scans</span
              >
              <TasksButton v-if="userStore.is_auditor" not-rounded />
            </div>
            <UTable
              :data="tasks"
              :columns="scanColumns"
              :ui="{ tbody: '[&>tr]:cursor-pointer' }"
              @select="
                (_, row) =>
                  navigateTo(
                    `/projects/${row.original.target.project}/scans/${row.original.id}`,
                  )
              "
            />
          </UPageCard>
        </div>
        <FindingsCounterAll only-active />
        <div
          v-if="hosts.length > 0 || vulnerabilities.length > 0"
          class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start"
        >
          <UPageCard variant="outline">
            <div class="flex items-center justify-between mb-4">
              <span class="text-base font-semibold text-highlighted"
                >Latest Hosts</span
              >
            </div>
            <UTable
              :data="hosts"
              :columns="hostColumns"
              :ui="{ tbody: '[&>tr]:cursor-pointer' }"
              @select="
                (_, row) =>
                  navigateTo(
                    `/projects/${row.original.project}/hosts/${row.original.id}`,
                  )
              "
            />
          </UPageCard>
          <UPageCard variant="outline">
            <div class="flex items-center justify-between mb-4">
              <span class="text-base font-semibold text-highlighted"
                >Latest Vulnerabilities</span
              >
            </div>
            <UTable
              :data="vulnerabilities"
              :columns="vulnerabilityColumns"
              :ui="{ tbody: '[&>tr]:cursor-pointer' }"
              @select="
                (_, row) =>
                  navigateTo(
                    `/projects/${row.original.project}/vulnerabilities/${row.original.id}`,
                  )
              "
            />
          </UPageCard>
        </div>
        <CrudFormModal
          v-if="userStore.is_admin"
          :open="createProjectOpen"
          :api="projectsApi"
          :config="projectsConfig"
          @open="createProjectOpen = $event"
        />
      </div>
      <div v-else>
        <UPageSection title="Supported Tools">
          <UMarquee>
            <UAvatar
              v-for="tool in tools"
              :key="tool.id"
              :src="tool.icon"
              size="xl"
            />
          </UMarquee>
        </UPageSection>
        <UPageSection
          title="Core Features"
          :features="[
            {
              title: 'Processes',
              description:
                'Design your scanning workflows to combine multiple hacking tools',
              icon: 'i-lucide-workflow',
              to: '/processes',
            },
            {
              title: 'Reports',
              description:
                'Export polished reports in multiple formats, ready for clients, stakeholders, or automated pipelines',
              icon: 'i-lucide-file-text',
              ui: { leadingIcon: 'text-neutral' },
            },
            {
              title: 'Metrics',
              description:
                'Track vulnerability trends, measure coverage, and visualize how your attack surface evolves',
              icon: 'i-lucide-chart-bar',
              to: '/metrics',
              ui: { leadingIcon: 'text-success' },
            },
            {
              title: 'Alerts',
              description:
                'Receive notifications when the finding that you are looking for is detected',
              icon: 'i-lucide-triangle-alert',
              ui: { leadingIcon: 'text-warning' },
            },
            {
              title: 'Notes',
              description:
                'Capture hypotheses, annotate findings, and plan your recon strategy where the work happens',
              icon: 'i-lucide-notebook',
              ui: { leadingIcon: 'text-purple-500' },
            },
            {
              title: 'Telegram Bot',
              description:
                'Away From Keyboard? Keep triggering scans from our Telegram Bot',
              icon: 'i-simple-icons-telegram',
              to: integrationsStore.telegram?.is_available
                ? `https://t.me/${integrationsStore.telegram?.bot}`
                : undefined,
              target: integrationsStore.telegram?.is_available
                ? '_blank'
                : undefined,
              ui: { leadingIcon: 'text-info' },
            },
          ]"
        />
        <UPageSection title="Integrations">
          <UMarquee>
            <UAvatar
              v-for="integration in integrations"
              :key="integration.id"
              :src="integration.icon"
              size="xl"
            />
          </UMarquee>
        </UPageSection>
        <UPageSection
          title="Join the Community"
          :features="[
            {
              title: 'GitHub',
              description: 'Star us',
              icon: 'i-simple-icons-github',
              to: 'https://github.com/pablosnt/rekono',
              target: '_blank',
              orientation: 'vertical',
              ui: { root: 'text-center', leadingIcon: 'text-neutral' },
            },
            {
              title: 'Twitter',
              description: 'Follow us',
              icon: 'i-simple-icons-x',
              to: 'https://x.com/rekonosec',
              target: '_blank',
              orientation: 'vertical',
              ui: { root: 'text-center', leadingIcon: 'text-neutral' },
            },
            {
              title: 'Discord',
              description: 'Join us',
              icon: 'i-simple-icons-discord',
              to: 'https://discord.gg/Zyduu5C7M3',
              target: '_blank',
              orientation: 'vertical',
              ui: { root: 'text-center', leadingIcon: 'text-indigo-500' },
            },
            {
              title: 'Ko-fi',
              description: 'Support us',
              icon: 'i-simple-icons-kofi',
              to: 'https://ko-fi.com/pablosnt',
              target: '_blank',
              orientation: 'vertical',
              ui: { root: 'text-center', leadingIcon: 'text-primary' },
            },
            {
              title: 'Buy Me a Coffee',
              description: 'Support us',
              icon: 'i-simple-icons-buymeacoffee',
              to: 'https://buymeacoffee.com/pablosnt',
              target: '_blank',
              orientation: 'vertical',
              ui: { root: 'text-center', leadingIcon: 'text-warning' },
            },
            {
              title: 'Docs',
              description: 'Read us',
              icon: 'i-simple-icons-readthedocs',
              to: 'https://github.com/pablosnt/rekono/wiki',
              target: '_blank',
              orientation: 'vertical',
              ui: { root: 'text-center', leadingIcon: 'text-neutral' },
            },
          ]"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { Host, Project, Task, Vulnerability } from "~/types/models";
import { useUserStore } from "~/store/user";
import {
  executionStatuses,
  hostOS,
  severities,
  targetTypes,
} from "~/constants";
import { useIntegrationsStore } from "~/store/integrations";

const api = useApi("/api/");
const projectsApi = useApi("/api/projects/");
const userStore = useUserStore();
const table = useTable();
const { formFields, formSchema } = useProjectsConfig();
const integrationsStore = useIntegrationsStore();

const hour = new Date().getHours();
const greeting = hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening";
const loading = ref(false);
const projects = useState<Project[]>("top-projects", () => []);
const tasks = ref<Task[]>([]);
const hosts = ref<Host[]>([]);
const vulnerabilities = ref<Vulnerability[]>([]);
const tools = ref([]);
const integrations = ref([]);
const hasScans = computed(() => tasks.value.length > 0);
const hasProjects = computed(() => projects.value.length > 0);
const description = computed(() => {
  if (loading.value) return "Welcome to Rekono";
  if (!hasProjects.value && !hasScans.value) {
    if (userStore.is_admin) {
      return "Rekono is your automated recon-to-report platform. It maps attack surfaces, uncovers vulnerabilities, and chains findings across your entire scope.Create your first project to define your targets and kick off the operation.";
    }
    if (userStore.is_auditor) {
      return "Rekono is your automated recon-to-report platform. It maps attack surfaces, uncovers vulnerabilities, and chains findings across your entire scope.Ask your admin to assign you to a project to launch your first scan.";
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
const projectColumns = [
  {
    accessorKey: "name",
    header: table.iconAndValueHeader("Name", "i-lucide-case-sensitive"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell(row.getValue("name") as string),
  },
  {
    accessorKey: "tags",
    header: table.iconAndValueHeader("Tags", "i-lucide-tag"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      h(resolveComponent("CrudTags"), { tags: row.getValue("tags") }),
  },
  {
    accessorKey: "targets",
    header: table.iconAndValueHeader("Targets", "i-lucide-locate-fixed"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell((row.getValue("targets") as number[]).length),
  },
];
const scanColumns = [
  {
    id: "scanner",
    header: table.iconAndValueHeader("Scanner", "i-lucide-terminal"),
    cell: ({ row }: { row: { original: Task } }) =>
      row.original.process
        ? table.valueCell(row.original.process.name)
        : table.toolCell(
            row.original.configuration?.tool,
            row.original.configuration,
          ),
  },
  {
    id: "target",
    header: table.iconAndValueHeader("Target", "i-lucide-locate-fixed"),
    cell: ({ row }: { row: { original: Task } }) => {
      let label = row.original.target?.target;
      if (row.original.target_port) {
        label += `:${row.original.target_port.port}`;
        if (row.original.target_port.path) {
          label +=
            row.original.target_port.path[0] === "/"
              ? row.original.target_port.path
              : `/${row.original.target_port.path}`;
        }
      }
      const icon =
        targetTypes.find((t) => t.value === row.original.target?.type)?.icon ||
        "i-lucide-locate-fixed";
      return table.iconAndValueCell(label, icon);
    },
  },
  {
    id: "status",
    header: table.iconAndValueHeader("Status", "i-lucide-activity"),
    cell: ({ row }: { row: { original: Task } }) => {
      const status = executionStatuses.find(
        (s) => s.value === row.original.status,
      );
      return row.original.status === "Running"
        ? h(resolveComponent("UProgress"), {
            status: true,
            modelValue: row.original.progress,
            max: 100,
            color: "warning",
          })
        : table.badgeCell(status?.value, status?.icon, status?.color);
    },
  },
];
const hostColumns = [
  {
    accessorKey: "ip",
    header: table.iconAndValueHeader("IP", "i-lucide-server"),
    cell: ({ row }: { row: { original: Host } }) =>
      table.valueCell(row.original.ip),
  },
  {
    accessorKey: "domain",
    header: table.iconAndValueHeader("Domain", "i-lucide-globe"),
    cell: ({ row }: { row: { original: Host } }) =>
      table.valueCell(row.original.domain),
  },
  {
    accessorKey: "os",
    header: table.iconAndValueHeader("OS", "i-lucide-monitor"),
    cell: ({ row }: { row: { original: Host } }) => {
      const osConfig = hostOS.find((o) => o.value === row.original.os_type);
      return table.iconAndValueCell(
        row.original.os,
        osConfig?.icon,
        osConfig?.color,
      );
    },
  },
];
const vulnerabilityColumns = [
  {
    id: "host",
    header: table.iconAndValueHeader("Host", "i-lucide-server"),
    cell: ({ row }: { row: { original: Vulnerability } }) =>
      table.hostCell(
        row.original.port?.host || row.original.technology?.port?.host,
        row.original.project,
      ),
  },
  {
    accessorKey: "name",
    header: table.iconAndValueHeader("Name", "i-lucide-case-sensitive"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell(row.getValue("name") as string),
  },
  {
    accessorKey: "severity",
    header: table.iconAndValueHeader("Severity", "i-lucide-shield-alert"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) => {
      const value = row.getValue("severity") as string | undefined;
      const severity = severities.find((s) => s.value === value);
      return table.badgeCell(value, severity?.icon, severity?.color);
    },
  },
  {
    accessorKey: "cve",
    header: table.iconAndValueHeader("CVE", "i-lucide-hash"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell(row.getValue("cve") as string | undefined),
  },
];

function fetch() {
  loading.value = true;
  api
    .get("tasks/latest/")
    .then((response) => {
      tasks.value = response;
      if (response.length > 0) {
        api.get("hosts/latest/").then((response) => (hosts.value = response));
        api
          .get("vulnerabilities/latest/")
          .then((response) => (vulnerabilities.value = response));
      } else {
        api
          .list("tools/", { icon__isnull: false }, true)
          .then((response) => (tools.value = response.items));
        api
          .list("integrations/", {}, true)
          .then((response) => (integrations.value = response.items));
      }
    })
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>

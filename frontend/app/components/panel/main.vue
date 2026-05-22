<template>
  <Panel :navigation-items="items" storage-key="panel">
    <slot />
  </Panel>
</template>

<script setup lang="ts">
import type { Project } from "~/types/models";
import { useUserStore } from "~/store/user";

const api = useApi("/api/");
const userStore = useUserStore();
const { panelRefresh } = usePanel();
const topProjects = useState<Project[]>("top-projects", () => []);
const badges = reactive({
  projects: "",
  hosts: "",
  ports: "",
  technologies: "",
  paths: "",
  osint: "",
  credentials: "",
  vulnerabilities: "",
  exploits: "",
});
const topProjectChildren = ref([]);
const items = computed(() => [
  {
    label: "Home",
    icon: "i-lucide-house",
    to: "/",
  },
  {
    label: "Projects",
    icon: "i-lucide-folder",
    type: "link",
    defaultOpen: true,
    to: "/projects",
    badge: badges.projects || undefined,
    children:
      topProjectChildren.value.length > 0
        ? topProjectChildren.value
        : undefined,
  },
  {
    label: "Assets",
    icon: "i-lucide-server",
    defaultOpen: true,
    children: [
      {
        label: "Hosts",
        icon: "i-lucide-server",
        to: "/hosts",
        badge: badges.hosts || undefined,
      },
      {
        label: "Ports",
        icon: "i-lucide-ethernet-port",
        to: "/ports",
        badge: badges.ports || undefined,
      },
      {
        label: "Technologies",
        icon: "i-lucide-layers",
        to: "/technologies",
        badge: badges.technologies || undefined,
      },
      {
        label: "Paths",
        icon: "i-lucide-slash",
        to: "/paths",
        badge: badges.paths || undefined,
      },
    ],
  },
  {
    label: "Findings",
    icon: "i-lucide-scan",
    defaultOpen: true,
    children: [
      {
        label: "OSINT",
        icon: "i-lucide-rss",
        to: "/osint",
        badge: badges.osint || undefined,
      },
      {
        label: "Credentials",
        icon: "i-lucide-key",
        to: "/credentials",
        badge: badges.credentials || undefined,
      },
      {
        label: "Vulnerabilities",
        icon: "i-lucide-bug",
        to: "/vulnerabilities",
        badge: badges.vulnerabilities || undefined,
      },
      {
        label: "Exploits",
        icon: "i-lucide-flame",
        to: "/exploits",
        badge: badges.exploits || undefined,
      },
    ],
  },
  {
    label: "Metrics",
    icon: "i-lucide-chart-bar",
    to: "/metrics",
  },
  ...(userStore.is_auditor
    ? [
        {
          label: "Toolkit",
          icon: "i-lucide-toolbox",
          defaultOpen: false,
          children: [
            {
              label: "Tools",
              icon: "i-lucide-square-terminal",
              to: "/tools",
            },
            {
              label: "Processes",
              icon: "i-lucide-workflow",
              to: "/processes",
            },
            {
              label: "Wordlists",
              icon: "i-mdi-file-word",
              to: "/wordlists",
            },
          ],
        },
      ]
    : []),
  ...(userStore.is_admin
    ? [
        {
          label: "Administration",
          icon: "i-lucide-settings",
          defaultOpen: false,
          children: [
            {
              label: "System",
              icon: "i-lucide-settings",
              to: "/admin/system",
            },
            {
              label: "Integrations",
              icon: "i-lucide-plug",
              to: "/admin/integrations",
            },
            {
              label: "Users",
              icon: "i-lucide-users",
              to: "/admin/users",
            },
          ],
        },
      ]
    : []),
]);

function loadBadges() {
  api.get("projects/top/").then((response: Project[]) => {
    topProjects.value = response;
    const children = [];
    for (let i = 0; i < response.length; i++) {
      children.push({
        label: response[i].name,
        avatar: { text: response[i].name.charAt(0).toUpperCase() },
        to: `/projects/${response[i].id}`,
      });
    }
    if (children.length > 0) {
      api.list("projects/", {}, false, 1, 1).then((projectsCount: object) => {
        badges.projects = formatCount(projectsCount.total);
        if (projectsCount.total > children.length) {
          children.push({
            label: "Show all",
            to: "/projects",
          });
        }
        topProjectChildren.value = children;
      });
    } else {
      badges.projects = "0";
      topProjectChildren.value = [];
    }
  });
  const openFindings = { is_fixed: false };
  const activeFindings = {
    triage_status__in: "True Positive,Untriaged",
    ...openFindings,
  };
  api
    .list("hosts/", openFindings, false, 1, 1)
    .then((response: object) => (badges.hosts = formatCount(response.total)));
  api
    .list("ports/", openFindings, false, 1, 1)
    .then((response: object) => (badges.ports = formatCount(response.total)));
  api
    .list("technologies/", openFindings, false, 1, 1)
    .then(
      (response: object) => (badges.technologies = formatCount(response.total)),
    );
  api
    .list("paths/", openFindings, false, 1, 1)
    .then((response: object) => (badges.paths = formatCount(response.total)));
  api
    .list("osint/", activeFindings, false, 1, 1)
    .then((response: object) => (badges.osint = formatCount(response.total)));
  api
    .list("credentials/", activeFindings, false, 1, 1)
    .then(
      (response: object) => (badges.credentials = formatCount(response.total)),
    );
  api
    .list("vulnerabilities/", activeFindings, false, 1, 1)
    .then(
      (response: object) =>
        (badges.vulnerabilities = formatCount(response.total)),
    );
  api
    .list("exploits/", activeFindings, false, 1, 1)
    .then(
      (response: object) => (badges.exploits = formatCount(response.total)),
    );
}

onMounted(loadBadges);

watch(panelRefresh, loadBadges);
</script>

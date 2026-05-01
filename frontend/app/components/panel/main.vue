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
const items = ref([
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
      },
      {
        label: "Ports",
        icon: "i-lucide-ethernet-port",
        to: "/ports",
      },
      {
        label: "Technologies",
        icon: "i-lucide-layers",
        to: "/technologies",
      },
      {
        label: "Paths",
        icon: "i-lucide-slash",
        to: "/paths",
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
      },
      {
        label: "Credentials",
        icon: "i-lucide-key",
        to: "/credentials",
      },
      {
        label: "Vulnerabilities",
        icon: "i-lucide-bug",
        to: "/vulnerabilities",
      },
      {
        label: "Exploits",
        icon: "i-lucide-flame",
        to: "/exploits",
      },
    ],
  },
  {
    label: "Metrics",
    icon: "i-lucide-chart-bar",
    to: "/metrics",
  },
]);

function loadBadges() {
  api.get("projects/top/").then((response: Project[]) => {
    topProjects.value = response;
    const children: NavigationItem[] = [];
    for (let i = 0; i < response.length; i++) {
      children.push({
        label: response[i].name,
        avatar: { text: response[i].name.charAt(0).toUpperCase() },
        to: `/projects/${response[i].id}`,
      });
    }
    if (children.length > 0) {
      api.list("projects/", {}, false, 1, 1).then((response: object) => {
        if (items.value[1]) {
          items.value[1].badge = formatCount(response.total);
          if (response.total > children.length) {
            children.push({
              label: "Show all",
              to: "/projects",
            });
          }
          items.value[1].children = children;
        }
      });
    } else {
      if (items.value[1]) {
        items.value[1].badge = "0";
      }
    }
  });
  const openFindings = { is_fixed: false };
  const activeFindings = {
    triage_status__in: "True Positive,Untriaged",
    ...openFindings,
  };
  api.list("hosts/", openFindings, false, 1, 1).then((response: object) => {
    if (items.value[2]?.children?.[0]) {
      items.value[2].children[0].badge = formatCount(response.total);
    }
  });
  api.list("ports/", openFindings, false, 1, 1).then((response: object) => {
    if (items.value[2]?.children?.[1]) {
      items.value[2].children[1].badge = formatCount(response.total);
    }
  });
  api
    .list("technologies/", openFindings, false, 1, 1)
    .then((response: object) => {
      if (items.value[2]?.children?.[2]) {
        items.value[2].children[2].badge = formatCount(response.total);
      }
    });
  api.list("paths/", openFindings, false, 1, 1).then((response: object) => {
    if (items.value[2]?.children?.[3]) {
      items.value[2].children[3].badge = formatCount(response.total);
    }
  });
  api.list("osint/", activeFindings, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[0]) {
      items.value[3].children[0].badge = formatCount(response.total);
    }
  });
  api
    .list("credentials/", activeFindings, false, 1, 1)
    .then((response: object) => {
      if (items.value[3]?.children?.[1]) {
        items.value[3].children[1].badge = formatCount(response.total);
      }
    });
  api
    .list("vulnerabilities/", activeFindings, false, 1, 1)
    .then((response: object) => {
      if (items.value[3]?.children?.[2]) {
        items.value[3].children[2].badge = formatCount(response.total);
      }
    });
  api
    .list("exploits/", activeFindings, false, 1, 1)
    .then((response: object) => {
      if (items.value[3]?.children?.[3]) {
        items.value[3].children[3].badge = formatCount(response.total);
      }
    });
}

onMounted(() => {
  if (userStore.is_auditor) {
    items.value.push({
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
    });
  }
  if (userStore.is_admin) {
    items.value.push({
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
    });
  }
  loadBadges();
});

watch(panelRefresh, loadBadges);
</script>

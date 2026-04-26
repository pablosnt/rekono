<template>
  <Panel :navigation-items="items" storage-key="panel">
    <slot />
  </Panel>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi("/api/");
const userStore = useUserStore();
const counts = reactive({
  hosts: 0,
  ports: 0,
  technologies: 0,
  paths: 0,
  osint: 0,
  credentials: 0,
  vulnerabilities: 0,
  exploits: 0,
});
provide("projectCounts", readonly(counts));

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
  api.get("projects/top/").then((response: object) => {
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
          items.value[1].badge = response.total.toString();
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
  api.list("hosts/", {}, false, 1, 1).then((response: object) => {
    if (items.value[2]?.children?.[0]) {
      items.value[2].children[0].badge = response.total.toString();
    }
    counts.hosts = response.total;
  });
  api.list("ports/", {}, false, 1, 1).then((response: object) => {
    if (items.value[2]?.children?.[1]) {
      items.value[2].children[1].badge = response.total.toString();
    }
    counts.ports = response.total;
  });
  api.list("technologies/", {}, false, 1, 1).then((response: object) => {
    if (items.value[2]?.children?.[2]) {
      items.value[2].children[2].badge = response.total.toString();
    }
    counts.technologies = response.total;
  });
  api.list("paths/", {}, false, 1, 1).then((response: object) => {
    if (items.value[2]?.children?.[3]) {
      items.value[2].children[3].badge = response.total.toString();
    }
    counts.paths = response.total;
  });
  api.list("osint/", {}, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[0]) {
      items.value[3].children[0].badge = response.total.toString();
    }
    counts.osint = response.total;
  });
  api.list("credentials/", {}, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[1]) {
      items.value[3].children[1].badge = response.total.toString();
    }
    counts.credentials = response.total;
  });
  api.list("vulnerabilities/", {}, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[2]) {
      items.value[3].children[2].badge = response.total.toString();
    }
    counts.vulnerabilities = response.total;
  });
  api.list("exploits/", {}, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[3]) {
      items.value[3].children[3].badge = response.total.toString();
    }
    counts.exploits = response.total;
  });
});
</script>

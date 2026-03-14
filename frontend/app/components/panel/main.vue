<template>
  <Panel :navigation-items="items" storage-key="main-panel">
    <slot />
  </Panel>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi();
const userStore = useUserStore();

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
    to: "/assets",
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
      icon: "i-lucide-tool-case",
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
  api.get("stats/top-projects/").then((response: object) => {
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
    if (items.value[2]) {
      items.value[2].badge = response.total.toString();
    }
  });
  api.list("osint/", {}, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[0]) {
      items.value[3].children[0].badge = response.total.toString();
    }
  });
  api.list("credentials/", {}, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[1]) {
      items.value[3].children[1].badge = response.total.toString();
    }
  });
  api.list("vulnerabilities/", {}, false, 1, 1).then((response: object) => {
    if (items.value[3]?.children?.[2]) {
      items.value[3].children[2].badge = response.total.toString();
    }
  });
});
</script>

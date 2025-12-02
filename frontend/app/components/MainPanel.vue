<template>
  <UDashboardGroup>
    <UDashboardSidebar
      collapsible
      resizable
      :ui="{ footer: 'border-t border-default' }"
    >
      <template #header="{ collapsed }">
        <AppLogo v-if="!collapsed" class="h-5 w-auto shrink-0" />
        <UIcon
          v-else
          name="i-simple-icons-nuxtdotjs"
          class="size-5 text-primary mx-auto"
        />
      </template>

      <template #default="{ collapsed }">
        <UNavigationMenu
          :collapsed="collapsed"
          :items="items"
          orientation="vertical"
          popover
        />

        <!-- TODO: Move the button to the user profile page -->
        <UColorModeButton
          :label="colorMode.value === 'dark' ? 'Dark mode' : 'Light mode'"
          class="mt-auto"
          size="xl"
        />
      </template>

      <template #footer="{ collapsed }">
        <!-- TODO: Popup to show user options -->
        <UButton
          :avatar="{
            text: userStore.name ? userStore.name.charAt(0).toUpperCase() : '',
            size: 'lg',
          }"
          :label="collapsed ? undefined : userStore.name"
          color="neutral"
          variant="ghost"
          class="w-full"
          :block="collapsed"
          size="xl"
        />
      </template>
    </UDashboardSidebar>
    <slot />
  </UDashboardGroup>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
const api = useApi();
const colorMode = useColorMode();
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
        icon: "i-lucide-globe",
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
      label: "Tooling",
      icon: "i-lucide-wrench",
      defaultOpen: true,
      children: [
        {
          label: "Tools",
          icon: "i-lucide-terminal",
          to: "/tools",
        },
        {
          label: "Processes",
          icon: "i-lucide-workflow",
          to: "/processes",
        },
        {
          label: "Wordlists",
          icon: "i-lucide-file-text",
          to: "/wordlists",
        },
      ],
    });
  }
  if (userStore.is_admin) {
    items.value.push({
      label: "Administration",
      icon: "i-lucide-settings",
      defaultOpen: true,
      children: [
        {
          label: "Settings",
          icon: "i-lucide-settings",
          to: "/admin/settings",
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
  api.get("stats/top-projects/").then((response) => {
    let children = [];
    for (let i = 0; i < response.length; i++) {
      children.push({
        label: response[i].name,
        to: `/projects/${response[i].id}`,
      });
    }
    if (children.length > 0) {
      api.list("projects/", {}, false, 1, 1).then((response) => {
        items.value[1].badge = response.total.toString();
        if (response.total > children.length) {
          children.push({ label: "Show all", to: "/projects" });
        }
        items.value[1].children = children;
      });
    } else {
      items.value[1].badge = "0";
    }
  });
  api.list("hosts/", {}, false, 1, 1).then((response) => {
    items.value[2].badge = response.total.toString();
  });
  api.list("osint/", {}, false, 1, 1).then((response) => {
    items.value[3].children[0].badge = response.total.toString();
  });
  api.list("credentials/", {}, false, 1, 1).then((response) => {
    items.value[3].children[1].badge = response.total.toString();
  });
  api.list("vulnerabilities/", {}, false, 1, 1).then((response) => {
    items.value[3].children[2].badge = response.total.toString();
  });
});
</script>

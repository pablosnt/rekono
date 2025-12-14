<template>
  <UDashboardGroup>
    <UDashboardSidebar
      class="group"
      v-model:collapsed="sidebarCollapsed"
      collapsible
      resizable
      @update:collapsed="updateSidebar()"
    >
      <template #header="{ collapsed }">
        <div class="relative flex items-center justify-center w-full">
          <AppLogo v-if="!collapsed" class="h-5 w-auto shrink-0" />
          <UIcon
            v-else
            name="i-simple-icons-nuxtdotjs"
            class="size-5 text-primary opacity-100 group-hover:opacity-0 transition-opacity duration-200"
          />
          <UButton
            :icon="
              collapsed ? 'i-lucide-chevrons-right' : 'i-lucide-chevrons-left'
            "
            color="neutral"
            variant="ghost"
            :class="
              'ml-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200' +
              (collapsed ? ' absolute' : '')
            "
            @click="
              sidebarCollapsed = !sidebarCollapsed;
              updateSidebar();
            "
          />
        </div>
      </template>

      <template #default="{ collapsed }">
        <UNavigationMenu
          :collapsed="collapsed"
          :items="items"
          orientation="vertical"
          popover
        />
      </template>

      <template #footer="{ collapsed }">
        <UModal
          v-model:open="profileOpen"
          :ui="{ content: 'sm:max-w-6xl sm:max-h-2xl' }"
        >
          <UButton
            :avatar="{
              text: userStore.name
                ? userStore.name.charAt(0).toUpperCase()
                : '',
              class: 'bg-primary-500 text-white',
              size: 'lg',
            }"
            :label="collapsed ? undefined : userStore.name"
            color="neutral"
            variant="ghost"
            class="w-full"
            :block="collapsed"
            size="xl"
            @click="profileOpen = true"
          />
          <template #header>
            <UUser
              :avatar="{
                text: userStore.name
                  ? userStore.name.charAt(0).toUpperCase()
                  : '',
                class: 'bg-primary-500 text-white',
              }"
              size="xl"
              :name="userStore.name"
              :description="userStore.role"
            />
            <UColorModeButton class="ml-auto" size="xl" />
            <UButton
              icon="i-lucide-x"
              size="xl"
              variant="ghost"
              color="neutral"
              @click="profileOpen = false"
            />
          </template>
          <template #body>
            <Profile />
          </template>
        </UModal>
      </template>
    </UDashboardSidebar>
    <UContainer class="flex flex-col min-h-full">
      <div class="flex-1">
        <slot />
      </div>
      <Footer />
    </UContainer>
  </UDashboardGroup>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi();
const userStore = useUserStore();
const profileOpen = ref(false);
const sidebarCollapsed = ref(null);
const sidebarCollapsedKey = ref("main-panel-collapsed");
const mounted = ref(false);
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

function updateSidebar() {
  if (!mounted.value) return;
  localStorage.setItem(sidebarCollapsedKey.value, sidebarCollapsed.value);
}

onMounted(() => {
  mounted.value = true;
  if (localStorage.getItem(sidebarCollapsedKey.value) === "true") {
    sidebarCollapsed.value = true;
  } else {
    sidebarCollapsed.value = false;
  }
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
    const children = [];
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

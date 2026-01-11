<template>
  <UDashboardGroup
    persistent
    storage="local"
    :storage-key="sidebarCollapsedKey"
  >
    <UDashboardSidebar
      v-if="mounted"
      v-model:collapsed="sidebarCollapsed"
      class="group"
      style="display: flex"
      :resizable="largeScreen"
      collapsible
      @update:collapsed="
        (value) => {
          if (largeScreen) {
            sidebarCollapsed = value;
          }
        }
      "
    >
      <template #header>
        <div class="relative flex items-center justify-center w-full">
          <AppLogo v-if="!sidebarCollapsed" class="h-5 w-auto shrink-0" />
          <UIcon
            v-else
            name="i-simple-icons-nuxtdotjs"
            class="size-5 text-primary opacity-100 group-hover:opacity-0 transition-opacity duration-200"
          />
          <UButton
            v-if="largeScreen"
            :icon="
              sidebarCollapsed
                ? 'i-lucide-chevrons-right'
                : 'i-lucide-chevrons-left'
            "
            color="neutral"
            variant="ghost"
            :class="
              'ml-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200' +
              (sidebarCollapsed ? ' absolute' : '')
            "
            @click="sidebarCollapsed = !sidebarCollapsed"
          />
        </div>
      </template>
      <UNavigationMenu
        :collapsed="sidebarCollapsed"
        :items="items"
        orientation="vertical"
        popover
      />
      <template #footer>
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
            :label="sidebarCollapsed ? undefined : userStore.name || undefined"
            color="neutral"
            variant="ghost"
            class="w-full"
            :block="sidebarCollapsed"
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
              :name="userStore.name || undefined"
              :description="userStore.role || undefined"
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
    <UDashboardPanel>
      <template #body>
        <UContainer class="min-h-screen">
          <slot />
          <Footer />
        </UContainer>
      </template>
    </UDashboardPanel>
  </UDashboardGroup>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi();
const userStore = useUserStore();
const profileOpen = ref(false);
const sidebarCollapsed = ref(false);
const sidebarCollapsedKey = ref("main-panel");
const mounted = ref(false);
const windowWidth = ref(0);
const largeScreen = computed(() => windowWidth.value >= 1024);
interface NavigationItem {
  label: string;
  icon: string;
  to?: string;
  type?: "link" | "label" | "trigger";
  defaultOpen?: boolean;
  children?: NavigationItem[];
  badge?: string;
}

const items = ref<NavigationItem[]>([
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

const handleResize = () => {
  windowWidth.value = window.innerWidth;
  if (!largeScreen.value) {
    sidebarCollapsed.value = true;
  }
};

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
});

onMounted(() => {
  mounted.value = true;
  handleResize();
  window.addEventListener("resize", handleResize);
  if (userStore.is_auditor) {
    items.value.push({
      label: "Tooling",
      icon: "i-lucide-terminal",
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
  api.get("stats/top-projects/").then((response: object) => {
    const children: NavigationItem[] = [];
    for (let i = 0; i < response.length; i++) {
      children.push({
        label: response[i].name,
        icon: "i-lucide-folder",
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
              icon: "i-lucide-list",
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

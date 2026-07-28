<template>
  <div class="flex flex-1 h-full overflow-hidden [contain:layout]">
    <USidebar
      v-model:open="open"
      variant="floating"
      collapsible="icon"
      mode="drawer"
      :ui="{
        container: 'h-full [contain:layout]',
      }"
      :style="{ '--sidebar-width': '14rem' }"
      rail
    >
      <UNavigationMenu
        :items="items"
        :collapsed="collapsed"
        orientation="vertical"
        tooltip
        :ui="{ link: 'p-1.5 overflow-hidden' }"
      />
      <template #footer>
        <UButton
          icon="i-lucide-log-out"
          :label="collapsed ? undefined : 'Logout'"
          aria-label="Logout"
          color="neutral"
          variant="ghost"
          size="lg"
          block
          @click="logout()"
        />
      </template>
    </USidebar>
    <div class="flex-1 p-4 overflow-y-auto">
      <UContainer>
        <template v-if="active === 'profile'">
          <ProfileInformation />
        </template>
        <template v-else-if="active === 'security'">
          <LazyProfileUpdatePassword />
          <LazyProfileMfa />
          <LazyProfileApiTokens />
        </template>
        <template v-else-if="active === 'telegram-bot'">
          <LazyProfileTelegramBot />
        </template>
        <template v-else-if="active === 'http-headers'">
          <LazyHttpHeaders
            :user="userStore.user"
            :can-create="true"
            :can-edit="true"
            :can-delete="true"
            :can-read="true"
          />
        </template>
      </UContainer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";

const open = defineModel<boolean>("sidebarOpen", { default: true });

const userStore = useUserStore();
const integrations = useIntegrationsStore();
const api = useApi("/api/security/logout/");
const breakpoints = useBreakpoints(breakpointsTailwind);
const collapsed = computed(
  () => breakpoints.smaller("sm").value && !open.value,
);
const active = ref("profile");
const isTelegramAvailable = integrations.telegram?.is_available;
const baseItems = [
  { label: "Profile", icon: "i-lucide-user", value: "profile" },
  {
    label: "Telegram Bot",
    icon: "i-simple-icons-telegram",
    value: "telegram-bot",
  },
  { label: "Security", icon: "i-lucide-lock", value: "security" }
];
if (userStore.is_auditor) baseItems.push({ label: "HTTP Headers", icon: "i-lucide-globe", value: "http-headers" },)
const items = computed(() =>
  baseItems
    .filter((item) => item.value !== "telegram-bot" || isTelegramAvailable)
    .map((item) =>
      Object.assign({}, item, {
        active: active.value === item.value,
        onSelect: () => {
          active.value = item.value;
          if (breakpoints.smaller("sm").value) open.value = false;
        },
      }),
    ),
);

function logout() {
  if (userStore.is_authenticated) {
    api.create("");
  }
  return userStore.logout();
}

onMounted(integrations.fetchTelegram);
</script>

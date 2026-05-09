<template>
  <div class="flex flex-1 h-full">
    <USidebar collapsible="none">
      <UNavigationMenu
        :items="items"
        orientation="vertical"
        :ui="{ link: 'p-1.5 overflow-hidden' }"
      />
      <template #footer>
        <UButton
          icon="i-lucide-log-out"
          label="Logout"
          color="neutral"
          variant="ghost"
          size="lg"
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
          <ProfileUpdatePassword />
          <ProfileMfa />
          <ProfileApiTokens />
        </template>
        <template v-else-if="active === 'telegram-bot'">
          <ProfileTelegramBot />
        </template>
        <template v-else-if="active === 'http-headers'">
          <HttpHeaders
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
import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";

const userStore = useUserStore();
const integrations = useIntegrationsStore();
const api = useApi("/api/security/logout/");
const active = ref("profile");
const isTelegramAvailable = integrations.telegram?.is_available;
const baseItems = [
  { label: "Profile", icon: "i-lucide-user", value: "profile" },
  {
    label: "Telegram Bot",
    icon: "i-simple-icons-telegram",
    value: "telegram-bot",
  },
  { label: "Security", icon: "i-lucide-lock", value: "security" },
  { label: "HTTP Headers", icon: "i-lucide-globe", value: "http-headers" },
];
const items = computed(() =>
  baseItems
    .filter((item) => item.value !== "telegram-bot" || isTelegramAvailable)
    .map((item) => ({
      ...item,
      active: active.value === item.value,
      onSelect: () => (active.value = item.value),
    })),
);

function logout() {
  if (userStore.is_authenticated) {
    api.create("");
  }
  return userStore.logout();
}

onMounted(integrations.fetchTelegram);
</script>

<template>
  <!-- todo: this navigation menu is not responsive  -->
  <!-- todo: components where we use the class w- and a static number are not responsive -->
  <div class="flex flex-row w-full h-180 overflow-hidden">
    <div class="w-64 border-r border-default flex flex-col h-full">
      <UNavigationMenu
        :items="items"
        orientation="vertical"
        class="flex-1 p-2"
      />
      <UButton
        icon="i-lucide-log-out"
        label="Logout"
        color="neutral"
        variant="ghost"
        size="lg"
        class="m-2"
        @click="logout()"
      />
    </div>

    <div class="flex-1 overflow-y-auto">
      <UContainer>
        <template v-if="active === 'profile'">
          <ProfileInformation />
        </template>
        <template v-else-if="active === 'security'">
          <ProfileChangePassword />
          <ProfileMfa />
          <ProfileApiTokens />
        </template>
        <template v-else-if="active === 'telegram-bot'">
          <ProfileTelegramBot :settings="telegramSettings" />
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

const userStore = useUserStore();
const api = useApi("/api/security/logout/", false);
const telegramSettingsApi = useApi("/api/telegram/settings/");
const telegramSettings = ref();
const tokens = useTokens();
const active = ref("profile");

const baseItems = [
  { label: "Profile", icon: "i-lucide-user", value: "profile" },
  {
    label: "Telegram Bot",
    icon: "i-simple-icons-telegram",
    value: "telegram-bot",
  },
  { label: "Security", icon: "i-lucide-lock", value: "security" },
  {
    label: "HTTP Headers",
    icon: "i-lucide-globe",
    value: "http-headers",
  },
];

const items = computed(() =>
  baseItems
    .filter(
      (item) =>
        item.value !== "telegram-bot" || telegramSettings.value?.is_available,
    )
    .map((item) => ({
      ...item,
      active: active.value === item.value,
      onSelect: () => (active.value = item.value),
    })),
);

function logout() {
  const refresh = tokens.get().refresh;
  if (refresh) {
    api.create("", { refresh: refresh });
  }
  return api.forwardToLogin();
}

onMounted(() => {
  telegramSettingsApi.get("1/").then((response) => {
    telegramSettings.value = response;
  });
});
</script>

<template>
  <UDashboardGroup persistent storage="local" :storage-key="storageKey">
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
          <UColorModeImage
            v-else
            light="/favicon-light.ico"
            dark="/favicon-dark.ico"
            class="opacity-100 group-hover:opacity-0 transition-opacity duration-200"
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
        :items="navigationItems"
        orientation="vertical"
        tooltip
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
      <template #header>
        <slot name="header" />
      </template>
      <template #body>
        <div class="mx-10">
          <slot />
        </div>
      </template>
      <template #footer>
        <Footer />
      </template>
    </UDashboardPanel>
  </UDashboardGroup>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

defineProps<{
  storageKey: string;
  navigationItems: Array<string, unknown>;
}>();
const userStore = useUserStore();
const profileOpen = ref(false);
const sidebarCollapsed = ref(false);
const mounted = ref(false);
const windowWidth = ref(0);
const largeScreen = computed(() => windowWidth.value >= 1024);

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
});
</script>

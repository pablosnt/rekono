<template>
  <div class="flex h-dvh overflow-hidden bg-neutral-200 dark:bg-neutral-950">
    <USidebar
      v-model:open="open"
      collapsible="icon"
      variant="inset"
      rail
      :ui="{
        container: 'h-full',
      }"
    >
      <template #header>
        <slot name="panel-header" :open="open">
          <div class="relative flex items-center w-full justify-start">
            <UColorModeAvatar
              v-if="!open"
              light="/favicon-light.ico"
              dark="/favicon-dark.ico"
              alt="Rekono"
              class="size-8"
            />
            <UColorModeImage
              v-else
              dark="/logo-dark.png"
              light="/logo-light.png"
              alt="Rekono"
              class="w-full h-auto"
            />
          </div>
        </slot>
      </template>
      <UNavigationMenu
        :collapsed="!open"
        :items="items"
        orientation="vertical"
        tooltip
        popover
        :ui="{ link: 'p-1.5 overflow-hidden' }"
      />
      <template #footer>
        <UModal
          v-model:open="profileOpen"
          title="Profile"
          :fullscreen="isMobile"
          :ui="{
            content: isMobile
              ? 'flex flex-col'
              : 'sm:max-w-6xl h-[min(45rem,75dvh)] flex flex-col',
            body: 'flex-1 min-h-0 p-0',
          }"
        >
          <UButton
            :avatar="{
              text: userStore.name
                ? userStore.name.charAt(0).toUpperCase()
                : '',
              class: 'bg-primary-500',
              ui: { fallback: 'text-white' },
              size: 'sm',
            }"
            :label="open ? userStore.name || undefined : undefined"
            :aria-label="
              !open ? `Open profile for ${userStore.name || 'user'}` : undefined
            "
            color="neutral"
            variant="ghost"
            class="w-full"
            :block="!open"
            @click="profileOpen = true"
          />
          <template #header>
            <UButton
              icon="i-lucide-menu"
              size="xl"
              variant="ghost"
              color="neutral"
              class="lg:hidden"
              aria-label="Open profile navigation"
              @click="profileSidebarOpen = true"
            />
            <UUser
              :avatar="{
                text: userStore.name
                  ? userStore.name.charAt(0).toUpperCase()
                  : '',
                class: 'bg-primary-500 text-white',
                ui: { fallback: 'text-white' },
              }"
              :name="userStore.name || undefined"
              :description="userStore.role || undefined"
            />
            <UColorModeButton class="ml-auto" size="xl" />
            <UButton
              icon="i-lucide-x"
              size="xl"
              variant="ghost"
              color="neutral"
              aria-label="Close profile"
              @click="profileOpen = false"
            />
          </template>
          <template #body>
            <Profile v-model:sidebar-open="profileSidebarOpen" />
          </template>
        </UModal>
      </template>
    </USidebar>
    <div class="flex-1 min-w-0 flex flex-col min-h-0 lg:m-4 lg:mb-0 lg:ms-0">
      <div
        class="flex-1 min-h-0 overflow-y-auto bg-default lg:rounded-xl lg:shadow-sm lg:ring lg:ring-default flex flex-col"
      >
        <div class="flex items-center gap-2 p-3 lg:hidden">
          <UTooltip
            text="Open panel"
            :content="{
              side: 'right',
              sideOffset: 8,
              collisionPadding: 8,
            }"
          >
            <UButton
              icon="i-lucide-panel-left-open"
              variant="ghost"
              color="neutral"
              aria-label="Open navigation"
              @click="open = true"
            />
          </UTooltip>
        </div>
        <slot name="content-header" />
        <div class="p-4 lg:p-10 lg:mx-10 flex-1">
          <slot />
        </div>
        <Footer v-once class="lg:hidden" />
      </div>
      <Footer v-once class="hidden lg:block" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  useLocalStorage,
  useBreakpoints,
  breakpointsTailwind,
} from "@vueuse/core";
import { useUserStore } from "~/store/user";

const props = defineProps<{
  storageKey: string;
  navigationItems: Array<Record<string, unknown>>;
}>();

const route = useRoute();
const userStore = useUserStore();
const open = useLocalStorage(props.storageKey, true);
const profileOpen = ref(false);
const profileSidebarOpen = ref(true);
const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller("lg");

const items = computed(() =>
  props.navigationItems.map((item) => setActiveState(item)),
);

watch(
  () => route.path,
  () => {
    if (isMobile.value) {
      open.value = false;
    }
  },
);

function setActiveState(
  item: Record<string, unknown>,
): Array<Record<string, unknown>> {
  const newItem = { ...item };
  if (item.to) {
    const path = item.to.toString();
    newItem.active =
      route.path === path ||
      (path !== "/" &&
        route.params.project_id &&
        path !== `/projects/${route.params.project_id}` &&
        (route.path.startsWith(path) || route.path.startsWith(path + "/")));
  }
  if (item.children) {
    newItem.children = item.children.map((child) => setActiveState(child));
  }
  return newItem;
}
</script>

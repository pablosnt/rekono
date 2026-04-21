<template>
  <div class="flex flex-1 bg-neutral-200 dark:bg-neutral-950">
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
          <div class="relative flex items-center w-full justify-between">
            <div v-if="open" class="flex items-center justify-center gap-2">
              <UColorModeImage
                light="/favicon-light.ico"
                dark="/favicon-dark.ico"
                width="30"
              />
              <AppLogo class="h-7 w-auto shrink-0" />
            </div>
            <UColorModeImage
              v-else
              light="/favicon-light.ico"
              dark="/favicon-dark.ico"
              class="opacity-100 group-hover:opacity-0 transition-opacity duration-200"
              width="30"
            />
          </div>
        </slot>
      </template>
      <UNavigationMenu
        :collapsed="!open"
        :items="navigationItems"
        orientation="vertical"
        tooltip
        popover
        :ui="{ link: 'p-1.5 overflow-hidden' }"
      />
      <template #footer>
        <UModal
          v-model:open="profileOpen"
          :ui="{
            content: 'sm:max-w-6xl h-[min(45rem,75dvh)] flex flex-col',
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
            color="neutral"
            variant="ghost"
            class="w-full"
            :block="!open"
            @click="profileOpen = true"
          />
          <template #header>
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
              @click="profileOpen = false"
            />
          </template>
          <template #body>
            <Profile />
          </template>
        </UModal>
      </template>
    </USidebar>
    <div class="flex-1 flex flex-col overflow-hidden lg:m-4 lg:mt-8 lg:ms-0">
      <div
        class="flex-1 overflow-hidden bg-default lg:rounded-xl lg:shadow-sm lg:ring lg:ring-default"
      >
        <div class="flex items-center gap-2 p-3 lg:hidden">
          <UButton
            icon="i-lucide-panel-left-open"
            variant="ghost"
            color="neutral"
            @click="open = true"
          />
        </div>
        <slot name="content-header" />
        <div class="p-10 mx-10">
          <slot />
        </div>
      </div>
      <Footer />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLocalStorage } from "@vueuse/core";
import { useUserStore } from "~/store/user";

const props = defineProps<{
  storageKey: string;
  navigationItems: Array<Record<string, unknown>>;
}>();

const userStore = useUserStore();
const open = useLocalStorage(props.storageKey, true);
const profileOpen = ref(false);
</script>

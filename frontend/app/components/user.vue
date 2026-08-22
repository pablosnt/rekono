<template>
  <UPageCard variant="subtle" spotlight>
    <template #leading>
      <UUser
        :name="displayName"
        :description="user.role"
        :avatar="{
          text: displayName.charAt(0).toUpperCase(),
          class: user.id === userStore.user ? 'bg-primary-500' : '',
          ui: user.id === userStore.user ? { fallback: 'text-white' } : {},
        }"
        size="xl"
      >
        <template #name>
          <UTooltip v-if="truncatedName !== displayName" :text="displayName">
            <span>{{ truncatedName }}</span>
          </UTooltip>
          <template v-else>{{ displayName }}</template>
        </template>
      </UUser>
    </template>
    <div class="absolute top-4 right-4">
      <UTooltip v-if="user.is_active && (user.last_login || user.date_joined)">
        <UButton
          icon="i-lucide-clock"
          color="neutral"
          variant="ghost"
          aria-label="User activity"
        />
        <template #content>
          <div>
            <p v-if="user.last_login">
              Last login
              {{ useTimeAgo(new Date(user.last_login)).value }}
            </p>
            <p v-if="user.date_joined">
              Joined
              {{ useTimeAgo(new Date(user.date_joined)).value }}
            </p>
          </div>
        </template>
      </UTooltip>
    </div>
    <slot />
  </UPageCard>
</template>

<script setup lang="ts">
import type { User } from "~/types/models";
import { useUserStore } from "~/store/user";
import { useTimeAgo } from "@vueuse/core";

const props = defineProps<{ user: User }>();
const userStore = useUserStore();
const displayName = computed(() => getUserDisplayName(props.user));
const truncatedName = computed(() => truncateText(displayName.value, 15));
</script>

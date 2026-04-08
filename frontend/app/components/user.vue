<template>
  <UPageCard variant="subtle" spotlight>
    <template #leading>
      <UUser
        :name="truncateText(getUserDisplayName(user), 15)"
        :description="user.role"
        :avatar="{
          text: getUserDisplayName(user).charAt(0).toUpperCase(),
          class: user.id.toString() === userStore.user ? 'bg-primary-500' : '',
          ui:
            user.id.toString() === userStore.user
              ? { fallback: 'text-white' }
              : {},
        }"
        size="xl"
      />
    </template>
    <div class="absolute top-4 right-4">
      <UTooltip v-if="user.is_active && (user.last_login || user.date_joined)">
        <UButton icon="i-lucide-clock" color="neutral" variant="ghost" />
        <template #content>
          <div>
            <p v-if="user.last_login">
              Last login
              {{ useTimeAgo(new Date(user.last_login)) }}
            </p>
            <p v-if="user.date_joined">
              Joined
              {{ useTimeAgo(new Date(user.date_joined)) }}
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

defineProps<{ user: User }>();
const userStore = useUserStore();
</script>

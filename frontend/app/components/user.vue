<template>
  <UPageCard variant="subtle" spotlight>
    <template #leading>
      <UUser
        :name="utils.truncateText(utils.getUserDisplayName(user), 15)"
        :description="user.role"
        :avatar="{
          text: utils.getUserDisplayName(user).charAt(0).toUpperCase(),
          class:
            user.id.toString() === userStore.user
              ? 'bg-primary-500 text-white'
              : '',
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
              {{ utils.formatRelativeDatetime(user.last_login).toLowerCase() }}
            </p>
            <p v-if="user.date_joined">
              Joined
              {{ utils.formatRelativeDatetime(user.date_joined).toLowerCase() }}
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

defineProps<{ user: User }>();
const userStore = useUserStore();
const utils = useUtils();
</script>

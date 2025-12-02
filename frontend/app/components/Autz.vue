<template>
  <template v-if="userStore.isRole(role) || userStore.is_admin">
    <slot />
  </template>
  <template v-else>
    <!-- TODO -->
    <UNotification
      color="danger"
      title="Access denied"
      description="You do not have permission to access this page."
    />
  </template>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
defineProps<{ role: string }>();
const userStore = useUserStore();
</script>

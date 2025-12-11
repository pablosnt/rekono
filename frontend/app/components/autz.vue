<template>
  <template v-if="userStore.isRole(role) || userStore.is_admin">
    <slot />
  </template>
  <template v-else>
    <!-- todo -->
    <UNotification
      color="danger"
      title="Access denied"
      description="You do not have permission to access this page."
    />
  </template>
</template>
<!-- todo: remove this component? -->
<script setup lang="ts">
import { useUserStore } from "~/store/user";

defineProps<{ role: string }>();
const userStore = useUserStore();
</script>

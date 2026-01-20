<template>
  <div class="space-y-14">
    <AdminQueues />
    <AdminSettings />
    <HttpHeaders
      :can-read="userStore.is_admin"
      :can-edit="userStore.is_admin"
      :can-delete="userStore.is_admin"
      :can-create="userStore.is_admin"
      :show-access-denied-error="false"
    />
    <AdminTargetDenylist />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const userStore = useUserStore();
</script>

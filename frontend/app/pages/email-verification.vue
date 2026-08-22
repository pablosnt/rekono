<template>
  <PublicForm :title="state.title" :description="state.description">
    <template #footer>
      <UButton
        v-if="status === 'verifying'"
        label="Verifying"
        loading
        disabled
        color="primary"
        size="xl"
      />
      <UButton
        v-else
        :label="target.label"
        :icon="target.icon"
        color="primary"
        size="xl"
        @click="goToDestination"
      />
    </template>
  </PublicForm>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi("/api/users/verify-email/", false);
const route = useRoute();
const userStore = useUserStore();
const otp = route.query.otp ? route.query.otp : null;
const status = ref<"verifying" | "verified" | "failed">("verifying");
let redirectTimer: ReturnType<typeof setTimeout> | undefined;
const states = {
  verifying: {
    title: "Verifying your email",
    description: "Hold on while we confirm your new address",
  },
  verified: {
    title: "Email Verified",
    description: "Your new address is active. We'll take you back in a moment",
  },
  failed: {
    title: "Verification Failed",
    description:
      "This link is invalid or has expired. Start the email change again from your profile",
  },
};
const state = computed(() => states[status.value]);
const target = computed(() =>
  userStore.is_authenticated
    ? { to: "/", label: "Go home", icon: "i-lucide-house" }
    : { to: "/login", label: "Go to login", icon: "i-lucide-log-in" },
);

function goToDestination() {
  if (redirectTimer) clearTimeout(redirectTimer);
  navigateTo(target.value.to);
}

onMounted(() => {
  if (!otp) navigateTo(target.value.to);
  api
    .create("", { otp: otp }, undefined, undefined, [])
    .then(() => {
      status.value = "verified";
      if (userStore.is_authenticated) userStore.fetchProfile();
      redirectTimer = setTimeout(() => navigateTo(target.value.to), 10000);
    })
    .catch(() => (status.value = "failed"));
});

onUnmounted(() => {
  if (redirectTimer) clearTimeout(redirectTimer);
});
</script>

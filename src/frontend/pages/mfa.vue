<template>
  <NuxtLayout name="public" :loading="loading">
    <v-card-title class="text-center">Multi Factor Authentication</v-card-title>
    <v-card-text class="text-center">{{
      app
        ? "Type your OTP from your authenticator app"
        : "Paste the token sent to your email"
    }}</v-card-text>
    <MfaForm
      ref="mfaForm"
      allow-email
      :loading="loading"
      @new-otp="(mfa) => login(mfa)"
      @app="(value) => (app = value)"
    />
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const loading = ref(false);
const mfaForm = ref(null);
const router = useRouter();
const tokens = useTokens();
const token = ref(tokens.get().mfa);
const app = ref(true);
const api = useApi("/api/security/mfa/", false);

function login(mfa: string): void {
  loading.value = true;
  api
    .create({ token: token.value, mfa: mfa })
    .then((response) => {
      const isLogin = tokens.save(response);
      if (isLogin) {
        router.push({ name: "index" });
      }
      loading.value = false;
    })
    .catch(() => {
      loading.value = false;
      mfaForm.value.clearOtp();
    });
}
</script>

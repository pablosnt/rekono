<template>
  <NuxtLayout name="public-form" :loading="loading">
    <v-card-title class="text-center">Multi Factor Authentication</v-card-title>

    <v-card-text v-if="app" class="text-center"
      >Type your OTP from your authentication app</v-card-text
    >
    <v-card-text v-if="!app" class="text-center"
      >Type the OTP sent to your email</v-card-text
    >

    <FormMfa
      ref="mfaForm"
      :auto-trigger="true"
      :allow-email="true"
      :loading="loading"
      @new-otp="(mfa) => login(mfa)"
    >
      <template #buttons>
        <v-card-actions class="justify-center">
          <v-btn
            autofocus
            color="red"
            size="large"
            variant="tonal"
            text="Login"
            type="submit"
            :disabled="loading"
            block
          />
        </v-card-actions>
      </template>
    </FormMfa>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const loading = ref(false);
const mfaForm = ref(null);
const router = useRouter();
const tokens = useTokens();
const token = ref(tokens.get().mfa);
const api = useApi("/api/security/mfa/", false);
function login(mfa) {
  loading.value = true;
  api
    .create({ token: token.value, mfa: mfa })
    .then((response) => {
      const isLogin = tokens.save(response);
      loading.value = false;
      if (isLogin) {
        router.push({ name: "index" });
      }
    })
    .catch(() => {
      loading.value = false;
      mfaForm.value.clearOtp();
    });
}
</script>

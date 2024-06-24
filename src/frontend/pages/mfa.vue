<template>
  <NuxtLayout name="public-form" :loading="loading">
    <v-card-title class="text-center">Multi Factor Authentication</v-card-title>

    <v-card-text v-if="app" class="text-center"
      >Type your OTP from your authentication app</v-card-text
    >
    <v-card-text v-if="!app" class="text-center"
      >Type the OTP sent to your email</v-card-text
    >

    <v-form v-model="valid" @submit.prevent="login()">
      <v-otp-input
        v-if="app"
        v-model="mfa"
        variant="solo"
        autofocus
        validate-on="blur"
        :rules="[
          (o) => !!o || 'OTP is required',
          (o) => validate.mfa.test(o) || 'Invalid OTP',
        ]"
      />

      <v-text-field
        v-if="!app"
        v-model="mfa"
        density="compact"
        label="OTP"
        prepend-inner-icon="mdi-key"
        variant="outlined"
        autofocus
        validate-on="input"
        :rules="[
          (o) => !!o || 'OTP is required',
          (o) => o.length === 128 || 'Invalid OTP',
        ]"
      />

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

      <div class="text-center">
        <v-btn
          :disabled="loading"
          @click.prevent="
            app = !app;
            mfa = null;
            !app ? emailApi.create({ token: token }) : null;
          "
          >Use {{ app ? "email" : "app" }} instead</v-btn
        >
      </div>
    </v-form>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const validate = ref(useValidation());
const app = ref(true);
const mfa = ref(null);
const loading = ref(false);
const valid = ref(true);
const router = useRouter();
const tokens = useTokens();
const token = ref(tokens.get().mfa);
const api = useApi("/api/security/mfa/", false);
const emailApi = ref(useApi("/api/security/mfa/email/", false));
function login() {
  if (valid.value) {
    loading.value = true;
    api
      .create({ token: token.value, mfa: mfa.value })
      .then((response) => {
        const isLogin = tokens.save(response);
        loading.value = false;
        if (isLogin) {
          router.push({ name: "index" });
        }
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

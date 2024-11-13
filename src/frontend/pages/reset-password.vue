<template>
  <NuxtLayout name="public" :loading="loading">
    <v-card-text class="text-center"
      >You will receive via email a link to reset your password</v-card-text
    >
    <v-form v-if="!otp" v-model="valid" @submit.prevent="sendResetToken()">
      <v-text-field
        v-model="email"
        density="compact"
        label="Email"
        prepend-inner-icon="mdi-email"
        variant="outlined"
        :rules="[
          (e) => !!e || 'Email is required',
          (e) => validate.email.test(e) || 'Invalid Email address',
        ]"
        validate-on="blur"
      />
      <BaseButtonSubmit text="Reset Password" :disabled="loading" />
    </v-form>
    <PasswordForm
      v-if="otp"
      :api="api"
      submit-text="Reset Password"
      :otp="otp"
      :loading="loading"
      @loading="(value) => (loading = value)"
      @completed="() => router.push({ name: 'login' })"
    />
    <v-btn
      class="d-flex text-align-right text-medium-emphasis"
      prepend-icon="mdi-arrow-left-bold"
      variant="text"
      size="small"
      text="Login"
      to="/login"
      :disabled="loading"
    />
  </NuxtLayout>
</template>

<script setup lang="ts">
const validate = ref(useValidation());
const email = ref(null);
const loading = ref(false);
const valid = ref(true);
const alert = useAlert();
const route = useRoute();
const router = useRouter();
const otp = ref(route.query.otp ? route.query.otp : null);
const api = useApi("/api/users/reset-password/", false);

function sendResetToken(): void {
  if (valid.value) {
    loading.value = true;
    api
      .create({ email: email.value })
      .then(() => {
        loading.value = false;
        alert(
          "Done! You will receive via email a temporal link to change your password",
          "success",
        );
      })
      .catch(() => (loading.value = false));
  }
}
</script>

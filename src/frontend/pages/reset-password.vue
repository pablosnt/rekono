<template>
  <NuxtLayout name="public" :loading="loading">
    <v-card-text class="text-center"
      >You will receive a link via email to reset your password</v-card-text
    >
    <v-form v-if="!otp" v-model="valid" @submit.prevent="sendResetToken()">
      <v-text-field
        v-model="email"
        density="comfortable"
        label="Email"
        prepend-inner-icon="mdi-email"
        variant="outlined"
        :rules="[
          (e) => !!e || 'Email is required',
          (e) => validate.email.test(e) || 'Invalid Email address',
        ]"
        validate-on="blur"
      />
      <UtilsSubmit text="Reset Password" :disabled="loading" />
    </v-form>
    <PasswordForm
      v-if="otp"
      v-model="password"
      submit-text="Reset Password"
      :disabled="loading"
      @custom-submit="(valid) => resetPassword(valid)"
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
const password = ref(null);
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
          "Password reset requested. Use the link sent to your email",
          "success",
        );
      })
      .catch(() => (loading.value = false));
  }
}

function resetPassword(valid): void {
  if (valid && otp.value) {
    loading.value = true;
    api
      .update({ password: password.value, otp: otp.value })
      .then(() => {
        loading.value = false;
        password.value = null;
        router.push({ name: "login" });
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

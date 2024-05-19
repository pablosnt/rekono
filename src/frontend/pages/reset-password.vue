<template>
  <NuxtLayout name="public-form">
    <v-card-text class="text-center"
      >You will receive via email a link to reset your password</v-card-text
    >
    <v-form v-model="valid" @submit.prevent="resetPassword()">
      <v-text-field
        v-if="!otp"
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

      <v-text-field
        v-if="otp"
        v-model="password"
        :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
        :type="visible ? 'text' : 'password'"
        density="compact"
        label="Password"
        prepend-inner-icon="mdi-lock"
        variant="outlined"
        :rules="[
          (p) => !!p || 'Password is required',
          (p) =>
            validate.password(p) ||
            'Password must contain one uppercase, lowercase, digit and symbol',
        ]"
        validate-on="blur"
        @click:append-inner="visible = !visible"
      />

      <v-text-field
        v-if="otp"
        v-model="passwordConfirmation"
        :append-inner-icon="visibleConfirmation ? 'mdi-eye-off' : 'mdi-eye'"
        :type="visibleConfirmation ? 'text' : 'password'"
        density="compact"
        label="Confirm password"
        prepend-inner-icon="mdi-lock"
        variant="outlined"
        :rules="[
          (p) => !!p || 'Password confirmation is required',
          (p) => p === password || 'Paswords do not match',
        ]"
        validate-on="blur"
        @click:append-inner="visibleConfirmation = !visibleConfirmation"
      />

      <v-card-actions class="justify-center">
        <v-btn
          v-if="!loading"
          autofocus
          color="red"
          size="large"
          variant="tonal"
          text="Reset Password"
          type="submit"
          block
        />
        <v-progress-circular v-if="loading" color="error" indeterminate />
      </v-card-actions>
      <v-btn
        v-if="!loading"
        class="d-flex text-align-right text-medium-emphasis"
        prepend-icon="mdi-arrow-left-bold"
        variant="text"
        size="small"
        text="Login"
        to="/login"
      />
    </v-form>
  </NuxtLayout>
</template>

<script setup lang="ts">
const validate = ref(useValidation());
const visible = ref(false);
const visibleConfirmation = ref(false);
const email = ref(null);
const password = ref(null);
const passwordConfirmation = ref(null);
const loading = ref(false);
const valid = ref(true);
const alert = useAlert();
const route = useRoute();
const router = useRouter();
const otp = ref(route.query.otp ? route.query.otp : null);
const api = useApi("/api/users/reset-password/", false);
function resetPassword() {
  if (valid.value) {
    loading.value = true;
    let request = null;
    if (otp.value) {
      request = api
        .update({ otp: otp.value, password: password.value })
        .then(() => {
          loading.value = false;
          router.push({ name: "login" });
        });
    } else {
      request = api.create({ email: email.value }).then(() => {
        loading.value = false;
        alert(
          "Done! You will receive via email a temporal link to change your password",
          "success",
        );
      });
    }
    request.catch(() => {
      loading.value = false;
    });
  }
}
</script>

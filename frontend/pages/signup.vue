<template>
  <NuxtLayout name="public" :loading="loading">
    <v-card-title class="text-center">Welcome to Rekono!</v-card-title>
    <PasswordForm
      v-model="password"
      submit-text="Create Account"
      :submit-disabled="loading"
      @custom-submit="(valid) => submit(valid)"
    >
      <template #prepend>
        <v-text-field
          v-model="username"
          class="mb-2"
          density="comfortable"
          label="Username"
          prepend-inner-icon="mdi-account"
          variant="outlined"
          :rules="[
            (u) => !!u || 'Username is required',
            (u) => validate.name.test(u.trim()) || 'Invalid username',
          ]"
          validate-on="input"
        />
        <v-text-field
          v-model="firstName"
          class="mb-2"
          density="comfortable"
          label="First name"
          prepend-inner-icon="mdi-card-account-details-outline"
          variant="outlined"
          :rules="[
            (n) => !!n || 'First name is required',
            (n) => validate.name.test(n.trim()) || 'Invalid first name',
          ]"
          validate-on="input"
        />
        <v-text-field
          v-model="lastName"
          class="mb-2"
          prepend-inner-icon="mdi-card-account-details-outline"
          density="comfortable"
          label="Last name"
          variant="outlined"
          :rules="[
            (n) => !!n || 'Last name is required',
            (n) => validate.name.test(n.trim()) || 'Invalid last name',
          ]"
          validate-on="input"
        />
      </template>
    </PasswordForm>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const router = useRouter();
const validate = ref(useValidation());
const loading = ref(false);
const otp = route.query.otp ? route.query.otp : null;
if (!otp) {
  router.push("/login");
}
const api = useApi("/api/users/signup/", false, "User");

const username = ref(null);
const firstName = ref(null);
const lastName = ref(null);
const password = ref(null);

function submit(valid: boolean): void {
  if (valid) {
    loading.value = true;
    api
      .create({
        username: username.value.trim(),
        first_name: firstName.value.trim(),
        last_name: lastName.value.trim(),
        password: password.value,
        otp: otp,
      })
      .then(() => {
        loading.value = false;
        router.push("/login");
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

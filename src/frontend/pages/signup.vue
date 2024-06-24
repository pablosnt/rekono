<template>
  <NuxtLayout name="public-form" :loading="loading">
    <v-card-title class="text-center">Welcome to Rekono!</v-card-title>
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-text-field
        v-model="username"
        density="compact"
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
        density="compact"
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
        prepend-inner-icon="mdi-card-account-details-outline"
        density="compact"
        label="Last name"
        variant="outlined"
        :rules="[
          (n) => !!n || 'Last name is required',
          (n) => validate.name.test(n.trim()) || 'Invalid last name',
        ]"
        validate-on="input"
      />

      <v-text-field
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
        v-model="passwordConfirmation"
        :type="visible ? 'text' : 'password'"
        density="compact"
        label="Confirm password"
        prepend-inner-icon="mdi-lock"
        variant="outlined"
        :rules="[
          (p) => !!p || 'Password confirmation is required',
          (p) => p === password || 'Paswords do not match',
        ]"
        validate-on="blur"
      />

      <v-card-actions class="justify-center">
        <v-btn
          color="red"
          size="large"
          variant="tonal"
          text="Create Account"
          type="submit"
          :disabled="loading"
          block
        />
      </v-card-actions>
    </v-form>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const router = useRouter();
const validate = ref(useValidation());
const valid = ref(true);
const loading = ref(false);
const otp = route.query.otp ? route.query.otp : null;
if (!otp) {
  router.push("/login");
}
const api = useApi("/api/users/create/", false, "User");

const username = ref(null);
const firstName = ref(null);
const lastName = ref(null);
const password = ref(null);
const passwordConfirmation = ref(null);
const visible = ref(false);

function submit() {
  if (valid.value) {
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

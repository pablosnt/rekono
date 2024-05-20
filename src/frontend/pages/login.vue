<template>
  <NuxtLayout name="public-form">
    <v-form v-model="valid" @submit.prevent="login()">
      <v-text-field
        v-model="username"
        density="compact"
        label="Username"
        prepend-inner-icon="mdi-account"
        variant="outlined"
        :rules="[(u) => !!u || 'Username is required']"
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
        :rules="[(p) => !!p || 'Password is required']"
        validate-on="input"
        @click:append-inner="visible = !visible"
      />
      <v-card-actions class="justify-center">
        <v-btn
          v-if="!loading"
          color="red"
          size="large"
          variant="tonal"
          text="Login"
          type="submit"
          block
        />
        <v-progress-circular v-if="loading" color="error" indeterminate />
      </v-card-actions>
      <v-btn
        v-if="!loading"
        class="d-flex text-align-right text-medium-emphasis"
        variant="text"
        size="small"
        text="Reset password"
        to="/reset-password"
      />
    </v-form>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const username = ref(null);
const password = ref(null);
const visible = ref(false);
const loading = ref(false);
const valid = ref(true);
const router = useRouter();
const tokens = useTokens();
const api = useApi("/api/security/login/", false);
function login() {
  if (valid.value) {
    loading.value = true;
    api
      .create({ username: username.value, password: password.value })
      .then((response) => {
        const isLogin = tokens.save(response);
        loading.value = false;
        if (isLogin) {
          router.push({ name: "index" });
        } else {
          router.push({ name: "mfa" });
        }
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

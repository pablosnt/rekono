<template>
  <PublicForm
    :schema="schema"
    title="Sign in to Rekono"
    :fields="[
      {
        name: 'username',
        type: 'text',
        label: 'Username',
        placeholder: 'Enter your username',
        required: true,
        size: 'xl',
        autofocus: true,
        autocomplete: 'username',
      },
      {
        name: 'password',
        label: 'Password',
        type: 'password',
        placeholder: 'Enter your password',
        required: true,
        size: 'xl',
        autocomplete: 'current-password',
      },
    ]"
    :submit="{ label: 'Sign in', autoFocus: true, size: 'xl' }"
    :loading="loading"
    @submit="submit"
  >
    <template #password-hint>
      <ULink :to="{ path: '/reset-password' }" class="text-primary font-medium"
        >Forgot password?</ULink
      >
    </template>
  </PublicForm>
</template>

<script setup lang="ts">
import * as z from "zod";
import { useUserStore } from "~/store/user";

definePageMeta({ layout: "public" });
const api = useApi("/api/security/login/", false);
const userStore = useUserStore();
const loading = ref(false);
const schema = z.object({
  username: z.string("Username is required"),
  password: z.string("Password is required"),
});

function submit(event: object) {
  loading.value = true;
  api
    .create("", {
      username: event.data.username,
      password: event.data.password,
    })
    .then((response) => {
      userStore.login(response);
      if (userStore.is_authenticated) {
        navigateTo("/");
      } else if (userStore.is_partial_authenticated) {
        navigateTo("/mfa");
      }
    })
    .finally(() => (loading.value = false));
}
</script>

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
      },
      {
        name: 'password',
        label: 'Password',
        type: 'password',
        placeholder: 'Enter your password',
        required: true,
        size: 'xl',
      },
    ]"
    :submit="{ label: 'Sign in', autoFocus: true, size: 'xl' }"
    :loading="loading"
    @submit="onSubmit"
  >
    <template #password-hint>
      <ULink
        :to="{ path: '/reset-password' }"
        class="text-primary font-medium"
        tabindex="-1"
        >Forgot password?</ULink
      >
    </template>
  </PublicForm>
</template>

<script setup lang="ts">
import * as z from "zod";

definePageMeta({ layout: "public" });
const api = useApi("/api/security/login/", false);
const tokens = useTokens();
const loading = ref(false);
const schema = z.object({
  username: z.string("Username is required"),
  password: z.string("Password is required"),
});

function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading.value = true;
  api
    .create("", {
      username: payload.data.username,
      password: payload.data.password,
    })
    .then((response) => {
      if (tokens.login(response)) {
        navigateTo("/");
      } else {
        navigateTo("/mfa");
      }
      loading.value = false;
    })
    .catch(() => {
      loading.value = false;
    });
}
</script>

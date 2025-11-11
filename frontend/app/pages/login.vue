<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md" variant="ghost">
      <UAuthForm
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
        :validate-on="['input', 'change']"
        :submit="{ label: 'Sign in', autoFocus: true, size: 'xl' }"
        :loading="loading"
        loading-auto
        @submit="onSubmit"
      >
        <template #leading>
          <div class="flex flex-col items-center justify-center mb-3 mt-3">
            <img src="/favicon.ico" />
          </div>
        </template>
        <template #password-hint>
          <ULink to="#" class="text-primary font-medium" tabindex="-1"
            >Forgot password?</ULink
          >
        </template>
      </UAuthForm>
    </UPageCard>
  </div>
</template>

<script setup lang="ts">
import * as z from "zod";

const api = useApi("/api/security/login/", false);
const tokens = useTokens();

let loading = false;
const schema = z.object({
  username: z.string("Username is required"),
  password: z.string("Password is required"),
});

function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading = true;
  api
    .create("", {
      username: payload.data.username,
      password: payload.data.password,
    })
    .then((response) => {
      loading = false;
      if (tokens.login(response)) {
        navigateTo("/");
      } else {
        navigateTo("/mfa");
      }
    })
    .catch(() => {
      loading = false;
    });
}
</script>

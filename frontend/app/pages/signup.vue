<template>
  <PublicForm
    :schema="schema"
    title="Sign up for Rekono"
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
        name: 'first_name',
        type: 'text',
        label: 'First name',
        placeholder: 'Enter your first name',
        required: true,
        size: 'xl',
      },
      {
        name: 'last_name',
        type: 'text',
        label: 'Last name',
        placeholder: 'Enter your last name',
        required: true,
        size: 'xl',
      },
      {
        name: 'password',
        label: 'Password',
        type: 'password',
        placeholder: 'Enter your password',
        required: true,
        size: 'xl',
      },
      {
        name: 'confirmpassword',
        label: 'Confirm password',
        type: 'password',
        placeholder: 'Repeat your password',
        required: true,
        size: 'xl',
      },
    ]"
    :submit="{ label: 'Sign up', autoFocus: true, size: 'xl' }"
    :loading="loading"
    @submit="submit"
  />
</template>

<script setup lang="ts">
import * as z from "zod";

definePageMeta({ layout: "public" });
const api = useApi("/api/security/signup/", false);
const validation = useValidation();
const route = useRoute();
const loading = ref(false);
const otp = ref(route.query.otp ? route.query.otp : null);
if (!otp.value) {
  navigateTo("/login");
}
const schema = z
  .object({
    username: validation.name("username", true, 100),
    first_name: validation.name("first_name", true, 100),
    last_name: validation.name("last_name", true, 100),
    password: validation.passwordPolicy,
    confirmpassword: z.string("Password must be confirmed"),
  })
  .refine((data) => data.password === data.confirmpassword, {
    message: "Passwords don't match",
    path: ["confirmpassword"],
  });

function submit(event: object) {
  loading.value = true;
  api
    .create("", {
      username: event.data.username,
      first_name: event.data.first_name,
      last_name: event.data.last_name,
      password: event.data.password,
      otp: otp.value,
    })
    .then(() => {
      navigateTo("/login");
      loading.value = false;
    })
    .catch(() => {
      loading.value = false;
    });
}
</script>

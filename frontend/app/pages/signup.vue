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
        name: 'firstname',
        type: 'text',
        label: 'First name',
        placeholder: 'Enter your first name',
        required: true,
        size: 'xl',
      },
      {
        name: 'lastname',
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
    @submit="onSubmit"
  />
</template>

<script setup lang="ts">
import * as z from "zod";

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
    username: z.string("Username is required"),
    firstname: z.string("First name is required"),
    lastname: z.string("Last name is required"),
    password: validation.passwordPolicy,
    confirmpassword: z.string("Password must be confirmed"),
  })
  .refine((data) => data.password === data.confirmpassword, {
    message: "Passwords don't match",
    path: ["confirmpassword"],
  });

function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading.value = true;
  api
    .create("", {
      username: payload.data.username,
      first_name: payload.data.firstname,
      last_name: payload.data.lastname,
      password: payload.data.password,
      otp: otp,
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

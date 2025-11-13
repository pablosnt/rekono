<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md" variant="ghost">
      <UAuthForm
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
            label: 'Password',
            type: 'password',
            placeholder: 'Repeat your password',
            required: true,
            size: 'xl',
          },
        ]"
        :validate-on="['input', 'change']"
        :submit="{ label: 'Sign up', autoFocus: true, size: 'xl' }"
        :loading="loading"
        loading-auto
        @submit="onSubmit"
      >
        <template #leading>
          <div class="flex flex-col items-center justify-center mb-3 mt-1">
            <UColorModeImage
                light="/favicon.ico"
                dark="/favicon.ico"
                :width="100"
                :height="100"
            />
          </div>
        </template>
      </UAuthForm>
    </UPageCard>
  </div>
</template>

<script setup lang="ts">
import * as z from "zod";

const api = useApi("/api/security/signup/", false);
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
    password: z
      .string("Password is required")
      .min(12, "Must be at least 12 characters")
      .refine((password) => /[a-z]/.test(password), {
        message: "Must be at least one lowercase letter",
      })
      .refine((password) => /[A-Z]/.test(password), {
        message: "Must be at least one uppercase letter",
      })

      .refine((password) => /[0-9]/.test(password), {
        message: "Must be at least one digit",
      })
      .refine((password) => /\W/.test(password), {
        message: "Must be at least one symbol",
      }),
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

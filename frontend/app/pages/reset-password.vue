<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md" variant="ghost">
      <UAuthForm
        :schema="schema"
        title="Reset Password"
        :description="description"
        :fields="fields"
        :validate-on="['input', 'change']"
        :submit="{ label: 'Reset password', autoFocus: true, size: 'xl' }"
        :loading="loading"
        loading-auto
        @submit="onSubmit"
      >
        <template #leading>
          <div class="flex flex-col items-center justify-center mb-3 mt-3">
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

const api = useApi("/api/users/reset-password/", false);
const route = useRoute();
const toast = useToast();

const loading = ref(false);
const otp = ref(route.query.otp ? route.query.otp : null);
let fields = [
  {
    name: "email",
    type: "text",
    label: "Email",
    placeholder: "Enter your email",
    required: true,
    size: "xl",
    autofocus: true,
  },
];
let schema = z.object({ email: z.email("Valid email is required") });
let description = ref("Enter your user account's email and we will send you a password reset link")
if (otp.value) {
  fields = [
    {
      name: "password",
      label: "Password",
      type: "password",
      placeholder: "Enter your password",
      required: true,
      size: "xl",
      autofocus: true,
    },
  ];
  schema = z.object({
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
  });
  description.value = "Define the new password to access your user account"
}

function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading.value = true;
  if (otp.value) {
    api
      .update("", { password: payload.data.password, otp: otp.value })
      .then(() => {
        loading.value = false;
        navigateTo("/login");
      })
      .catch(() => {
        loading.value = false;
      });
  } else {
    api
      .create("", { email: payload.data.email })
      .then(() => {
        loading.value = false;
        toast.add({
          description:
            "Password reset requested. Use the link sent to your email",
          color: "success",
        });
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

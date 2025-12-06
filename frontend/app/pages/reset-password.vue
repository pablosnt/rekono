<template>
  <PublicForm
    :schema="schema"
    title="Reset Password"
    :description="description"
    :fields="fields"
    :submit="{ label: 'Reset password', autoFocus: true, size: 'xl' }"
    :loading="loading"
    @submit="onSubmit"
  />
</template>

<script setup lang="ts">
import * as z from "zod";

definePageMeta({ layout: "public" });
const api = useApi("/api/users/reset-password/", false);
const validation = useValidation();
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
const description = ref(
  "Enter your user account's email and we will send you a password reset link",
);
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
    {
      name: "confirmpassword",
      label: "Confirm password",
      type: "password",
      placeholder: "Repeat your password",
      required: true,
      size: "xl",
    },
  ];
  schema = z
    .object({
      password: validation.passwordPolicy,
      confirmpassword: z.string("Password must be confirmed"),
    })
    .refine((data) => data.password === data.confirmpassword, {
      message: "Passwords don't match",
      path: ["confirmpassword"],
    });
  description.value = "Define the new password to access your user account";
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
          title: "Password reset requested",
          description:
            "Use the link sent to your email to define your new password",
          color: "success",
        });
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

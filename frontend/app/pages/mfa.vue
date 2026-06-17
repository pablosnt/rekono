<template>
  <PublicForm
    :schema="schema"
    title="Multi-Factor Authentication"
    :fields="fields"
    :validate-on="['blur', 'submit']"
    :submit="{ label: 'Sign in', autoFocus: true, size: 'xl' }"
    :loading="loading"
    @submit="submit"
  >
    <template #after-form>
      <div class="mt-5 flex justify-center items-center">
        <UButton
          :label="
            method === 'app' ? 'MFA via email' : 'MFA via authenticator app'
          "
          color="neutral"
          variant="ghost"
          class="text-muted"
          @click="handleMethodSwitch()"
        />
      </div>
    </template>
  </PublicForm>
</template>

<script setup lang="ts">
import * as z from "zod";
import { useUserStore } from "~/store/user";

const userStore = useUserStore();
const validation = useValidation();
const toast = useToast();
const api = useApi("/api/security/mfa/");
const loading = ref(false);
const fields = ref([]);
const schema = ref(z.object({}));
const method = ref("email");
handleMethodSwitch();

function handleMethodSwitch() {
  method.value = method.value === "app" ? "email" : "app";
  if (method.value === "email") {
    api.create("email/");
    fields.value = [
      {
        name: "mfaEmail",
        type: "password",
        label: "OTP",
        length: 128,
        size: "xl",
        required: true,
        icon: "i-lucide-key",
      },
    ];
    schema.value = z.object({
      mfaEmail: validation.secret("mfaEmail", true, 128),
    });
  } else {
    fields.value = [
      {
        name: "mfaApp",
        type: "otp",
        label: "OTP",
        length: 6,
        size: "xl",
        required: true,
      },
    ];
    schema.value = z.object({
      mfaApp: z.array(z.string()).length(6, "OTP must be exactly 6 digits"),
    });
  }
}

function submit(event: object) {
  loading.value = true;
  api
    .create("", {
      mfa: event.data.mfaEmail
        ? event.data.mfaEmail
        : event.data.mfaApp.join(""),
    })
    .then((response) => {
      userStore.login(response);
      navigateTo("/");
    })
    .catch((error) => {
      if (error?.statusCode === 401) {
        toast.add({
          description: "Invalid MFA code. Please try again.",
          color: "error",
        });
      }
    })
    .finally(() => {
      loading.value = false;
    });
}

onMounted(() => {
  if (!userStore.is_partial_authenticated) {
    return navigateTo("/login");
  }
});
</script>

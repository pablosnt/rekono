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
const api = useApi("/api/security/mfa/");
const loading = ref(false);
const fields = ref([]);
let schema = z.object({});
const method = ref("email");
handleMethodSwitch();

async function handleMethodSwitch() {
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
    schema = z.object({
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
    schema = z.object({
      mfaApp: z.array(z.string()).length(6, "OTP must be exactly 6 digits"),
    });
  }
}

function submit(event: object) {
  loading.value = true;
  try {
    api
      .create("", {
        mfa: event.data.mfaEmail
          ? event.data.mfaEmail
          : event.data.mfaApp.join(""),
      })
      .then((response) => {
        userStore.login(response);
        navigateTo("/");
      });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (!userStore.is_partial_authenticated) {
    return navigateTo("/login");
  }
});
</script>

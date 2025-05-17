<template>
  <v-form v-model="valid" @submit.prevent="newOtp()">
    <v-otp-input
      v-if="app"
      v-model="mfa"
      class="mb-3"
      variant="outlined"
      autofocus
      :loading="loading ? 'red' : false"
      focus-all
      validate-on="blur"
      :rules="[
        (o) => !!o || 'Code is required',
        (o) => validate.mfa.test(o) || 'Invalid code',
      ]"
      @update:model-value="mfa && mfa.length === 6 ? newOtp() : null"
    />
    <v-text-field
      v-if="!app"
      v-model="mfa"
      class="ma-3"
      density="comfortable"
      label="Token"
      prepend-inner-icon="mdi-key"
      variant="outlined"
      autofocus
      validate-on="input"
      :rules="[
        (o) => !!o || 'Token is required',
        (o) => o.length === 128 || 'Invalid token',
      ]"
      @update:model-value="mfa && mfa.length === 128 ? newOtp() : null"
    />
    <div
      v-if="allowEmail && ((smtp && smtp.is_available) || user.user == null)"
      class="text-center"
    >
      <v-btn
        variant="text"
        :disabled="loading"
        @click.prevent="
          app = !app;
          $emit('app', app);
          mfa = null;
          !app ? api.create(token !== null ? { token: token } : {}) : null;
        "
        >Use {{ app ? "email" : "app" }} instead</v-btn
      >
    </div>
  </v-form>
</template>

<script setup lang="ts">
defineProps({
  allowEmail: { type: Boolean, required: false, default: false },
  loading: { type: Boolean, required: false, default: false },
});
const emit = defineEmits(["newOtp", "app"]);
const user = userStore();
const validate = ref(useValidation());
const app = ref(true);
const mfa = ref(undefined);
const valid = ref(true);
const tokens = useTokens();
const token = ref(tokens.get().mfa);
const api = ref(useApi("/api/security/mfa/email/", token.value === null));
const smtp = ref(null);
if (user.user) {
  useApi("/api/smtp/", true)
    .get(1)
    .then((response) => (smtp.value = response));
}

function newOtp(): void {
  if (valid.value) {
    emit("newOtp", mfa.value);
  }
}

function clearOtp(): void {
  mfa.value = null;
}

defineExpose({ clearOtp });
</script>

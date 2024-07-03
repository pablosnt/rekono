<template>
  <v-form v-model="valid" @submit.prevent="newOtp()">
    <v-otp-input
      v-if="app"
      v-model="mfa"
      variant="solo"
      autofocus
      validate-on="blur"
      :rules="[
        (o) => !!o || 'OTP is required',
        (o) => validate.mfa.test(o) || 'Invalid OTP',
      ]"
      @update:model-value="
        autoTrigger && mfa && mfa.length === 6 ? newOtp() : null
      "
    />

    <v-text-field
      v-if="!app"
      v-model="mfa"
      class="mt-5"
      density="compact"
      label="OTP"
      prepend-inner-icon="mdi-key"
      variant="outlined"
      autofocus
      validate-on="input"
      :rules="[
        (o) => !!o || 'OTP is required',
        (o) => o.length === 128 || 'Invalid OTP',
      ]"
      @update:model-value="
        autoTrigger && mfa && mfa.length === 128 ? newOtp() : null
      "
    />

    <slot name="buttons" />

    <div v-if="allowEmail" class="text-center">
      <v-btn
        variant="text"
        :disabled="loading"
        @click.prevent="
          app = !app;
          mfa = null;
          !app
            ? emailApi.create(token.value !== null ? { token: token } : {})
            : null;
        "
        >Use {{ app ? "email" : "app" }} instead</v-btn
      >
    </div>
  </v-form>
</template>

<script setup lang="ts">
defineProps({
  allowEmail: {
    type: Boolean,
    required: false,
    default: false,
  },
  loading: {
    type: Boolean,
    required: false,
    default: false,
  },
  autoTrigger: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const emit = defineEmits(["loadData"]);
const validate = ref(useValidation());
const app = ref(true);
const mfa = ref(null);
const valid = ref(true);
const tokens = useTokens();
const token = ref(tokens.get().mfa);
const emailApi = ref(useApi("/api/security/mfa/email/", token.value === null));

function newOtp() {
  if (valid.value) {
    emit("newOtp", mfa.value);
  }
}

function clearOtp() {
  mfa.value = null;
}

defineExpose({ clearOtp });
</script>

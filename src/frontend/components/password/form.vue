<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-text-field
      v-model="password"
      class="mb-3"
      :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
      :type="visible ? 'text' : 'password'"
      density="compact"
      label="Password"
      :prepend-inner-icon="icon"
      variant="outlined"
      :rules="[
        (p) => !!p || 'Password is required',
        (p) =>
          validate.password(p) ||
          'Password must contain one uppercase, lowercase, digit and symbol',
      ]"
      validate-on="blur"
      @click:append-inner="visible = !visible"
    />

    <v-text-field
      v-model="passwordConfirmation"
      class="mb-2"
      :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
      :type="visible ? 'text' : 'password'"
      density="compact"
      label="Confirm password"
      :prepend-inner-icon="icon"
      variant="outlined"
      :rules="[
        (p) => !!p || 'Password confirmation is required',
        (p) => p === password || 'Paswords do not match',
      ]"
      validate-on="blur"
      @click:append-inner="visible = !visible"
    />

    <v-card-actions class="justify-center">
      <UtilsSubmit :text="submitText" :disabled="loading" />
    </v-card-actions>
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  submitText: String,
  icon: {
    type: String,
    required: false,
    default: "mdi-lock",
  },
  otp: {
    type: String,
    required: false,
    default: null,
  },
  oldPassword: {
    type: String,
    required: false,
    default: null,
  },
  loading: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const emit = defineEmits(["loading", "error", "completed"]);
const validate = ref(useValidation());
const valid = ref(true);
const visible = ref(false);
const password = ref(null);
const passwordConfirmation = ref(null);

function submit(): void {
  if (valid.value && (props.otp || props.oldPassword)) {
    emit("loading", true);
    const body = { password: password.value };
    if (props.otp) {
      body.otp = props.otp;
    } else if (props.oldPassword) {
      body.old_password = props.oldPassword;
    }
    props.api
      .update(body)
      .then((response) => {
        emit("loading", false);
        emit("completed", response);
      })
      .catch((error) => {
        emit("loading", false);
        emit("error", error);
      });
  }
}
</script>

<template>
  <v-form
    v-model="valid"
    @submit.prevent="
      $emit(
        'customSubmit',
        valid &&
          model &&
          passwordConfirmation &&
          model === passwordConfirmation,
      )
    "
  >
    <slot name="prepend" />
    <v-text-field
      v-model="model"
      class="mb-2"
      :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
      :type="visible ? 'text' : 'password'"
      density="comfortable"
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
      :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
      :type="visible ? 'text' : 'password'"
      density="comfortable"
      label="Confirm password"
      :prepend-inner-icon="icon"
      variant="outlined"
      :rules="[
        (p) => !!p || 'Password confirmation is required',
        (p) => p === model || 'Paswords do not match',
      ]"
      validate-on="blur"
      @click:append-inner="visible = !visible"
    />
    <slot name="submit">
      <v-card-actions v-if="submitText !== null" class="justify-center">
        <UtilsSubmit
          :text="submitText"
          :disabled="
            submitDisabled ||
            !valid ||
            !model ||
            !passwordConfirmation ||
            model !== passwordConfirmation
          "
        />
      </v-card-actions>
    </slot>
  </v-form>
</template>

<script setup lang="ts">
defineProps({
  icon: { type: String, required: false, default: "mdi-lock" },
  submitText: { type: String, required: false, default: null },
  submitDisabled: { type: Boolean, required: false, default: false },
});
defineEmits(["customSubmit"]);
const model = defineModel();
const validate = ref(useValidation());
const valid = ref(true);
const visible = ref(false);
const passwordConfirmation = ref(null);
</script>

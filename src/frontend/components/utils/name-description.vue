<template>
  <v-form
    v-model="valid"
    @submit.prevent="
      valid ? $emit('submit', name.trim(), description.trim()) : null
    "
  >
    <v-text-field
      v-model="name"
      class="mt-2"
      label="Name"
      variant="outlined"
      :rules="[
        (n) => !!n || 'Name is required',
        (n) => validate.name.test(n) || 'Invalid name value',
      ]"
      validate-on="input"
      :disabled="disabled"
    />

    <v-textarea
      v-model="description"
      class="mt-2"
      label="Description"
      variant="outlined"
      :rules="[
        (d) => !!d || 'Description is required',
        (d) => validate.text.test(d) || 'Invalid description value',
      ]"
      validate-on="input"
      auto-grow
      max-rows="10"
      rows="3"
      :disabled="disabled"
    />

    <slot name="inputs" />

    <UtilsSubmit
      :text="!edit ? 'Create' : 'Update'"
      class="mt-4"
      :autofocus="false"
      :disabled="disabled"
    />
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  edit: {
    type: Object,
    required: false,
    default: null,
  },
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
});
defineEmits(["submit"]);
const validate = ref(useValidation());
const valid = ref(true);
const name = ref(props.edit ? props.edit.name : null);
const description = ref(props.edit ? props.edit.description : null);
</script>

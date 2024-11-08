<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <!-- todo: create general form with name and description ? -->
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

    <UtilsButtonSubmit
      text="Create"
      class="mt-4"
      :autofocus="false"
      :disabled="disabled"
    />
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
  extraData: {
    type: Object,
    required: false,
    default: null,
  },
});
const emit = defineEmits(["completed", "loading"]);
const validate = ref(useValidation());
const valid = ref(true);
const name = ref(null);
const description = ref(null);

function submit() {
  if (valid.value) {
    emit("loading", true);
    props.api
      .create(
        Object.assign(
          {},
          {
            name: name.value.trim(),
            description: description.value.trim(),
          },
          props.extraData !== null ? props.extraData : {},
        ),
      )
      .then((response) => {
        emit("completed", response);
        emit("loading", false);
      })
      .catch(() => {
        emit("loading", false);
      });
  }
}
</script>

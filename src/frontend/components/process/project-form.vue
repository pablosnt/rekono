<template>
  <v-form v-model="valid" @submit.prevent="submit()">
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
    />

    <TagInput
      class="mt-2"
      :value="tags"
      @new-values="(value) => (tags = value)"
    />

    <UtilsButtonSubmit
      :text="!edit ? 'Create' : 'Update'"
      class="mt-4"
      :autofocus="false"
    />
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  edit: Object,
});
const emit = defineEmits(["completed", "loading"]);
const validate = ref(useValidation());
const valid = ref(true);
const name = ref(props.edit ? props.edit.name : null);
const description = ref(props.edit ? props.edit.description : null);
const tags = ref(props.edit ? props.edit.tags : []);
function submit(): void {
  if (valid.value) {
    emit("loading", true);
    const request = props.edit ? props.api.update : props.api.create;
    request(
      {
        name: name.value.trim(),
        description: description.value.trim(),
        tags: tags.value,
      },
      props.edit?.id,
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

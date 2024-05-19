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
      validate-on="blur"
      density="comfortable"
    />

    <v-autocomplete
      v-model="type"
      auto-select-first
      class="mt-2"
      clearable
      hide-details
      density="comfortable"
      variant="outlined"
      label="Type"
      :items="enums.wordlists"
      prepend-inner-icon="mdi-routes"
      :rules="[(t) => !!t || 'Type is required']"
      validate-on="blur"
    />

    <v-file-input
      v-if="!edit"
      v-model="file"
      class="mt-7"
      clearable
      density="comfortable"
      variant="outlined"
      show-size
      label="File"
      prepend-inner-icon="$file"
      :prepend-icon="null"
      accept="text/plain"
      :rules="[
        (f) => !!f || 'File is required',
        (f) =>
          !f.length ||
          f[0].size <= maxSize * 1000000 ||
          `File size must be less than ${maxSize} MB`,
      ]"
      validate-on="blur"
    />

    <v-btn
      color="red"
      size="large"
      variant="tonal"
      :text="!edit ? 'Create' : 'Update'"
      type="submit"
      class="mt-5"
      block
    />
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  edit: Object,
});
const maxSize = ref(512 * 1000000);
useApi("/api/settings/", true, "Settings")
  .get(1)
  .then((data) => (maxSize.value = data.max_uploaded_file_mb));
const validate = ref(useValidation());
const emit = defineEmits(["completed", "loading"]);
const enums = ref(useEnums());
const valid = ref(true);
const name = ref(props.edit ? props.edit.name : null);
const type = ref(props.edit ? props.edit.type : null);
const file = ref(null);
function submit() {
  if (valid.value) {
    emit("loading", true);
    let request = null;
    let body = null;
    if (props.edit) {
      request = props.api.update;
      body = { name: name.value, type: type.value };
    } else {
      request = props.api.create;
      body = new FormData();
      body.append("name", name.value);
      body.append("type", type.value);
      body.append("file", file.value);
    }
    request(body, props.edit?.id)
      .then((data) => {
        emit("completed", data);
      })
      .catch(() => {
        emit("loading", false);
      });
  }
}
</script>

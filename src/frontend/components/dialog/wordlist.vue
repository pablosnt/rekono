<template>
  <DialogDefault
    :title="edit ? 'Edit Wordlist' : 'New Wordlist'"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <template #default>
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
          validate-on="input"
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
          validate-on="input"
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
  </DialogDefault>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  edit: Object,
});
const emit = defineEmits(["closeDialog", "completed"]);
const enums = ref(useEnums());
const validate = ref(useValidation());
const valid = ref(true);
const loading = ref(false);

const maxSize = ref(512 * 1000000);
useApi("/api/settings/", true, "Settings")
  .get(1)
  .then((response) => (maxSize.value = response.max_uploaded_file_mb));

const name = ref(props.edit ? props.edit.name : null);
const type = ref(props.edit ? props.edit.type : null);
const file = ref(null);

function submit() {
  if (valid.value) {
    loading.value = true;
    let request = null;
    let body = null;
    if (props.edit) {
      request = props.api.update;
      body = { name: name.value.trim(), type: type.value };
    } else {
      request = props.api.create;
      body = new FormData();
      body.append("name", name.value.trim());
      body.append("type", type.value);
      body.append("file", file.value);
    }
    request(body, props.edit?.id)
      .then((response) => {
        emit("completed", response);
        loading.value = false;
        emit("closeDialog");
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

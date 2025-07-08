<template>
  <BaseDialog
    :title="edit ? 'Edit Wordlist' : 'New Wordlist'"
    :loading="loading"
    @close-dialog="$emit('closeDialog')"
  >
    <v-container fluid>
      <v-form v-model="valid" @submit.prevent="submit()">
        <v-row class="mb-3">
          <v-text-field
            v-model="name"
            label="Name"
            variant="outlined"
            :rules="[
              (n) => !!n || 'Name is required',
              (n) => validate.name.test(n) || 'Invalid name value',
            ]"
            validate-on="input"
            density="comfortable"
            @update:model-value="disabled = false"
          />
        </v-row>
        <v-row class="mb-7">
          <BaseAutocomplete
            v-model="type"
            hide-details
            density="comfortable"
            variant="outlined"
            label="Type"
            :definition="enums.wordlists"
            icon="mdi-routes"
            @update:model-value="disabled = false"
          />
        </v-row>
        <v-row>
          <v-file-input
            v-if="!edit"
            v-model="file"
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
            @update:model-value="disabled = false"
        /></v-row>
        <v-row>
          <UtilsSubmit
            :autofocus="false"
            :text="!edit ? 'Create' : 'Update'"
            :disabled="disabled || !valid || !name || (!file && !edit)"
            class="mt-5"
          />
        </v-row>
      </v-form>
    </v-container>
  </BaseDialog>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  edit: { type: Object, required: false, default: null },
});
const emit = defineEmits(["closeDialog", "completed"]);
const enums = useEnums();
const validate = ref(useValidation());
const valid = ref(true);
const loading = ref(false);
const disabled = ref(true);
const name = ref(props.edit ? props.edit.name : null);
const type = ref(props.edit ? props.edit.type : "Endpoint");
const file = ref(null);
const maxSize = ref(512 * 1000000);
useApi("/api/settings/", true, "Settings")
  .get(1)
  .then((response) => (maxSize.value = response.max_uploaded_file_mb));

function submit(): void {
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
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

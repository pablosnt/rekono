<template>
  <Dialog
    title="New Technology"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-conatiner fluid>
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

        <v-text-field
          v-model="version"
          class="mt-2"
          label="Version"
          variant="outlined"
          :rules="[
            (v) => !v || validate.name.test(v) || 'Invalid version value',
          ]"
          validate-on="input"
        />
        <UtilsButtonSubmit text="Create" />
      </v-conatiner>
    </v-form>
  </Dialog>
</template>

<script setup lang="ts">
const props = defineProps({ api: Object });
const emit = defineEmits(["closeDialog", "completed"]);
const validate = useValidation();
const route = useRoute();
const name = ref(null);
const version = ref(null);
const valid = ref(true);
const loading = ref(false);

function submit(): void {
  if (valid.value) {
    loading.value = true;
    props.api
      .create({
        target: route.params.target_id,
        name: name.value.trim(),
        version: version.value.trim(),
      })
      .then((response) => {
        loading.value = false;
        emit("completed", response);
      })
      .catch(() => (loading.value = false));
  }
}
</script>

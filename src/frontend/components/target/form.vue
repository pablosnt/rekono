<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <BaseTagInput
      class="mt-5"
      :value="targets"
      label="Targets"
      icon="mdi-target"
      :validate="validate.target"
      @new-value="(value) => (target = value)"
      @new-values="(value) => (targets = value)"
    />
    <BaseButtonSubmit text="Create" :disabled="loading" />
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  projectId: Number,
  api: {
    type: Object,
    required: false,
    default: useApi("/api/targets/", true, "Target"),
  },
});
const emit = defineEmits(["completed", "loading"]);
const validate = useValidation();
const valid = ref(true);
const loading = ref(false);
const target = ref(null);
const targets = ref([]);

function submit(): void {
  const targetsToCreate =
    target.value === null
      ? targets.value
      : targets.value.concat([target.value]);
  if (targetsToCreate.length > 0 && valid.value) {
    emit("loading", true);
    loading.value = true;
    const body = { project: props.projectId };
    let success = 0;
    let errors = 0;
    for (const target of targetsToCreate) {
      body.target = target;
      props.api
        .create(body)
        .then(() => {
          success++;
          if (success + errors === targetsToCreate.length) {
            emit("completed");
            emit("loading", false);
            loading.value = false;
          }
        })
        .catch(() => {
          errors++;
          if (success + errors === targetsToCreate.length) {
            if (success > 0) {
              emit("completed");
            }
            emit("loading", false);
            loading.value = false;
          }
        });
    }
  }
}
</script>

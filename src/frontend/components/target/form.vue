<template>
  <v-form @submit.prevent="submit()">
    <BaseTagInput
      class="mt-5"
      :value="targets"
      label="Targets"
      icon="mdi-target"
      :validate="validate.target"
      @input-value="
        (value) => {
          target = value;
          $emit('target', value);
        }
      "
      @new-values="
        (value) => {
          targets = value;
          $emit('targets', value);
        }
      "
    />
    <slot name="submit">
      <UtilsSubmit
        text="Create"
        :disabled="loading || (targets.length === 0 && target === null)"
      />
    </slot>
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
const emit = defineEmits(["completed", "loading", "target", "targets"]);
const validate = useValidation();
const loading = ref(false);
const target = ref(null);
const targets = ref([]);

function submit(): void {
  const targetsToCreate =
    target.value === null
      ? targets.value
      : targets.value.concat([target.value]);
  if (targetsToCreate.length > 0) {
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

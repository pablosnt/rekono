<template>
  <v-form @submit.prevent="submit()">
    <BaseTagInput
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
      <UtilsPercentage
        v-if="loading && targetsToCreate.length > 1"
        :total="targetsToCreate.length"
        :progress="success + errors"
      />
      <UtilsSubmit
        v-if="!loading || targetsToCreate.length < 2"
        text="Create"
        :disabled="targets.length === 0 && target === null"
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
const targetsToCreate = ref([]);
const success = ref(0);
const errors = ref(0);

function submit(): void {
  targetsToCreate.value =
    target.value === null
      ? targets.value
      : targets.value.concat([target.value]);
  if (targetsToCreate.value.length > 0) {
    emit("loading", true);
    loading.value = true;
    const body = { project: props.projectId };
    success.value = 0;
    errors.value = 0;
    for (const target of targetsToCreate.value) {
      body.target = target;
      props.api
        .create(body)
        .then(() => {
          success.value++;
          if (success.value + errors.value === targetsToCreate.value.length) {
            emit("completed");
            emit("loading", false);
            loading.value = false;
          }
        })
        .catch(() => {
          errors.value++;
          if (success.value + errors.value === targetsToCreate.value.length) {
            if (success.value > 0) {
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

<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <InputTag
      class="mt-5"
      :value="targets"
      label="Targets"
      icon="mdi-target"
      :validate="validate.target"
      @new-value="(value) => (targets = value)"
    />
    <ButtonSubmit text="Create" :disabled="loading" />
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  project: {
    type: Object,
    required: false,
    default: null,
  },
  projectId: {
    type: Number,
    required: false,
    default: null,
  },
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
const targets = ref([]);

function submit() {
  if (targets.value.length > 0 && valid.value) {
    emit("loading", true);
    loading.value = true;
    const body = { project: props.project.id };
    let success = 0;
    let errors = 0;
    for (let i = 0; i < targets.value.length; i++) {
      body.target = targets.value[i];
      props.api
        .create(body)
        .then(() => {
          success++;
          if (success + errors === targets.value.length) {
            emit("completed");
            emit("loading", false);
            loading.value = false;
          }
        })
        .catch(() => {
          errors++;
          if (success + errors === targets.value.length) {
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

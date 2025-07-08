<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="space-around" dense>
        <v-col cols="5">
          <v-number-input
            v-model="port"
            class="mt-2"
            control-variant="split"
            label="Port"
            inset
            variant="outlined"
            :max="65535"
            :min="1"
            :prepend-icon="utils.getIcon(port)"
            @update:model-value="disabled = false"
          />
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="path"
            class="mt-2"
            label="Path"
            variant="outlined"
            :rules="[
              (p) => !p || validate.path.test(p) || 'Invalid path value',
            ]"
            validate-on="input"
          >
            <template #prepend>
              <p><strong>/</strong></p>
            </template>
          </v-text-field>
        </v-col>
      </v-row>
      <UtilsSubmit class="mt-4" :disabled="disabled" text="Create" />
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: {
    type: Object,
    required: false,
    default: useApi("/api/target-ports/", true, "Target port"),
  },
});
const emit = defineEmits(["completed", "loading"]);
const validate = useValidation();
const route = useRoute();
const utils = usePorts();
const valid = ref(true);
const disabled = ref(true);
const port = ref(null);
const path = ref(null);

function submit(): void {
  if (valid.value) {
    if (path.value && !path.value.startsWith("/")) {
      path.value = "/".concat(path.value);
    }
    emit("loading", true);
    props.api
      .create({
        port: port.value,
        path: path.value,
        target: route.params.target_id,
      })
      .then((response) => {
        emit("loading", false);
        emit("completed", response);
        disabled.value = true;
      })
      .catch(() => emit("loading", false));
  }
}
</script>

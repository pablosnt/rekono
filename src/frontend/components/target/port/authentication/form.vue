<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="center" dense>
        <v-col cols="11">
          <v-autocomplete
            v-model="type"
            auto-select-first
            density="comfortable"
            variant="outlined"
            label="Type"
            :items="enums.authentications"
            clearable
            validate-on="input"
            :rules="[(t) => !!t || 'Type is required']"
            prepend-inner-icon="mdi-key-chain"
          />
        </v-col>
      </v-row>
      <v-row justify="center" dense>
        <v-col cols="11">
          <v-text-field
            v-model="name"
            class="mt-2"
            label="Name"
            variant="outlined"
            :rules="[
              (n) => !n || validate.name.test(n) || 'Invalid name value',
            ]"
            validate-on="input"
            prepend-inner-icon="mdi-shield-account"
            :disabled="type === 'None'"
          />
        </v-col>
      </v-row>
      <v-row justify="center" dense>
        <v-col cols="11">
          <v-text-field
            v-model="secret"
            class="mt-2"
            label="Secret"
            variant="outlined"
            :rules="[
              (s) => !!s || 'Secret is required',
              (s) => validate.secret.test(s) || 'Invalid secret value',
            ]"
            validate-on="input"
            prepend-inner-icon="mdi-shield-key"
            :disabled="type === 'None'"
            @update:model-value="disabled = false"
          />
        </v-col>
      </v-row>
      <UtilsSubmit
        class="mt-4"
        :disabled="disabled && type !== 'None'"
        text="Save"
      />
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: {
    type: Object,
    required: false,
    default: useApi("/api/authentications/", true, "Authentication"),
  },
  targetPort: Number,
});
const emit = defineEmits(["completed", "loading"]);
const validate = useValidation();
const enums = useEnums();
const valid = ref(true);
const disabled = ref(true);
const name = ref(null);
const secret = ref(null);
const type = ref("None");

function submit(): void {
  if (type.value === "None") {
    emit("completed");
  }
  if (valid.value) {
    emit("loading", true);
    props.api
      .create({
        target_port: props.targetPort,
        name: name.value,
        secret: secret.value,
        type: type.value,
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

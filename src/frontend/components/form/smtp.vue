<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="space-around" dense>
        <v-col cols="6">
          <v-text-field
            v-model="smtp.host"
            prepend-icon="mdi-server"
            label="SMTP Host"
            variant="outlined"
            hide-details
            single-line
            :rules="[
              (h) => !!h || 'Host is required',
              (h) => validate.target.test(h.trim()) || 'Invalid host value',
            ]"
            validate-on="input"
            clearable
            @update:model-value="disabled = smtp.host === null"
          />
        </v-col>
        <v-col cols="4">
          <VNumberInput
            v-model="smtp.port"
            hide-details
            hide-spin-buttons
            single-line
            clearable
            label="Port"
            inset
            variant="outlined"
            :max="65535"
            :min="1"
            :rules="[(p) => !!p || 'Port is required']"
            validate-on="input"
            @update:model-value="disabled = smtp.port === null"
          />
        </v-col>
        <v-col cols="2">
          <v-checkbox
            v-model="smtp.tls"
            label="TLS"
            hide-details
            @update:model-value="disabled = false"
          />
        </v-col>
      </v-row>
      <v-row class="mt-6" dense>
        <v-col cols="10">
          <v-text-field
            v-model="smtp.username"
            density="compact"
            label="Username"
            prepend-icon="mdi-account"
            variant="outlined"
            :rules="[
              (u) =>
                !u || validate.name.test(u.trim()) || 'Username is invalid',
            ]"
            validate-on="input"
            clearable
            @update:model-value="disabled = false"
          />
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="10">
          <v-text-field
            v-model="smtp.password"
            type="password"
            density="compact"
            label="Password"
            prepend-icon="mdi-lock"
            variant="outlined"
            :rules="[
              (p) =>
                !p || validate.secret.test(p.trim()) || 'Password is invalid',
            ]"
            validate-on="input"
            clearable
            @update:model-value="disabled = false"
          />
        </v-col>
      </v-row>
      <v-btn
        color="red"
        size="large"
        variant="tonal"
        text="Save"
        type="submit"
        class="mt-5"
        block
        autofocus
        :disabled="disabled"
      />
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { VNumberInput } from "vuetify/labs/VNumberInput";
const props = defineProps({
  api: Object,
  data: Object,
});
const emit = defineEmits(["completed", "loading"]);
emit("loading", true);
const validate = ref(useValidation());
const valid = ref(true);
const disabled = ref(true);

const smtp = ref({
  host: null,
  port: null,
  tls: false,
  username: null,
  password: null,
});
watch(
  () => props.data,
  () => {
    emit("loading", false);
    smtp.value = props.data;
  },
);

function submit() {
  if (valid.value) {
    const data = {
      host: smtp.value.host,
      port: smtp.value.port,
      tls: smtp.value.tls,
      username: smtp.value.username,
    };
    if (smtp.value.password !== "*".repeat(smtp.value.password.length)) {
      data.password = smtp.value.password;
    }
    console.log(data);
    emit("loading", true);
    props.api.update(data, 1).then((data) => {
      emit("completed", data);
      emit("loading", false);
    });
  }
}
</script>

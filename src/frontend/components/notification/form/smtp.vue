<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="space-around" dense>
        <v-col cols="6">
          <v-text-field
            v-model="host"
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
            @update:model-value="disabled = host === null"
          />
        </v-col>
        <v-col cols="4">
          <VNumberInput
            v-model="port"
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
            @update:model-value="disabled = port === null"
          />
        </v-col>
        <v-col cols="2">
          <v-checkbox
            v-model="tls"
            label="TLS"
            hide-details
            @update:model-value="disabled = false"
          />
        </v-col>
      </v-row>
      <v-row class="mt-6" dense>
        <v-col cols="10">
          <v-text-field
            v-model="username"
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
            v-model="password"
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
      <UtilsSubmit text="Save" class="mt-5" :disabled="disabled" />
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
const validate = ref(useValidation());
const valid = ref(true);
const disabled = ref(true);
const host = ref(props.data ? props.data.host : null);
const port = ref(props.data ? props.data.port : null);
const tls = ref(props.data ? props.data.tls : false);
const username = ref(props.data ? props.data.username : null);
const password = ref(props.data ? props.data.password : null);

function submit(): void {
  if (valid.value) {
    emit("loading", true);
    props.api
      .update(
        {
          host: host.value.trim(),
          port: port.value,
          tls: tls.value,
          username: username.value.trim(),
          password:
            !password.value ||
            password.value !== "*".repeat(password.value.length)
              ? password.value !== null
                ? password.value
                : null
              : undefined,
        },
        1,
      )
      .then((response) => {
        emit("completed", response);
        emit("loading", false);
        disabled.value = true;
      });
  }
}
</script>

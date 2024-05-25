<template>
  <DialogIntegration
    :api="integrationApi"
    :integration="integration"
    :is-available="isAvailable"
    color="blue"
    :loading="loading"
    @close-dialog="$emit('closeDialog')"
  >
    <template #default>
      <v-form v-model="valid" @submit.prevent="submit()">
        <v-container fluid>
          <v-row justify="center" dense>
            <v-col cols="9">
              <v-text-field
                v-model="server"
                prepend-icon="mdi-server"
                label="Defect-Dojo Server"
                placeholder="http(s)://<host>:<port>"
                variant="outlined"
                hint="The API endpoints '/api/...' will be appended to the server address"
                :rules="[
                  (s) =>
                    !s ||
                    validate.target.test(s.trim()) ||
                    'Invalid server value',
                ]"
                validate-on="input"
                clearable
                @update:model-value="disabled = false"
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
          <v-row justify="center" dense>
            <v-col cols="11">
              <v-text-field
                v-model="apiToken"
                type="password"
                label="Defect-Dojo API key"
                prepend-icon="mdi-key"
                variant="outlined"
                :rules="[
                  (k) =>
                    !k || validate.secret.test(k.trim()) || 'Invalid API key',
                ]"
                validate-on="input"
                clearable
                @update:model-value="disabled = false"
              />
            </v-col>
          </v-row>
          <v-row justify="center" dense>
            <v-col cols="3">
              <v-text-field
                v-model="tag"
                prepend-icon="mdi-tag"
                label="Tag"
                variant="outlined"
                hide-details
                :rules="[
                  (t) => !!t || 'Tag is required',
                  (t) => validate.name.test(t.trim()) || 'Invalid tag value',
                ]"
                validate-on="input"
                clearable
                @update:model-value="disabled = false"
              />
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="testType"
                label="Test Type"
                variant="outlined"
                hide-details
                :rules="[
                  (t) => !!t || 'Test type is required',
                  (t) =>
                    validate.name.test(t.trim()) || 'Invalid test type value',
                ]"
                validate-on="input"
                clearable
                @update:model-value="disabled = false"
              />
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="test"
                label="Test"
                variant="outlined"
                hide-details
                :rules="[
                  (t) => !!t || 'Test is required',
                  (t) => validate.name.test(t.trim()) || 'Invalid test value',
                ]"
                validate-on="input"
                clearable
                @update:model-value="disabled = false"
              />
            </v-col>
          </v-row>
        </v-container>
        <v-btn
          color="blue"
          size="large"
          variant="tonal"
          text="Save"
          type="submit"
          class="mt-5"
          :disabled="disabled"
          block
          autofocus
        />
      </v-form>
    </template>
  </DialogIntegration>
</template>

<script setup lang="ts">
defineProps({
  integrationApi: Object,
  integration: Object,
});
const emit = defineEmits(["closeDialog"]);
const api = useApi("/api/defect-dojo/settings/", true, "Defect-Dojo");
const valid = ref(true);
const validate = ref(useValidation());
const disabled = ref(true);
const loading = ref(true);

const isAvailable = ref(false);
const server = ref(null);
const apiToken = ref(null);
const tls = ref(false);
const tag = ref(null);
const testType = ref(null);
const test = ref(null);

api.get(1).then((response) => {
  loadData(response);
  loading.value = false;
});

function loadData(data) {
  isAvailable.value = data.is_available;
  server.value = data.server;
  apiToken.value = data.api_token;
  tls.value = data.tls_validation;
  tag.value = data.tag;
  testType.value = data.test_type;
  test.value = data.test;
}

function submit() {
  if (valid.value) {
    loading.value = true;
    api
      .update(
        {
          server: server.value.trim(),
          api_token:
            !apiToken.value ||
            apiToken.value !== "*".repeat(apiToken.value.length)
              ? apiToken.value !== null
                ? apiToken.value.trim()
                : null
              : undefined,
          tls_validation: tls.value,
          tag: tag.value.trim(),
          test_type: testType.value.trim(),
          test: test.value.trim(),
        },
        1,
      )
      .then((response) => {
        loadData(response);
        loading.value = false;
        disabled.value = true;
        if (response.is_available) {
          emit("closeDialog");
        }
      });
  }
}
</script>

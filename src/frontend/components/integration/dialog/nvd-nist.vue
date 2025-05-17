<template>
  <IntegrationDialog
    :api="integrationApi"
    :integration="integration"
    :is-available="isAvailable"
    color="black-darken-3"
    :loading="loading"
    @close-dialog="$emit('closeDialog')"
  >
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-container fluid
        ><v-row v-if="!isAvailable" class="mb-5" justify="center" dense>
          <v-alert
            color="info"
            icon="$info"
            variant="tonal"
            class="text-center"
          >
            <template #text>
              <span class="font-weight-bold">This API key is not mandatory</span
              >. However, configuring one will increase their API's rate limit,
              so it can avoid some blocked requests.
              <v-btn
                class="pa-0 ml-0 text-none mb-1 font-weight-bold text-left"
                density="compact"
                text="Request yours here"
                target="_blank"
                href="https://nvd.nist.gov/developers/request-an-api-key"
                variant="plain"
              />
            </template>
          </v-alert>
        </v-row>
        <v-row class="mb-3" justify="center">
          <v-col cols="11">
            <v-text-field
              v-model="apiToken"
              type="password"
              label="NVD NIST API key"
              prepend-inner-icon="mdi-key"
              variant="outlined"
              :rules="[
                (k) =>
                  !k || validate.secret.test(k.trim()) || 'Invalid API key',
              ]"
              validate-on="input"
              clearable
              @update:model-value="disabled = false"
            />
            <UtilsSubmit
              color="black-darken-3"
              text="Save"
              :disabled="disabled"
              class="mt-5"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-form>
  </IntegrationDialog>
</template>

<script setup lang="ts">
defineProps({
  integrationApi: Object,
  integration: Object,
});
const emit = defineEmits(["closeDialog"]);
const api = useApi("/api/nvdnist/", true, "CVE Crowd");
const valid = ref(true);
const validate = ref(useValidation());
const disabled = ref(true);
const loading = ref(true);
const isAvailable = ref(false);
const apiToken = ref(null);

api.get(1).then((response) => {
  loadData(response);
  loading.value = false;
});

function loadData(data: object): void {
  isAvailable.value = data.is_available;
  apiToken.value = data.api_token;
}

function submit(): void {
  if (valid.value) {
    loading.value = true;
    api
      .update(
        {
          api_token:
            !apiToken.value ||
            apiToken.value !== "*".repeat(apiToken.value.length)
              ? apiToken.value !== null
                ? apiToken.value.trim()
                : null
              : undefined,
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

<template>
  <MenuAdministration>
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-container fluid>
        <v-row justify="space-around" dense>
          <v-col cols="5">
            <BaseSection
              class="mt-5"
              title="Vulnerability Management"
              icon="mdi-bug"
            >
              <v-switch
                v-model="settings.auto_fix_findings"
                color="red"
                label="Mark findings as fixed automatically when they are no longer detected"
                @update:model-value="disabled = false"
              />
            </BaseSection>
          </v-col>
          <v-col cols="4">
            <BaseSection class="mt-5" title="Security" icon="mdi-lock">
              <div class="text-center mr-10 ml-10">
                <VNumberInput
                  v-model="settings.max_uploaded_file_mb"
                  control-variant="split"
                  label="Max Upload File Size (MB)"
                  inset
                  variant="outlined"
                  :max="3072"
                  :min="128"
                  @update:model-value="disabled = false"
                />
              </div>
            </BaseSection>
          </v-col>
        </v-row>
        <v-row justify="center" dense>
          <v-col cols="10">
            <BaseSection
              class="mt-5"
              title="Proxy"
              subtitle="Proxies will be used during tool executions by configuring the following environment variables"
              icon="mdi-plus-network"
            >
              <v-container fluid>
                <v-row justify="space-around" dense>
                  <v-col
                    v-for="name in [
                      'all_proxy',
                      'no_proxy',
                      'http_proxy',
                      'https_proxy',
                      'ftp_proxy',
                    ]"
                    :key="name"
                    cols="5"
                  >
                    <v-text-field
                      :v-model="settings[name]"
                      class="mt-2"
                      variant="outlined"
                      :label="name.toUpperCase()"
                      :rules="[
                        (p) =>
                          !p ||
                          validate.targetRegex.test(p.trim()) ||
                          'Invalid proxy value',
                      ]"
                      validate-on="input"
                      @update:model-value="disabled = false"
                    />
                  </v-col>
                </v-row>
              </v-container>
            </BaseSection>
          </v-col>
        </v-row>
        <v-fab
          color="red"
          icon
          absolute
          size="64"
          :loading="loading"
          :disabled="disabled"
          @click="submit()"
        >
          <v-icon icon="mdi-floppy" />
          <v-tooltip activator="parent" text="Save" />
        </v-fab>
      </v-container>
    </v-form>
  </MenuAdministration>
</template>

<script setup lang="ts">
import { VNumberInput } from "vuetify/labs/VNumberInput";
definePageMeta({ layout: false });
const validate = useValidation();
const valid = ref(true);
const api = useApi("/api/settings/", true, "Configuration");
const disabled = ref(false);
const loading = ref(false);
const settings = ref({
  auto_fix_findings: true,
  max_uploaded_file_mb: 128,
  all_proxy: null,
  http_proxy: null,
  https_proxy: null,
  ftp_proxy: null,
  no_proxy: null,
});
api.get(1).then((response) => {
  settings.value = response;
  disabled.value = true;
});

function submit(): void {
  if (valid.value) {
    loading.value = true;
    api
      .update(settings.value, 1)
      .then((response) => {
        settings.value = response;
        disabled.value = true;
        loading.value = false;
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>

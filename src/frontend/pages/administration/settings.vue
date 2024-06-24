<template>
  <MenuAdministration>
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-container fluid>
        <v-row justify="center" dense>
          <v-col cols="5">
            <v-card variant="text" class="mt-5" width="100%">
              <template #title>
                <v-card-title class="text-h5">
                  <v-icon color="red" icon="mdi-bug" />
                  <span class="me-1" />
                  Vulnerability Management
                </v-card-title>
              </template>
              <template #text>
                <v-card-text>
                  <v-switch
                    v-model="settings.auto_fix_findings"
                    color="red"
                    label="Mark findings as fixed automatically when they are no longer detected by the same tool and configuration"
                    @update:model-value="disabled = false"
                  />
                </v-card-text>
              </template>
            </v-card>
          </v-col>
          <v-col cols="4">
            <v-card variant="text" class="mt-5" width="100%">
              <template #title>
                <v-card-title class="text-h5">
                  <v-icon color="red" icon="mdi-lock" />
                  <span class="me-1" />
                  Security
                </v-card-title>
              </template>
              <template #text>
                <v-card-text>
                  <v-container fluid>
                    <v-row justify="center" dense>
                      <v-col cols="8">
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
                      </v-col>
                    </v-row>
                  </v-container>
                </v-card-text>
              </template>
            </v-card>
          </v-col>
        </v-row>
        <v-row justify="center" dense>
          <v-col cols="9">
            <v-card variant="text" class="mt-5" width="100%">
              <template #title>
                <v-card-title class="text-h5">
                  <v-icon color="red" icon="mdi-plus-network" />
                  <span class="me-1" />
                  Proxy
                </v-card-title>
              </template>
              <template #text>
                <v-card-text>
                  <v-container fluid>
                    <v-row justify="space-around" dense>
                      <v-col cols="8">
                        <v-alert
                          color="info"
                          icon="$info"
                          variant="tonal"
                          text="Proxies only will be used during tool executions by configuring the following environment variables"
                        />
                      </v-col>
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
                          variant="underlined"
                          :label="name.toUpperCase()"
                          :rules="[
                            (p) =>
                              !p ||
                              validate.targetRegex.test(p.trim()) ||
                              'Invalid proxy value',
                          ]"
                          validate-on="input"
                          @update:model-value="disabled = false"
                        >
                          <template #prepend>
                            <p class="text-medium-emphasis">
                              export {{ name.toUpperCase() }} =
                            </p>
                          </template>
                          <template #prepend-inner> " </template>
                          <template #append-inner> " </template>
                        </v-text-field>
                      </v-col>
                    </v-row>
                  </v-container>
                </v-card-text>
              </template>
            </v-card>
          </v-col>
        </v-row>
        <v-fab
          color="red"
          icon
          class="position-fixed"
          location="bottom"
          size="64"
          :disabled="disabled"
          app
          @click="submit()"
        >
          <v-icon icon="mdi-tray-arrow-down" />
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

function submit() {
  if (valid.value) {
    api.update(settings.value, 1).then((response) => {
      settings.value = response;
      disabled.value = true;
    });
  }
}
</script>

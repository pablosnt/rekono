<template>
  <MenuAdministration>
    <v-container>
      <v-row>
        <v-card variant="text" class="mt-5" width="100%">
          <v-card-title class="text-h5">
            <v-icon color="red" icon="mdi-apps" />
            <span class="me-1" />
            Platforms
          </v-card-title>
          <v-container align-self="center" fluid>
            <v-row justify="space-around" dense>
              <v-col
                v-for="integration in integrations"
                :key="integration.id"
                class="d-flex justify-center align-center"
                cols="5"
              >
                <Integration
                  v-if="integration.id !== 1 && integration.id !== 4"
                  :api="iApi"
                  :integration="integration"
                />
                <v-dialog v-if="integration.id === 1 || integration.id === 4">
                  <template #activator="{ props: activatorProps }">
                    <Integration
                      :api="iApi"
                      :integration="integration"
                      hover
                      v-bind="activatorProps"
                    />
                  </template>
                  <template #default="{ isActive }">
                    <IntegrationDialogDefectDojo
                      v-if="integration.id === 1"
                      :integration-api="iApi"
                      :integration="integration"
                      @close-dialog="isActive.value = false"
                    />
                    <IntegrationDialogCveCrowd
                      v-if="integration.id === 4"
                      :integration-api="iApi"
                      :integration="integration"
                      @close-dialog="isActive.value = false"
                    />
                  </template>
                </v-dialog>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-row>
      <v-row>
        <v-card variant="text" class="mt-5">
          <template #title>
            <v-card-title class="text-h5">
              <v-icon color="red" icon="mdi-radar" />
              <span class="me-1" />
              Monitoring
            </v-card-title>
          </template>
          <template #text>
            <v-card-text>
              <v-container fluid>
                <v-row>
                  <v-alert
                    color="info"
                    icon="$info"
                    variant="tonal"
                    text="Some platforms like CVE Crowd, need to be used periodically to keep your findings up to date. Here you can configure the desired time lapse for the monitoring tasks"
                  />
                </v-row>
                <v-row class="mt-8" justify="space-around">
                  <v-col cols="5">
                    <VNumberInput
                      v-model="monitor.hour_span"
                      control-variant="split"
                      label="Hours"
                      inset
                      variant="outlined"
                      :max="168"
                      :min="24"
                      @update:model-value="save = true"
                    >
                      <template #append>
                        <BaseLink
                          icon="mdi-tray-arrow-down"
                          icon-color="green"
                          tooltip="Save"
                          hover
                          :disabled="!save"
                          @click="
                            mApi
                              .update({ hour_span: monitor.hour_span }, 1)
                              .then((response) => (monitor = response))
                          "
                        />
                      </template>
                    </VNumberInput>
                  </v-col>
                </v-row>
                <v-row
                  v-if="new Date(monitor.last_monitor).getFullYear() !== 1970"
                  justify="center"
                  dense
                >
                  <v-col cols="9">
                    <v-banner
                      icon="mdi-timelapse"
                      :text="`Last monitor was on ${new Date(monitor.last_monitor).toUTCString()}`"
                    />
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
          </template>
        </v-card>
      </v-row>
    </v-container>
  </MenuAdministration>
</template>

<script setup lang="ts">
import { VNumberInput } from "vuetify/labs/VNumberInput";
definePageMeta({ layout: false });
const iApi = useApi("/api/integrations/", true);
const integrations = ref([]);
iApi
  .list({ ordering: "id" }, true)
  .then((response) => (integrations.value = response.items));

const mApi = useApi("/api/monitor/", true, "Monitoring");
const save = ref(false);
const monitor = ref({});
mApi.get(1).then((response) => (monitor.value = response));
</script>

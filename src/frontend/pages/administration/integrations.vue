<template>
  <MenuAdministration>
    <v-container>
      <BaseSection class="mt-5" title="Platforms" icon="mdi-apps">
        <v-row justify="space-around" dense>
          <v-col
            v-for="integration in integrations"
            :key="integration.id"
            cols="5"
            class="ma-5"
          >
            <Integration
              v-if="
                !Object.keys(customForm).includes(integration.id.toString())
              "
              :api="iApi"
              :integration="integration"
            />
            <v-dialog
              v-if="Object.keys(customForm).includes(integration.id.toString())"
            >
              <template #activator="{ props: activatorProps }">
                <Integration
                  :api="iApi"
                  :integration="integration"
                  hover
                  v-bind="activatorProps"
                />
              </template>
              <template #default="{ isActive }">
                <component
                  :is="customForm[integration.id]"
                  :integration-api="iApi"
                  :integration="integration"
                  @close-dialog="isActive.value = false"
                />
              </template>
            </v-dialog>
          </v-col>
        </v-row>
      </BaseSection>
      <v-row>
        <BaseSection
          title="Monitoring"
          icon="mdi-radar"
          subtitle="Some platforms like CVE Crowd are executed periodically to keep your findings up to date"
        >
          <v-container fluid>
            <v-row justify="center">
              <v-col cols="5">
                <VNumberInput
                  v-model="monitor.hour_span"
                  control-variant="split"
                  label="Hours Lapse"
                  inset
                  variant="outlined"
                  :max="168"
                  :min="24"
                  @update:model-value="save = true"
                >
                  <template #append>
                    <BaseButton
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
                    <BaseButton
                      v-if="
                        new Date(monitor.last_monitor).getFullYear() !== 1970
                      "
                      icon="$info"
                      icon-color="info"
                      :tooltip="`Last monitor was on ${new Date(monitor.last_monitor).toDateString()}`"
                    />
                  </template>
                </VNumberInput>
              </v-col>
            </v-row>
          </v-container>
        </BaseSection>
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
const customForm = ref({
  1: resolveComponent("IntegrationDialogDefectDojo"),
  2: resolveComponent("IntegrationDialogNvdNist"),
  4: resolveComponent("IntegrationDialogCveCrowd"),
});
</script>

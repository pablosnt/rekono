<template>
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
      <v-col cols="4">
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
            <v-btn
              :disabled="!save"
              variant="text"
              icon="mdi-tray-arrow-down"
              color="green"
              @click="
                api
                  .update({ hour_span: monitor.hour_span }, 1)
                  .then((response) => (monitor = response))
              "
            />
          </template>
        </VNumberInput>
      </v-col>
      <v-col cols="6">
        <v-banner
          icon="mdi-timelapse"
          :text="`Last monitor was on ${new Date(monitor.last_monitor).toString()}`"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { VNumberInput } from "vuetify/labs/VNumberInput";
const save = ref(false);
const api = useApi("/api/monitor/", true, "Monitoring");
const monitor = ref({});
api.get(1).then((response) => (monitor.value = response));
</script>

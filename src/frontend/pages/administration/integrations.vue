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
                <ShowIntegration
                  v-if="integration.id !== 1 && integration.id !== 4"
                  :api="api"
                  :integration="integration"
                />
                <v-dialog v-if="integration.id === 1 || integration.id === 4">
                  <template #activator="{ props: activatorProps }">
                    <ShowIntegration
                      :api="api"
                      :integration="integration"
                      v-bind="activatorProps"
                    />
                  </template>
                  <template #default="{ isActive }">
                    <DialogDefectDojo
                      v-if="integration.id === 1"
                      :integration-api="api"
                      :integration="integration"
                      @close-dialog="isActive.value = false"
                    />
                    <DialogCveCrowd
                      v-if="integration.id === 4"
                      :integration-api="api"
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
          <v-card-title class="text-h5">
            <v-icon color="red" icon="mdi-radar" />
            <span class="me-1" />
            Monitoring
          </v-card-title>
          <v-card-text>
            <ShowMonitorSettings />
          </v-card-text>
        </v-card>
      </v-row>
    </v-container>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const api = useApi("/api/integrations/", true);
const integrations = ref([]);
api
  .list({ ordering: "id" }, true)
  .then((response) => (integrations.value = response.items));
</script>

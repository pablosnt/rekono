<template>
  <MenuAdministration>
    <v-container class="mt-5" fluid>
      <v-row justify="space-around" dense>
        <v-col
          v-for="queue in Object.keys(queues)"
          :key="queue"
          class="mt-5"
          cols="5"
        >
          <v-card elevation="3" class="mx-auto" density="comfortable">
            <template #title>
              <v-card-title class="text-capitalize">{{ queue }}</v-card-title>
            </template>
            <template #append>
              <div v-if="queues[queue].started_jobs > 0">
                <v-chip>
                  <v-progress-circular color="red" :size="20" indeterminate />
                  <span class="me-1" />
                  {{ queues[queue].started_jobs }} running
                </v-chip>
                <span class="me-2" />
              </div>
              <UtilsChipCounter
                :number="queues[queue].workers"
                entity="workers"
                icon="mdi-sitemap"
                :color="undefined"
                show-zero
              />
            </template>
            <template #text>
              <v-container fluid>
                <v-row justify="space-around" dense>
                  <v-col cols="4">
                    <p>
                      <span class="text-medium-emphasis ml-2"
                        ><v-icon icon="mdi-playlist-play" size="small" /> In
                        Queue:</span
                      >
                      {{ queues[queue].jobs }}
                    </p>
                  </v-col>
                  <v-col cols="4">
                    <p>
                      <span class="text-medium-emphasis ml-2"
                        ><v-icon icon="mdi-graph-outline" size="small" /> On
                        Hold:</span
                      >
                      {{ queues[queue].deferred_jobs }}
                    </p>
                  </v-col>
                  <v-col cols="4">
                    <p>
                      <span class="text-medium-emphasis ml-2"
                        ><v-icon icon="mdi-clock-outline" size="small" />
                        Scheduled:</span
                      >
                      {{ queues[queue].scheduled_jobs }}
                    </p>
                  </v-col>
                  <v-col cols="4">
                    <p>
                      <span class="text-medium-emphasis ml-2"
                        ><v-icon
                          icon="mdi-check-circle"
                          color="green"
                          size="small"
                        />
                        Successful:</span
                      >
                      {{ queues[queue].finished_jobs }}
                    </p>
                  </v-col>
                  <v-col cols="4">
                    <p>
                      <span class="text-medium-emphasis ml-2"
                        ><v-icon
                          icon="mdi-close-circle"
                          color="red"
                          size="small"
                        />
                        Failed:</span
                      >
                      {{ queues[queue].failed_jobs }}
                    </p>
                  </v-col>
                </v-row>
              </v-container>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const api = useApi("/api/rq-stats/", true);
const queues = ref({});
api.get().then((response) => (queues.value = response));
</script>

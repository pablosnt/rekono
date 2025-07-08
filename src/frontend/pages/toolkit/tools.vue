<template>
  <MenuToolkit>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      icon="mdi-rocket"
      empty-head="No Tools"
      empty-text="There are no tools"
      cols="4"
    >
      <template #item="{ item }">
        <v-card
          :title="item.name"
          :subtitle="
            '$ ' + item.command + (item.script ? ' ' + item.script : '')
          "
          :prepend-avatar="item.icon"
          elevation="2"
          class="ma-3"
          density="comfortable"
        >
          <template #append>
            <v-chip v-if="item.version" class="mr-2" prepend-icon="mdi-tag">
              {{ item.version }}
            </v-chip>
            <UtilsGreenCheck
              :condition="item.is_installed"
              true-text="Installed"
              false-text="Tool may have been installed after its last execution attempt"
            />
            <BaseButton :link="item.reference" new-tab hide />
          </template>
          <template #text>
            <p v-if="item.configurations.length === 1" class="ma-6">
              {{ item.configurations[0].name }}
            </p>
            <v-expansion-panels
              v-if="item.configurations.length > 1"
              v-model="show"
              variant="accordion"
            >
              <v-expansion-panel elevation="0" :value="item.id">
                <v-expansion-panel-title
                  >{{ item.configurations.filter((c) => c.default)[0].name }}
                  <v-tooltip activator="parent" text="Configurations" />
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-container v-show="show === item.id">
                    <v-row
                      v-for="configuration in item.configurations"
                      :key="configuration.id"
                    >
                      <p v-if="!configuration.default" class="ma-1">
                        {{ configuration.name }}
                      </p>
                    </v-row>
                  </v-container>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            <v-divider class="mt-4 mb-4" />
            <div class="d-flex flex-row justify-center ga-2">
              <v-chip
                v-for="intensity in item.intensities"
                :key="intensity.value"
                size="small"
                :color="enums.intensities[intensity.value].color"
              >
                {{ intensity.value }}
              </v-chip>
            </div>
          </template>
          <v-card-actions>
            <TaskButton :tool="item" tooltip="Run" />
            <v-spacer />
            <UtilsLike
              class="mr-5"
              :api="api"
              :item="item"
              @reload="(value) => dataset.loadData(value)"
            />
          </v-card-actions>
        </v-card>
      </template>
    </Dataset>
  </MenuToolkit>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const show = ref(null);
const dataset = ref(null);
const enums = useEnums();
const filters = useFilters();
const api = ref(useApi("/api/tools/", true, "Tool"));
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Stage",
      icon: "mdi-stairs",
      collection: filters.collectionFromEnum(enums.stages),
      fieldValue: "id",
      fieldTitle: "name",
      key: "stage",
    },
    {
      type: "autocomplete",
      label: "Intensity",
      icon: "mdi-fire",
      color: "orange",
      collection: filters.collectionFromEnum(enums.intensities),
      fieldValue: "id",
      fieldTitle: "name",
      key: "intensity",
    },
    {
      type: "switch",
      label: "Installed",
      color: "green",
      cols: 2,
      key: "is_installed",
      trueValue: true,
      falseValue: null,
    },
    {
      type: "switch",
      label: "Likes",
      color: "red",
      cols: 1,
      key: "like",
      trueValue: true,
      falseValue: null,
    },
    {
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      cols: 2,
      collection: ["id", "name", "command"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ])
  .then((results) => (filtering.value = results));
</script>

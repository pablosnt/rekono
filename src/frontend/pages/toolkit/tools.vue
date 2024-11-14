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
          rel="noopener"
          elevation="3"
          class="mx-auto"
          density="compact"
        >
          <template #append>
            <v-chip v-if="item.version" prepend-icon="mdi-tag">
              {{ item.version }}
            </v-chip>
            <span class="me-3" />
            <UtilsGreenCheck
              :condition="item.is_installed"
              true-text="Installed"
              false-text="Tool may have been installed after its last execution attempt"
            />
          </template>

          <template #text>
            <v-card-text>
              <template
                v-for="configuration in item.configurations"
                :key="configuration.id"
              >
                <div class="d-flex flex-row">
                  <BaseButton
                    v-if="configuration.default"
                    :icon="
                      item.configurations.length < 2
                        ? undefined
                        : show === item.id
                          ? 'mdi-chevron-up'
                          : 'mdi-chevron-down'
                    "
                    icon-color="black"
                    size="medium"
                    :tooltip="
                      item.configurations.length > 1
                        ? 'Configurations'
                        : 'Configuration'
                    "
                    @click="show = show !== item.id ? item.id : null"
                  >
                    <template #prepend>
                      <p>{{ configuration.name }}</p>
                      <span class="me-2" />
                    </template>
                  </BaseButton>
                </div>
                <v-expand-transition>
                  <div v-show="show == item.id" v-if="!configuration.default">
                    <p>{{ configuration.name }}</p>
                  </div>
                </v-expand-transition>
              </template>
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
            </v-card-text>
          </template>

          <v-card-actions>
            <TaskButton :tool="item" tooltip="Run" />
            <v-spacer />
            <UtilsLike
              :api="api"
              :item="item"
              @reload="(value) => dataset.loadData(value)"
            />
            <BaseButton :link="item.reference" new-tab hide />
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
const enums = ref(useEnums());
const filters = useFilters();
const api = ref(useApi("/api/tools/", true, "Tool"));
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Stage",
      icon: "mdi-stairs",
      collection: filters.collectionFromEnum(enums.value.stages),
      fieldValue: "id",
      fieldTitle: "name",
      key: "stage",
    },
    {
      type: "autocomplete",
      label: "Intensity",
      icon: "mdi-volume-high",
      collection: filters.collectionFromEnum(enums.value.intensities),
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
      collection: ["id", "name", "command"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ])
  .then((results) => (filtering.value = results));
</script>

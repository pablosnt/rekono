<template>
  <MenuToolkit>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      ordering="id"
      icon="mdi-rocket"
      empty="There are no tools"
      @load-data="(data) => (tools = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="tool in tools" :key="tool.id" cols="4">
            <v-card
              :title="tool.name"
              :subtitle="
                '$ ' + tool.command + (tool.script ? ' ' + tool.script : '')
              "
              :prepend-avatar="tool.icon"
              rel="noopener"
              elevation="3"
              class="mx-auto"
              density="compact"
            >
              <template #append>
                <v-chip v-if="tool.version">
                  <v-icon icon="mdi-tag" start />
                  {{ tool.version }}
                </v-chip>
                <span class="me-3" />
                <ButtonGreenCheck
                  :condition="tool.is_installed"
                  true-text="Installed"
                  false-text="Tool may have been installed after its last execution attempt"
                />
              </template>

              <template #text>
                <v-card-text>
                  <template
                    v-for="configuration in tool.configurations"
                    :key="configuration.id"
                  >
                    <div class="d-flex flex-row">
                      <v-btn
                        v-if="configuration.default"
                        icon
                        size="medium"
                        variant="text"
                        @click="show = show !== tool.id ? tool.id : null"
                      >
                        <p>{{ configuration.name }}</p>
                        <span class="me-2" />
                        <v-icon
                          v-if="tool.configurations.length > 1"
                          :icon="
                            show === tool.id
                              ? 'mdi-chevron-up'
                              : 'mdi-chevron-down'
                          "
                          color="black"
                        />
                        <v-tooltip
                          activator="parent"
                          :text="
                            tool.configurations.length > 1
                              ? 'Configurations'
                              : 'Configuration'
                          "
                        />
                      </v-btn>
                    </div>
                    <v-expand-transition>
                      <div
                        v-show="show == tool.id"
                        v-if="!configuration.default"
                      >
                        <p>{{ configuration.name }}</p>
                      </div>
                    </v-expand-transition>
                  </template>
                  <v-divider class="mt-4 mb-4" />
                  <div class="d-flex flex-row justify-center ga-2">
                    <v-chip
                      v-for="intensity in tool.intensities"
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
                <ButtonRun :tool="tool" />
                <v-spacer />
                <ButtonLike
                  :api="api"
                  :item="tool"
                  @reload="(value) => dataset.loadData(value)"
                />
                <ButtonLink :link="tool.reference" />
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuToolkit>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const tools = ref(null);
const show = ref(null);
const dataset = ref(null);
const enums = ref(useEnums());
const api = ref(useApi("/api/tools/", true, "Tool"));
const filtering = ref([
  {
    type: "autocomplete",
    label: "Stage",
    icon: "mdi-stairs",
    collection: Object.entries(enums.value.stages).map(([k, v]) => {
      v.name = k;
      return v;
    }),
    fieldValue: "id",
    fieldTitle: "name",
    key: "stage",
    value: null,
  },
  {
    type: "autocomplete",
    label: "Intensity",
    icon: "mdi-volume-high",
    collection: Object.entries(enums.value.intensities).map(([k, v]) => {
      v.name = k;
      return v;
    }),
    fieldValue: "id",
    fieldTitle: "name",
    key: "intensity",
    value: null,
  },
  {
    type: "switch",
    label: "Installed",
    color: "green",
    cols: 2,
    key: "is_installed",
    trueValue: true,
    falseValue: null,
    value: null,
  },
  {
    type: "switch",
    label: "Likes",
    color: "red",
    cols: 1,
    key: "like",
    trueValue: true,
    falseValue: null,
    value: null,
  },
  {
    type: "autocomplete",
    label: "Sort",
    icon: "mdi-sort",
    collection: ["id", "name", "command"],
    fieldValue: "id",
    fieldTitle: "name",
    key: "ordering",
    value: "id",
  },
]);
</script>

<template>
  <MenuResources>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      ordering="id"
      @load-data="(data) => (tools = data)"
    >
      <template #data>
        <v-container v-if="tools !== null" fluid>
          <v-row v-if="tools.length === 0" justify="center" dense>
            <v-empty-state icon="mdi-rocket" title="There are no tools" />
          </v-row>
          <v-row dense>
            <v-col v-for="tool in tools" :key="tool.id" cols="4">
              <v-card
                :title="tool.name"
                :subtitle="
                  '$ ' + tool.command + (tool.script ? ' ' + tool.script : '')
                "
                :prepend-avatar="tool.icon"
                rel="noopener"
                elevation="4"
                class="mx-auto"
                density="compact"
              >
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

                <v-card-actions>
                  <v-dialog width="auto">
                    <template #activator="{ props: activatorProps }">
                      <v-btn hover icon size="x-large" v-bind="activatorProps">
                        <v-icon icon="mdi-play-circle" color="green" />
                        <v-tooltip activator="parent" text="Run" />
                      </v-btn>
                    </template>
                    <template #default="{ isActive }">
                      <DialogTask
                        :tool="tool"
                        @close-dialog="isActive.value = false"
                      />
                    </template>
                  </v-dialog>
                  <v-spacer />
                  <ButtonLike
                    v-if="user.role !== 'Reader'"
                    :api="api"
                    :item="tool"
                    @reload="(value) => dataset.loadData(value)"
                  />
                  <ButtonLink :link="tool.reference" />
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </template>
    </Dataset>
  </MenuResources>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
defineEmits(["loadData"]);
const tools = ref(null);
const show = ref(null);
const dataset = ref(null);
const user = userStore();
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

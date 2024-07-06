<template>
  <MenuProject>
    <!-- TODO: Review Add dialog -->
    <Dataset
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: projectId }"
      ordering="id"
      :add="DialogTarget"
      icon="mdi-target"
      :empty="
        user.role === 'Reader'
          ? 'There are no targets'
          : 'Create your first target to start hacking'
      "
      @load-data="(data) => (targets = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="target in targets" :key="target.id" cols="6">
            <!-- TODO: On click dialog: target ports, http headers, parameters (CVEs, technologies) -->
            <v-card
              :title="target.target"
              :subtitle="target.type"
              elevation="2"
              class="mx-auto"
              density="compact"
              :prepend-icon="enums.targets[target.type].icon"
            >
              <template #append>
                <ButtonRun :target="target" />
                <ButtonDelete
                  :id="target.id"
                  :api="api"
                  :text="`Target '${target.target}' will be removed`"
                />
              </template>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const user = userStore();
const enums = useEnums();
const route = useRoute();
const projectId = ref(route.params.project_id);
const DialogTarget = resolveComponent("DialogTarget");
const api = useApi("/api/targets/", true, "Target");
const targets = ref([]);
const filtering = ref([
  {
    type: "autocomplete",
    label: "Type",
    icon: "mdi-target",
    collection: Object.entries(enums.targets).map(([k, v]) => {
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
    label: "Sort",
    icon: "mdi-sort",
    cols: 2,
    collection: ["id", "target", "type"],
    fieldValue: "id",
    fieldTitle: "name",
    key: "ordering",
    value: "id",
  },
]);
</script>

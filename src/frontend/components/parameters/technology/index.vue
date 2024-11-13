<template>
  <v-card
    title="Technologies"
    :prepend-icon="enums.findings.Technology.icon"
    variant="text"
  >
    <template #append>
      <v-dialog width="auto">
        <template #activator="{ props: activatorProps }">
          <v-btn
            icon="mdi-plus-thick"
            variant="text"
            size="large"
            color="green"
            v-bind="activatorProps"
          />
        </template>
        <template #default="{ isActive }">
          <ParametersTechnologyDialog
            :api="api"
            @completed="
              isActive.value = false;
              dataset.loadData(false);
            "
            @close-dialog="isActive.value = false"
          />
        </template>
      </v-dialog>
    </template>
    <template #text>
      <Dataset
        ref="dataset"
        :api="api"
        :header="false"
        :icon="enums.findings.Technology.icon"
        :default-parameters="{ target: route.params.target_id, ordering: 'id' }"
        empty-head="No Technologies"
        empty-text="There are no known technologies to be used as parameter"
        @load-data="(data) => (technologies = data)"
      >
        <template #data>
          <v-row justify="center" dense>
            <v-col cols="10">
              <v-table density="compact">
                <thead>
                  <tr>
                    <th class="text-center font-weight-bold">Name</th>
                    <th class="text-center font-weight-bold">Version</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="technology in technologies" :key="technology.id">
                    <td class="text-center text-capitalize">
                      {{ technology.name }}
                    </td>
                    <td class="text-center">{{ technology.version }}</td>
                    <td>
                      <UtilsDeleteButton
                        :id="technology.id"
                        :api="api"
                        :text="`Technology '${technology.name}' will be removed`"
                        @completed="dataset.loadData(false)"
                      />
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-col>
          </v-row>
        </template>
      </Dataset>
    </template>
  </v-card>
</template>

<script setup lang="ts">
const enums = useEnums();
const route = useRoute();
const api = useApi("/api/parameters/technologies/", true, "Technology");
const dataset = ref(null);
const technologies = ref([]);
</script>

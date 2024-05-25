<template>
  <MenuAdministration>
    <v-container fluid>
      <v-row justify="center" dense>
        <v-alert
          color="info"
          icon="$info"
          variant="tonal"
          text="Targets can be denied by regexes, specific values or whole networks"
          closable
        />
      </v-row>
    </v-container>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="[]"
      ordering="id"
      :add="DialogTargetDenylist"
      @load-data="(data) => (denylist = data)"
    >
      <template #data>
        <v-container fluid>
          <v-row dense>
            <v-col v-for="pattern in denylist" :key="pattern.id" cols="4">
              <v-card elevation="4" class="mx-auto" density="compact">
                <v-card-text>
                  <FormTargetDenylist
                    :api="api"
                    :pattern="pattern"
                    @completed="dataset.loadData(false)"
                  />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </template>
    </Dataset>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
defineEmits(["closeDialog"]);
const DialogTargetDenylist = resolveComponent("DialogTargetDenylist");
const api = ref(useApi("/api/target-denylist/", true, "Target pattern"));
const dataset = ref(null);
const denylist = ref([]);
</script>

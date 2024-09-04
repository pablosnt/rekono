<template>
  <MenuAdministration>
    <v-container fluid>
      <v-row justify="center" dense>
        <v-alert
          color="info"
          icon="$info"
          variant="tonal"
          text="Targets can be denied by regexes, specific values or whole networks. Default patterns can't be edited or removed as they are protecting the own Rekono infrastructure"
          closable
        />
      </v-row>
    </v-container>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="[]"
      ordering="id"
      :add="TargetDenylistDialog"
      @load-data="(data) => (denylist = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="pattern in denylist" :key="pattern.id" cols="4">
            <v-card elevation="3" class="mx-auto" density="compact">
              <TargetDenylistForm
                :api="api"
                :pattern="pattern"
                @completed="dataset.loadData(false)"
              />
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
defineEmits(["closeDialog"]);
const TargetDenylistDialog = resolveComponent("TargetDenylistDialog");
const api = ref(useApi("/api/target-denylist/", true, "Target pattern"));
const dataset = ref(null);
const denylist = ref([]);
</script>

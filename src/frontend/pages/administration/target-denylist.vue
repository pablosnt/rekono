<template>
  <MenuAdministration>
    <Dataset
      ref="dataset"
      :api="api"
      :default-parameters="{ ordering: 'id' }"
      :add="TargetDenylistDialog"
      cols="4"
    >
      <template #prepend-search>
        <v-row class="mb-5" dense>
          <v-alert
            class="text-center"
            color="info"
            icon="$info"
            variant="tonal"
            text="Targets can be denied by regex, specific values or network. Default patterns can't be edited or removed as they are protecting Rekono infrastructure"
            closable
          />
        </v-row>
      </template>
      <template #item="{ item }">
        <v-card elevation="1" class="ma-5" density="compact">
          <TargetDenylistForm
            class="ml-4 mr-4 mt-6"
            :api="api"
            :pattern="item"
            @completed="dataset.loadData(false)"
          />
        </v-card>
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
</script>

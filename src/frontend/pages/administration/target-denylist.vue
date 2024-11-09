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
      :default-parameters="{ ordering: 'id' }"
      :add="TargetDenylistDialog"
      cols="4"
    >
      <template #item="{ item }">
        <v-card elevation="3" class="mx-auto" density="compact">
          <TargetDenylistForm
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

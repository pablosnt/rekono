<template>
  <v-dialog width="auto">
    <template #activator="{ props: activatorProps }">
      <v-chip
        :prepend-icon="enums.triage[finding.triage_status].icon"
        :color="enums.triage[finding.triage_status].color"
        v-bind="activatorProps"
        >{{ finding.triage_status }}</v-chip
      >
    </template>
    <template #default="{ isActive }">
      <FindingTriageDialog
        :api="api"
        :finding="finding"
        @completed="
          isActive.value = false;
          $emit('change');
        "
        @close-dialog="isActive.value = false"
      />
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
defineProps({ api: Object, finding: Object });
defineEmits(["change"]);
const enums = useEnums();
</script>

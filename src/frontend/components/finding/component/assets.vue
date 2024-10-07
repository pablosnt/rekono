<template>
  <v-container fluid>
    <v-row dense>
      <v-col v-for="finding in findings" :key="finding.id" cols="6" />
    </v-row>
  </v-container>
</template>

<!-- 
    TODO:
    Hosts
      -- Ports & Services (same table as Hosts)
      Paths (per Port) (Dialog)
      Technologies (per Port) (expand section) 
      -- Credentials  (Dialog)
      -- Exploits (Dialog) 

    Check all findings have the relationships needed on creation
  -->

<script setup lang="ts">
defineProps({
  api: Object,
  findings: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
defineEmits(["reload"]);
// const enums = useEnums();
</script>

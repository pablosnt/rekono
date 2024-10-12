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
      -- Ports & Services (same table as Hosts) -> Limit of N ports per host, otherwise, load more button is needed
        -- Dialog with tabs
          -- Paths
          -- Technologies (there won't be many per port) (two sections: left side with list of techs, right side with details in tabs)
            -- Credentials (there won't be manhy per tech)
            -- Exploits
            -- Vulnerabilities (link to vulnerabilities page, if any)
        -- Vulnerabilities (link to vulnerabilities page, if any)

    TODO: Check all findings have the relationships needed on creation
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

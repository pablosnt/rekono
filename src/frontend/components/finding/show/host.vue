<template>
  <finding-show-component
    :api="api"
    :finding="finding"
    title="address"
    subtitle="os"
    :icon="enums.osType[finding.os_type].icon"
    :icon-color="enums.osType[finding.os_type].color"
    :defectdojo="defectdojo"
    :defectdojo-settings="defectdojoSettings"
    :hacktricks="hacktricks"
    finding-type="host"
    @reload="$emit('reload')"
  >
    <!-- TODO: table with ports and services -->
  </finding-show-component>
</template>

<!-- 
    TODO:
    Hosts
      -- Ports & Services (same table as Hosts) -> Limit of N ports per host, otherwise, load more button is needed
        -- New page with tabs
          -- Paths
          -- Technologies (there won't be many per port) (two sections: left side with list of techs, right side with details in tabs)
            -- Credentials (there won't be manhy per tech)
            -- Exploits (dialog)
            -- Vulnerabilities (link to vulnerabilities page, if any)
          -- Vulnerabilities (link to vulnerabilities page, if any)

    TODO: Check all findings have the relationships needed on creation
  -->

<script setup lang="ts">
defineProps({
  api: Object,
  finding: Object,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
defineEmits(["reload"]);
const enums = useEnums();
</script>

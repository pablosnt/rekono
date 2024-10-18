<template>
  <IntegrationLink
    v-if="
      defectdojo &&
      defectdojo.enabled &&
      defectdojoSettings.is_available &&
      finding.defect_dojo_id
    "
    :integration="defectdojo"
    :link="`${defectdojoSettings.server}/finding/${finding.defect_dojo_id}`"
    tooltip
    tooltip-text="Defect-Dojo finding"
  />
  <IntegrationLink
    v-if="hacktricks && hacktricks.enabled && finding.hacktricks_link"
    :integration="hacktricks"
    :link="finding.hacktricks_link"
    tooltip
  />
  <UtilsButtonLink :link="finding.reference" />
</template>

<script setup lang="ts">
defineProps({
  finding: Object,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
</script>

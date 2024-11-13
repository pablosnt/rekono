<template>
  <BaseLink
    v-if="
      defectdojo &&
      defectdojo.enabled &&
      defectdojoSettings.is_available &&
      finding.defect_dojo_id
    "
    :link="`${defectdojoSettings.server}/finding/${finding.defect_dojo_id}`"
    :avatar="defectdojo.icon"
    tooltip="Defect-Dojo finding"
  />
  <BaseLink
    v-if="hacktricks && hacktricks.enabled && finding.hacktricks_link"
    :link="finding.hacktricks_link"
    :avatar="hacktricks.icon"
    :tooltip="hacktricks.name"
  />
  <BaseLink :link="finding.reference" />
</template>

<script setup lang="ts">
defineProps({
  finding: Object,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
</script>

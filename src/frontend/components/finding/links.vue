<template>
  <BaseButton
    v-if="
      defectdojo &&
      defectdojo.enabled &&
      defectdojoSettings.is_available &&
      finding.defect_dojo_id
    "
    :link="`${defectdojoSettings.server}/finding/${finding.defect_dojo_id}`"
    :avatar="defectdojo.icon"
    tooltip="Defect-Dojo finding"
    new-tab
  />
  <BaseButton
    v-if="hacktricks && hacktricks.enabled"
    :link="finding.hacktricks_link"
    :avatar="hacktricks.icon"
    :tooltip="hacktricks.name"
    new-tab
    hide
  />
  <BaseButton :link="finding.reference" new-tab hide />
</template>

<script setup lang="ts">
defineProps({
  finding: Object,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
</script>

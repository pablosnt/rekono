<template>
  <!-- todo: findings like this might be marked as fixed because they are not detected by the same configuration with different wordlist -->
  <finding-show-component
    :api="api"
    :finding="finding"
    title="path"
    subtitle="status"
    :icon="enums.findings.Path.icon"
    :defectdojo="defectdojo"
    :defectdojo-settings="defectdojoSettings"
    :hacktricks="hacktricks"
    finding-type="path"
    @reload="$emit('reload')"
  >
    <template #text>
      {{ finding.extra_info }}
    </template>
  </finding-show-component>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  finding: Object,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
  host: Number,
});
defineEmits(["reload"]);
const enums = useEnums();
</script>

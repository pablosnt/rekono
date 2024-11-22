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
    <template #text>
      <FindingPort
        :ports="finding.port"
        :defectdojo="defectdojo"
        :defectdojo-settings="defectdojoSettings"
        :hacktricks="hacktricks"
      />
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
});
defineEmits(["reload"]);
const enums = useEnums();
</script>

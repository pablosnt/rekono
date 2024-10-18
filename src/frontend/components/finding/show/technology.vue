<template>
  <finding-show-component
    :api="api"
    :finding="finding"
    title="name"
    subtitle="version"
    :icon="enums.findings.Technology.icon"
    :defectdojo="defectdojo"
    :defectdojo-settings="defectdojoSettings"
    :hacktricks="hacktricks"
    finding-type="technology"
    @reload="$emit('reload')"
  >
    <template #text>
      {{ finding.description }}
    </template>
  </finding-show-component>
</template>

<!-- TODO: credentials, vulnerabilities, exploits  -->

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

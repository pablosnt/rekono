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
    <template #append-after>
      <UtilsCounter
        icon="mdi-ladybug"
        size="x-large"
        :collection="finding.vulnerability"
        :link="`/projects/${route.params.project_id}/findings?tab=vulnerabilities&host=${host}&port=${finding.port}&technology=${finding.id}`"
        tooltip="Vulnerabilities"
        show-zero
      />
    </template>
    <template #text>
      {{ finding.description }}
      <FindingShowCredentials
        :credentials="finding.credential"
        :defectdojo="defectdojo"
        :defectdojo-settings="defectdojoSettings"
        :hacktricks="hacktricks"
        @reload="$emit('reload')"
      />
    </template>
  </finding-show-component>
</template>

<!-- TODO: exploits  -->

<script setup lang="ts">
defineProps({
  api: Object,
  finding: Object,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
  host: Number
});
defineEmits(["reload"]);
const enums = useEnums();
const route = useRoute()
</script>

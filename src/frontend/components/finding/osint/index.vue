<template>
  <Finding
    v-if="finding"
    :api="api"
    :finding="finding"
    title="data"
    subtitle="source"
    :icon="
      finding.data_type ? enums.osintTypes[finding.data_type].icon : undefined
    "
    :icon-tooltip="finding.data_type"
    :defectdojo="defectdojo"
    :defectdojo-settings="defectdojoSettings"
    :hacktricks="hacktricks"
    finding-type="osint"
    triage
    @reload="$emit('reload')"
  >
    <template #actions>
      <BaseButton
        v-if="['IP', 'Domain'].includes(finding.data_type)"
        hover
        icon="mdi-target"
        icon-color="red"
        tooltip="Create target"
        @click="
          api
            .create({}, finding.id, 'target/')
            .then(() =>
              navigateTo(`/projects/${route.params.project_id}/targets`),
            )
        "
      />
    </template>
  </Finding>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  finding: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
defineEmits(["reload"]);
const enums = useEnums();
</script>

<template>
  <v-container fluid>
    <v-row dense>
      <v-col v-for="finding in findings" :key="finding.id" cols="6">
        <FindingShowComponent
          :api="api"
          :finding="finding"
          title="data"
          subtitle="source"
          :icon="
            finding.data_type
              ? enums.osintTypes[finding.data_type].icon
              : undefined
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
            <v-btn
              v-if="['IP', 'Domain'].includes(finding.data_type)"
              hover
              icon
              variant="text"
              @click="
                api
                  .create({}, finding.id, 'target/')
                  .then(() =>
                    navigateTo(`/projects/${route.params.project_id}/targets`),
                  )
              "
            >
              <v-icon icon="mdi-target" color="red" />
              <v-tooltip activator="parent" text="Create target" />
            </v-btn>
          </template>
        </FindingShowComponent>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  findings: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
defineEmits(["reload"]);
const enums = useEnums();
</script>

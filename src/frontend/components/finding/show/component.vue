<template>
  <v-card
    :title="finding[title]"
    :subtitle="subtitle ? finding[subtitle] : undefined"
  >
    <template #prepend>
      <v-btn v-if="icon" hover icon variant="text" @click.prevent.stop>
        <v-icon :icon="icon" :color="iconColor" />
        <v-tooltip v-if="iconTooltip" activator="parent" :text="iconTooltip" />
      </v-btn>
    </template>
    <template #append>
      <slot name="append-before" />
      <UtilsCounter
        class="ml-2"
        :collection="finding.notes"
        tooltip="Notes"
        icon="mdi-notebook"
        :link="`/projects/${route.params.project_id}/notes`"
        color="indigo-darken-1"
        new-tab
      />
      <FindingLinks
        :finding="finding"
        :defectdojo="defectdojo"
        :defectdojo-settings="defectdojoSettings"
        :hacktricks="hacktricks"
      />
      <slot name="append-after" />
    </template>
    <template #text>
      <slot name="text" />
      <v-divider class="my-3 mb-5" />
      <FindingToolCounter
        :finding="finding"
        @exposure="(value) => (exposure = value)"
      />
    </template>
    <v-card-actions>
      <FindingFix
        :api="api"
        :finding="finding"
        :asset-syntax="!triage"
        @change="$emit('reload')"
      />
      <v-spacer />
      <v-btn variant="text">
        <v-chip
          v-if="exposure"
          :text="exposure"
          prepend-icon="mdi-clock-alert"
          color="red"
        />
        <v-tooltip activator="parent" text="Exposure time" />
      </v-btn>
      <FindingTriageButton
        v-if="triage"
        :api="api"
        :finding="finding"
        @change="$emit('reload')"
      />
      <NoteButton v-bind="noteProperties" />
      <slot name="actions" />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  finding: Object,
  title: String,
  subtitle: {
    type: String,
    required: false,
    default: undefined,
  },
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  iconColor: {
    type: String,
    required: false,
    default: "red",
  },
  iconTooltip: {
    type: String,
    required: false,
    default: undefined,
  },
  triage: {
    type: Boolean,
    required: false,
    default: false,
  },
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
  findingType: String,
});
defineEmits(["reload"]);
const route = useRoute();
const noteProperties = ref({
  [props.findingType]: props.finding,
  project: route.params.project_id,
});
const exposure = ref(null);
</script>

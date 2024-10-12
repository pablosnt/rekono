<template>
  <v-card
    :title="finding[title]"
    :subtitle="subtitle ? finding[subtitle] : undefined"
  >
    <template #prepend>
      <v-btn v-if="icon" hover icon variant="text" @click.prevent.stop>
        <v-icon :icon="icon" color="red" />
        <v-tooltip v-if="iconTooltip" activator="parent" :text="iconTooltip" />
      </v-btn>
    </template>
    <template #append>
      <FindingLinks
        :finding="finding"
        :defectdojo="defectdojo"
        :defectdojo-settings="defectdojoSettings"
        :hacktricks="hacktricks"
      />
    </template>
    <template #text>
      <slot name="text" />
      <v-divider class="my-3 mb-5" />
      <FindingToolCounter :finding="finding" />
    </template>
    <v-card-actions>
      <FindingFix :api="api" :finding="finding" @change="$emit('reload')" />
      <v-spacer />
      <FindingTriageButton
        v-if="triage"
        :api="api"
        :finding="finding"
        @change="$emit('reload')"
      />
      <slot name="actions" />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
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
});
defineEmits(["reload"]);
</script>

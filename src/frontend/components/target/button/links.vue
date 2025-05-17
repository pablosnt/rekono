<template>
  <v-speed-dial
    v-if="
      target.tasks.length > 0 ||
      target.reports.length > 0 ||
      target.notes.length > 0
    "
    transition="fade-transition"
    :location="location"
    open-on-hover
  >
    <template #activator="{ props: activatorProps }">
      <BaseButton
        v-bind="activatorProps"
        size="x-large"
        color="blue-grey"
        icon="mdi-link"
        @click.prevent.stop
      />
    </template>
    <UtilsCounterButton
      key="1"
      :collection="target.tasks"
      tooltip="Tasks"
      icon="mdi-play-network"
      color="green"
      :link="`/projects/${target.project}/scans?target=${target.id}`"
      new-tab
    />
    <UtilsCounterButton
      key="2"
      :collection="target.reports"
      tooltip="Reports"
      icon="mdi-file-document"
      :link="`/projects/${target.project}/reports`"
      color="blue-grey-darken-1"
      new-tab
    />
    <UtilsCounterButton
      key="3"
      :collection="target.notes"
      tooltip="Notes"
      icon="mdi-notebook"
      :link="`/projects/${target.project}/notes`"
      color="indigo-darken-1"
      new-tab
    />
    <TargetDefectDojo
      class="mt-3"
      :target="target"
      :integration="integration"
      :settings="settings"
    />
  </v-speed-dial>
</template>

<script setup lang="ts">
defineProps({
  target: Object,
  integration: Object,
  settings: Object,
  location: { type: String, required: false, default: "left center" },
});
</script>

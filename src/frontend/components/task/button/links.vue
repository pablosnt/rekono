<template>
  <v-speed-dial
    v-if="
      task.wordlists.length > 0 ||
      task.reports.length > 0 ||
      task.notes.length > 0
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
      v-if="autz.isAuditor()"
      key="1"
      :collection="task.wordlists"
      tooltip="Wordlists used"
      icon="mdi-file-word-box"
      link="/toolkit/wordlists"
      color="blue-grey"
      new-tab
    />
    <UtilsCounterButton
      key="2"
      :collection="task.reports"
      tooltip="Reports"
      icon="mdi-file-document"
      :link="`/projects/${route.params.project_id}/reports`"
      color="blue-grey-darken-1"
      new-tab
    />
    <UtilsCounterButton
      key="3"
      :collection="task.notes"
      tooltip="Notes"
      icon="mdi-notebook"
      :link="`/projects/${route.params.project_id}/notes`"
      color="indigo-darken-1"
      new-tab
    />
  </v-speed-dial>
</template>

<script setup lang="ts">
defineProps({
  task: Object,
  location: { type: String, required: false, default: "left center" },
});
const route = useRoute();
const autz = useAutz();
</script>

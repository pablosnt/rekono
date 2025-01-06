<template>
  <v-speed-dial
    transition="fade-transition"
    location="bottom center"
    open-on-hover
  >
    <template #activator="{ props: activatorProps }">
      <BaseButton
        v-bind="activatorProps"
        size="large"
        color="blue-grey"
        icon="mdi-cog"
        @click.prevent.stop
      />
    </template>
    <NoteButton
      v-if="autz.isAuditor()"
      key="1"
      :project="parseInt(route.params.project_id)"
      :task="task"
      variant="flat"
      color="indigo-darken-1"
      icon-color="white"
      size="small"
      @completed="$emit('completed')"
    />
    <ReportButton
      key="2"
      :project="parseInt(route.params.project_id)"
      :target="task.target"
      :task="task"
      variant="flat"
      color="blue-grey-darken-2"
      icon-color="white"
      size="small"
      @completed="$emit('completed')"
    />
    <BaseButton
      key="3"
      v-if="autz.isAuditor() && task.progress === 100"
      icon="mdi-repeat"
      icon-color="white"
      color="green"
      size="small"
      tooltip="Re-run"
      variant="flat"
      @click.prevent.stop="
        api
          .create({}, task.id, 'repeat/')
          .then((response) =>
            navigateTo(
              `/projects/${route.params.project_id}/scans/${response.id}`,
            ),
          )
      "
    />
    <UtilsDeleteButton
      key="4"
      v-if="
        autz.isAuditor() && task.progress < 100 && task.status !== 'Cancelled'
      "
      :id="task.id"
      :api="api"
      :text="`Task '${task.title}' will be cancelled`"
      action="Cancel"
      @click.prevent.stop
      @completed="$emit('completed')"
      variant="flat"
      color="red"
      icon-color="white"
    />
  </v-speed-dial>
</template>

<script setup lang="ts">
defineProps({ task: Object, api: Object });
defineEmits(["completed"]);
const route = useRoute();
const autz = useAutz();
</script>

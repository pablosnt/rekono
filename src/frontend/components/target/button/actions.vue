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
      :project="parseInt(route.params.project_id)"
      :target="target"
      variant="flat"
      color="indigo-darken-1"
      icon-color="white"
      size="small"
    />
    <ReportButton
      :project="parseInt(route.params.project_id)"
      :target="target"
      variant="flat"
      color="blue-grey-darken-2"
      icon-color="white"
      size="small"
    />
    <UtilsDeleteButton
      :id="target.id"
      :api="api"
      :text="`Target '${target.target}' will be removed`"
      icon="mdi-trash-can"
      variant="flat"
      color="red"
      icon-color="white"
    />
  </v-speed-dial>
</template>

<script setup lang="ts">
defineProps({ target: Object, api: Object });
defineEmits(["completed"]);
const route = useRoute();
</script>

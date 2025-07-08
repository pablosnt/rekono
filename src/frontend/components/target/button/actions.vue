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
      :target="target"
      variant="flat"
      color="indigo-darken-1"
      icon-color="white"
      size="small"
      @completed="$emit('completed')"
    />
    <ReportButton
      key="2"
      :project="parseInt(route.params.project_id)"
      :target="target"
      variant="flat"
      color="blue-grey-darken-2"
      icon-color="white"
      size="small"
      @completed="$emit('completed')"
    />
    <UtilsDeleteButton
      v-if="autz.isAuditor()"
      :id="target.id"
      key="3"
      :api="api"
      :text="`Target '${target.target}' will be removed`"
      icon="mdi-trash-can"
      variant="flat"
      color="red"
      icon-color="white"
      @completed="$emit('completed')"
    />
  </v-speed-dial>
</template>

<script setup lang="ts">
defineProps({ target: Object, api: Object });
defineEmits(["completed"]);
const route = useRoute();
const autz = useAutz();
</script>

<template>
  <MenuProject>
    <DialogNote v-if="note" :note="note" />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const note = ref();
useApi("/api/notes/", true)
  .get(route.params.note_id)
  .then((response) => (note.value = response));
// TODO: Receive the note from notes page, while the data is loaded from the API
</script>

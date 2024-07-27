<template>
  <MenuProject>
    <DialogNote v-if="note" :note="note" />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const note = ref(null);
useApi("/api/notes/", true, "Note")
  .get(route.params.note_id)
  .then((response) => (note.value = response));
</script>

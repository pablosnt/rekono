<template>
  <v-chip
    v-if="note.forked_from"
    prepend-icon="mdi-arrow-decision"
    append-icon="mdi-open-in-new"
    color="red"
    variant="flat"
    link
    :href="`/projects/${note.project}/notes/${note.forked_from}`"
    >Forked</v-chip
  >
</template>

<script setup lang="ts">
defineProps({ note: Object });
</script>

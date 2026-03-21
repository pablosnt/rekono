<template>
  <!-- todo: Breadcrum with notes info -->
  <div>{{ $route.params.note_id }}</div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "project" });
</script>

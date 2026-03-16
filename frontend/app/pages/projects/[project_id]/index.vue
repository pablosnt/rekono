<template>
  <h1>Project ID: {{ $route.params.project_id }}</h1>
  <!-- todo: show name, description and tags. Edit & delete. DefectDojo synchronization management. Show summary via counters or something to fill space -->
</template>

<script setup lang="ts">
definePageMeta({ layout: "project" });
</script>

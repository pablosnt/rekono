<template>
  <h1>Project ID: {{ $route.params.project_id }}</h1>
</template>

<script setup lang="ts">
definePageMeta({ layout: "project" });
</script>

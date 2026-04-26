<template>
  <div class="flex flex-row flex-wrap mt-6 items-start justify-around w-full">
    <FindingsCounterSingle
      class="w-60 h-40"
      :project-id="project"
      finding-name-plural="OSINT"
    />
    <FindingsCounterSingle
      class="w-60 h-40"
      :project-id="project"
      finding-name-plural="Paths"
    />
    <FindingsCounterSingle
      class="w-60 h-40"
      :project-id="project"
      finding-name-plural="Credentials"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-6">
    <FindingsCounterSingle
      class="h-40"
      :project-id="project"
      finding-name-plural="OSINT"
      only-active
      is-triageable
    />
    <FindingsCounterSingle
      class="h-40"
      :project-id="project"
      finding-name-plural="Paths"
      only-active
    />
    <FindingsCounterSingle
      class="h-40"
      :project-id="project"
      finding-name-plural="Credentials"
      only-active
      is-triageable
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>

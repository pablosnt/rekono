<template>
  <div class="flex flex-row flex-wrap mt-6 items-start justify-around w-full">
    <FindingsCounterSingle
      class="w-60 h-40"
      :project-id="project"
      finding-name-plural="OSINT"
      only-active
      is-triageable
    />
    <FindingsCounterSingle
      class="w-60 h-40"
      :project-id="project"
      finding-name-plural="Paths"
      only-active
    />
    <FindingsCounterSingle
      class="w-60 h-40"
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

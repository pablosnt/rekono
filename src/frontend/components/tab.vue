<template>
  <v-tabs align-tabs="center" fixed-tabs>
    <v-tab
      v-for="o in options"
      :key="o"
      :text="o.title"
      :icon="o.icon"
      :to="o.to"
      color="red-darken-2"
    />
  </v-tabs>
  <v-tabs-window>
    <slot />
  </v-tabs-window>
</template>

<script setup lang="ts">
defineProps({ options: Array<object> });
</script>

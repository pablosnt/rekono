<template>
  <NuxtLayout name="header">
    <v-navigation-drawer expand-on-hover rail class="position-fixed">
      <v-list color="transparent" active-class="text-red">
        <v-list-item
          v-for="o in options"
          :key="o"
          :title="o.title"
          :prepend-icon="o.icon"
          :to="o.to"
          :active="o.to === route.path || route.path.startsWith(o.to)"
        />
      </v-list>
      <!-- TODO: Link to home and all projects in the bottom -->
    </v-navigation-drawer>
    <v-main>
      <slot />
    </v-main>
  </NuxtLayout>
</template>

<script setup lang="ts">
defineProps({ options: Array<object> });
const route = useRoute();
</script>

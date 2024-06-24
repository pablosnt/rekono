<template>
  <NuxtLayout name="header">
    <v-navigation-drawer expand-on-hover rail>
      <v-list color="transparent" active-class="text-red">
        <v-list-item
          v-for="o in options"
          :key="o"
          :title="o.title"
          :prepend-icon="o.icon"
          :to="o.to"
        />
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <slot />
    </v-main>
  </NuxtLayout>
</template>

<script setup lang="ts">
defineProps({ options: Array<object> });
</script>

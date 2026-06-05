<template>
  <UPageSection title="Integrations">
    <UMarquee>
      <div
        v-for="integration in integrations"
        :key="integration.id"
        class="flex flex-col items-center gap-2"
      >
        <UAvatar :src="integration.icon" :alt="integration.name" size="xl" />
        <span>{{ integration.name }}</span>
      </div>
    </UMarquee>
  </UPageSection>
</template>

<script setup lang="ts">
import type { Integration } from "~/types/models";

defineProps<{ integrations: Integration[] }>();
</script>

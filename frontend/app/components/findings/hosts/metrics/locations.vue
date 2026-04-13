<template>
  <VisSingleContainer :data="data">
    <VisTopoJSONMap
      :topojson="WorldMapTopoJSON"
      :point-label="(d) => d.label"
    />
  </VisSingleContainer>
</template>

<script setup lang="ts">
import { VisSingleContainer, VisTopoJSONMap } from "@unovis/vue";
import { WorldMapTopoJSON } from "@unovis/ts/maps";
import type { Host } from "~/types/models";
import { hostOS } from "~/constants";

const props = defineProps<{ hosts: Host[] }>();
const data = computed(() => {
  return {
    points: props.hosts
      .filter((h) => Boolean(h.latitude) && Boolean(h.longitude))
      .map((h) => {
        return {
          id: h.id,
          latitude: h.latitude,
          longitude: h.longitude,
          label: h.domain || h.ip || h.city,
          color: `var(--color-${hostOS.find((o) => o.value === h.os_type)?.color}-500)`,
        };
      }),
  };
});
</script>

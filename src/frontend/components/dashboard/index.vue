<template>
  <v-card v-if="ready" rounded="0" flat>
    <v-window
      v-model="tab"
      show-arrows="hover"
      continuous
      @update:model-value="
        forceReload++;
        router.replace({ query: { dashboard: tab } });
      "
    >
      <v-window-item
        ><DashboardActivity
          :key="forceReload + tab"
          :project="project"
          :target="target"
      /></v-window-item>
      <v-window-item
        ><DashboardAssets
          :key="forceReload + tab"
          :project="project"
          :target="target"
          :height="height"
      /></v-window-item>
      <v-window-item
        ><DashboardVulnerabilities
          :key="forceReload + tab"
          :project="project"
          :target="target"
          :height="height"
      /></v-window-item>
      <v-window-item
        ><DashboardTriaging
          :key="forceReload + tab"
          :project="project"
          :target="target"
          :height="height"
      /></v-window-item>
    </v-window>
    <v-card-actions class="justify-center">
      <v-item-group
        v-model="tab"
        class="text-center"
        mandatory
        @update:model-value="
          forceReload++;
          router.replace({ query: { dashboard: tab } });
        "
      >
        <v-item
          v-for="n in 4"
          :key="`btn-${n}`"
          v-slot="{ isSelected, toggle }"
          :value="n - 1"
        >
          <v-btn
            :variant="isSelected ? 'outlined' : 'text'"
            icon="mdi-record"
            @click="toggle"
          />
        </v-item>
      </v-item-group>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
const route = useRoute();
const router = useRouter();
const tab = ref(
  route.query.dashboard !== undefined &&
    [0, 1, 2, 3, 4].includes(parseInt(route.query.dashboard))
    ? parseInt(route.query.dashboard)
    : 0,
);
const ready = ref(false);
const height = ref("450");
const project = ref(null);
const target = ref(null);
const forceReload = ref(0);

if (route.params.target_id) {
  useApi("/api/targets/", true)
    .get(route.params.target_id)
    .then((response) => {
      target.value = response;
      ready.value = true;
    });
} else if (route.params.project_id) {
  useApi("/api/projects/", true)
    .get(route.params.project_id)
    .then((response) => {
      project.value = response;
      ready.value = true;
    });
} else {
  ready.value = true;
}
</script>

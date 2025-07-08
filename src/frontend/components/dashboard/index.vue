<template>
  <v-card v-if="ready" rounded="0" flat>
    <v-window
      v-model="page"
      show-arrows="hover"
      continuous
      @update:model-value="router.replace({ query: { page: page } })"
    >
      <v-window-item
        v-for="dashboard in dashboards"
        :key="dashboard.toString()"
      >
        <component
          :is="dashboard"
          :project="project"
          :target="target"
          :height="height"
        />
      </v-window-item>
    </v-window>
    <v-card-actions class="justify-center">
      <v-item-group
        v-model="page"
        class="text-center"
        mandatory
        @update:model-value="router.replace({ query: { page: page } })"
      >
        <v-item
          v-for="n in dashboards.length"
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
const ready = ref(false);
const height = ref("450");
const project = ref(null);
const target = ref(null);
const dashboards = ref([
  resolveComponent("DashboardActivity"),
  resolveComponent("DashboardAssets"),
  resolveComponent("DashboardAssetsEvolution"),
  resolveComponent("DashboardVulnerabilities"),
  resolveComponent("DashboardVulnerabilitiesEvolution"),
  resolveComponent("DashboardTriaging"),
]);
const page = ref(0);
if (route.query.page !== undefined) {
  const value = parseInt(route.query.page);
  if (value >= 0 && value < dashboards.value.length) {
    page.value = value;
  }
}

if (route.params.target_id) {
  useApi("/api/targets/", true)
    .get(route.params.target_id)
    .then((response) => {
      target.value = response;
      ready.value = true;
    });
}
if (route.params.project_id) {
  useApi("/api/projects/", true)
    .get(route.params.project_id)
    .then((response) => {
      project.value = response;
      ready.value = true;
    });
}
if (!route.params.target_id && !route.params.project_id) {
  ready.value = true;
}
</script>

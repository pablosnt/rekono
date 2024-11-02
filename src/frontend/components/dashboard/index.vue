<template>
  <v-card rounded="0" flat>
    <v-window v-model="tab" show-arrows="hover" continuous>
      <v-window-item
        ><DashboardActivity :project="project" :target="target"
      /></v-window-item>
      <v-window-item
        ><DashboardAssets :project="project" :target="target"
      /></v-window-item>
    </v-window>
    <!-- <v-card-actions class="justify-center">
      <v-item-group v-model="tab" class="text-center" mandatory>
        <v-item
          v-for="n in 2"
          :key="`btn-${n}`"
          v-slot="{ isSelected, toggle }"
          :value="n"
        >
          <v-btn
            :variant="isSelected ? 'outlined' : 'text'"
            icon="mdi-record"
            @click="toggle"
          ></v-btn>
        </v-item>
      </v-item-group>
    </v-card-actions> -->
  </v-card>
</template>

<script setup lang="ts">
const route = useRoute();
const tab = ref(0);
const project = ref(null);
const target = ref(null);

if (route.params.target_id) {
  useApi("/api/targets/", true)
    .get(route.params.target_id)
    .then((response) => (target.value = response));
} else if (route.params.project_id) {
  useApi("/api/project/", true)
    .get(route.params.project_id)
    .then((response) => (project.value = response));
}
</script>

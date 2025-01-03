<template>
  <v-card
    v-if="target"
    :title="target.target"
    :subtitle="target.type"
    elevation="0"
    variant="text"
    class="ma-3"
    density="comfortable"
    :prepend-icon="enums.targets[target.type].icon"
  >
    <template #append>
      <TaskButton v-if="project" :project="project" :target="target" />
      <TargetButtonLinks
        :target="target"
        :integration="integration"
        :settings="settings"
        location="bottom center"
      />
      <TargetButtonActions
        :target="target"
        :api="api"
        @completed="navigateTo(`/projects/${route.params.target_id}/targets`)"
      />
    </template>
    <BaseTabs
      :options="[
        {
          title: 'Dashboard',
          icon: 'mdi-chart-box',
          to: `/projects/${route.params.project_id}/targets/${route.params.target_id}/dashboard`,
        },
        {
          title: 'Scope',
          icon: 'mdi-antenna',
          to: `/projects/${route.params.project_id}/targets/${route.params.target_id}/scope`,
        },
        {
          title: 'HTTP Headers',
          icon: 'mdi-web',
          to: `/projects/${route.params.project_id}/targets/${route.params.target_id}/http-headers`,
        },
      ]"
    >
      <v-container fluid>
        <slot />
      </v-container>
    </BaseTabs>
  </v-card>
</template>

<script setup lang="ts">
const route = useRoute();
const enums = useEnums();
const target = ref(null);
const project = ref(null);
const integration = ref({ enabled: false });
const settings = ref({ is_available: false });
const api = useApi("/api/targets/", true, "Target");
api.get(route.params.target_id).then((response) => (target.value = response));
useApi("/api/projects/", true)
  .get(parseInt(route.params.project_id))
  .then((response) => (project.value = response));
useApi("/api/integrations/", true)
  .get(1)
  .then((integrationResponse) => {
    integration.value = integrationResponse;
  });
useApi("/api/defect-dojo/settings/", true)
  .get(1)
  .then((settingsResponse) => {
    settings.value = settingsResponse;
  });
</script>

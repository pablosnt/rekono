<template>
  <DashboardWindow
    title="Assets"
    subtitle="Evolution"
    :icon="enums.findings.Host.icon"
    icon-color="indigo"
    :project="project"
    :target="target"
    :loading="loading"
  >
    <v-container v-if="stats" fluid>
      <v-row justify="center">
        <v-col>
          <!-- TODO: General implementation of data series calculation from evolution response -->
          <apexchart
            type="area"
            :series="[
              {
                name: 'Hosts',
                data: dates.map((date) => {
                  const search = stats.hosts.filter(
                    (item) => item.date === date,
                  );
                  return {
                    y: search.length > 0 ? search[0].count : 0,
                    x: new Date(date).getTime(),
                  };
                }),
              },
              {
                name: 'Ports',
                data: dates.map((date) => {
                  const search = stats.ports.filter(
                    (item) => item.date === date,
                  );
                  return {
                    y: search.length > 0 ? search[0].count : 0,
                    x: new Date(date).getTime(),
                  };
                }),
              },
            ]"
            :options="{
              title: { test: 'Assets along the last year' },
              chart: {
                stacked: true,
              },
              animations: {
                enabled: true,
                speed: 800,
                animateGradually: {
                  enabled: true,
                  delay: 150,
                },
                dynamicAnimation: {
                  enabled: true,
                  speed: 350,
                },
              },
              xaxis: {
                type: 'datetime',
              },
              dataLabels: {
                enabled: false,
              },
              stroke: {
                curve: 'straight',
              },
              fill: {
                type: 'gradient',
                gradient: {
                  opacityFrom: 0.6,
                  opacityTo: 0.8,
                },
              },
            }"
            height="800"
          />
        </v-col>
      </v-row>
    </v-container>
  </DashboardWindow>
</template>

<script setup lang="ts">
const props = defineProps({
  project: {
    type: Object,
    required: false,
    default: null,
  },
  target: {
    type: Object,
    required: false,
    default: null,
  },
  height: String,
});
const enums = useEnums();
const api = useApi("/api/stats/assets/evolution/", true);
const stats = ref(null);
const loading = ref(true);
const dates = ref([]);

api
  .get(
    null,
    props.project || props.target
      ? `?${props.target ? `target=${props.target.id}` : `project=${props.project.id}`}`
      : null,
  )
  .then((response) => {
    stats.value = response;
    dates.value = [
      ...new Set(
        response.hosts
          .map((item) => item.date)
          .concat(response.ports.map((item) => item.date)),
      ),
    ];
    loading.value = false;
  });
</script>

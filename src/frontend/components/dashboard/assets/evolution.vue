<template>
  <DashboardWindow
    :api="api"
    title="Assets"
    subtitle="Evolution"
    :icon="enums.findings.Host.icon"
    icon-color="indigo"
    :project="project"
    :target="target"
    @stats="
      (data) => {
        stats = data;
        dates = [
          ...new Set(
            data.hosts
              .map((item) => item.date)
              .concat(data.ports.map((item) => item.date)),
          ),
        ];
      }
    "
  >
    <v-container v-if="stats" fluid>
      <v-row justify="center">
        <v-col>
          <apexchart
            type="area"
            :series="[
              {
                name: 'Hosts',
                data: serie(stats.hosts),
              },
              {
                name: 'Ports',
                data: serie(stats.ports),
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
defineProps({
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
const dates = ref([]);

function serie(data) {
  return dates.value.map((date) => {
    const search = data.filter((item) => item.date === date);
    return {
      y: search.length > 0 ? search[0].count : 0,
      x: new Date(date).getTime(),
    };
  });
}
</script>

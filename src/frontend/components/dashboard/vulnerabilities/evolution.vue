<template>
  <DashboardWindow
    :api="api"
    title="Vulnerabilities"
    subtitle="Evolution"
    :icon="enums.findings.Vulnerability.icon"
    icon-color="red"
    :project="project"
    :target="target"
    @stats="
      (data) => {
        stats = data;
        dates = [...new Set(data.evolution.map((item) => item.date))];
      }
    "
  >
    <template #append>
      <v-btn variant="text" icon>
        <v-icon color="info" icon="$info" />
        <v-tooltip
          activator="parent"
          text="Vulnerabilities fixed and detected again are shown as exposed from the first detection"
        />
      </v-btn>
    </template>
    <template #default>
      <v-container v-if="stats" fluid>
        <v-row justify="center">
          <v-col>
            <apexchart
              type="area"
              :series="
                Object.keys(enums.severity).map((severity) => {
                  return {
                    name: severity,
                    data: dates.map((date) => {
                      const search = stats.evolution.filter(
                        (item) =>
                          item.date === date && item.severity === severity,
                      );
                      return {
                        y: search.length > 0 ? search[0].count : 0,
                        x: new Date(date).getTime(),
                      };
                    }),
                  };
                })
              "
              :options="{
                title: { test: 'Vulnerabilities along the last year' },
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
                colors: Object.keys(enums.severity).map(
                  (severity) => enums.severity[severity].dashboard,
                ),
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
    </template>
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
const api = useApi("/api/stats/vulnerabilities/evolution/", true);
const stats = ref(null);
const dates = ref([]);
</script>

<template>
  <DashboardWindow
    title="Assets"
    :icon="enums.findings.Host.icon"
    icon-color="indigo"
    :project="project"
    :target="target"
    :loading="loading"
  >
    <v-container v-if="stats" fluid>
      <v-row justify="space-around">
        <v-col cols="5">
          <apexchart
            type="radar"
            :series="[
              {
                name: 'Hosts',
                data: os_types.map((os_type) => {
                  const search = stats.os_distribution.filter(
                    (item) => item.os_type === os_type,
                  );
                  return search.length > 0 ? search[0].count : 0;
                }),
              },
            ]"
            :options="{
              title: { text: 'Assets per OS' },
              chart: {
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
              },

              dataLabels: {
                enabled: true,
                background: {
                  enabled: true,
                  borderRadius: 2,
                },
              },
              labels: os_types,
              colors: ['#F44336'],
            }"
            :height="height"
          />
        </v-col>
        <v-col cols="6">
          <apexchart
            type="treemap"
            :series="[
              {
                name: 'services',
                data: stats.services_distribution.map((item) => {
                  return {
                    x: `${item.protocol} ${item.port} ${item.service}`,
                    y: item.count,
                  };
                }),
              },
            ]"
            :options="{
              title: { text: 'Ports & Services' },
              chart: {
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
              },
              plotOptions: { treemap: { distributed: true } },
            }"
            :height="height"
          />
        </v-col>
      </v-row>
      <v-row justify="space-around">
        <v-col cols="5">
          <apexchart
            type="treemap"
            :series="[
              {
                name: 'technologies',
                data: stats.technologies_distribution.map((item) => {
                  return {
                    x: item.name,
                    y: item.count,
                  };
                }),
              },
            ]"
            :options="{
              title: { text: 'Technologies' },
              chart: {
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
              },
              plotOptions: { treemap: { distributed: true } },
            }"
            :height="height"
          />
        </v-col>
        <v-col cols="6">
          <apexchart
            type="bar"
            :series="[
              {
                name: 'Critical',
                group: 'current',
                data: stats.top_vulnerable.map(
                  (item) => item.vulnerabilities_critical,
                ),
              },
              {
                name: 'High',
                group: 'current',
                data: stats.top_vulnerable.map(
                  (item) => item.vulnerabilities_high,
                ),
              },
              {
                name: 'Medium',
                group: 'current',
                data: stats.top_vulnerable.map(
                  (item) => item.vulnerabilities_medium,
                ),
              },
              {
                name: 'Low',
                group: 'current',
                data: stats.top_vulnerable.map(
                  (item) => item.vulnerabilities_low,
                ),
              },
              {
                name: 'Fixed',
                group: 'fixed',
                data: stats.top_vulnerable.map(
                  (item) => item.fixed_vulnerabilities,
                ),
              },
            ]"
            :options="{
              title: { text: 'Assets with more vulnerabilities' },
              chart: { stacked: true },
              tooltip: {
                shared: true,
                intersect: false,
              },
              dataLabels: {
                formatter: (value) => {
                  return value > 1000
                    ? Math.floor(value / 1000).toString() + 'k'
                    : value;
                },
              },
              plotOptions: {
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
                bar: { horizontal: true },
              },
              colors: [
                enums.severity.Critical.dashboard,
                enums.severity.High.dashboard,
                enums.severity.Medium.dashboard,
                enums.severity.Low.dashboard,
                '#4CAF50',
              ],
              xaxis: {
                categories: stats.top_vulnerable.map((item) => item.address),
                labels: {
                  formatter: (value) => {
                    return value > 1000
                      ? Math.floor(value / 1000).toString() + 'k'
                      : value;
                  },
                },
              },
            }"
            :height="height"
          />
          <!-- todo: Composable to divide by 1000 -->
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
const api = useApi("/api/stats/assets/", true);
const stats = ref(null);
const os_types = Object.keys(enums.osType);
const loading = ref(true);

api
  .get(
    null,
    props.project || props.target
      ? `?${props.target ? props.target.id : props.project.id}`
      : null,
  )
  .then((response) => {
    stats.value = response;
    loading.value = false;
  });
</script>

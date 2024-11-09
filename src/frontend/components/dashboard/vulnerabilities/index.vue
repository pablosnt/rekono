<template>
  <DashboardWindow
    :api="api"
    title="Vulnerabilities"
    :icon="enums.findings.Vulnerability.icon"
    icon-color="red"
    :project="project"
    :target="target"
    @stats="(data) => (stats = data)"
  >
    <template #extra-append>
      <v-switch
        v-model="fixed"
        class="mr-3 mt-5"
        color="green"
        label="Fix stats"
      />
    </template>
    <template #default>
      <v-container v-if="stats" fluid>
        <v-row justify="space-between">
          <v-col>
            <apexchart
              type="radialBar"
              :series="
                stats.fix_progress_per_severity.map((item) =>
                  item.progress.toFixed(2),
                )
              "
              :options="{
                title: { text: 'Fixing Progress' },
                subtitle: {
                  text: 'Percentage of fixed vulnerabilities per severity',
                },
                labels: stats.fix_progress_per_severity.map(
                  (item) => item.severity,
                ),
                colors: stats.fix_progress_per_severity.map(
                  (item) => enums.severity[item.severity].dashboard,
                ),
                legend: {
                  show: true,
                },
                plotOptions: {
                  radialBar: {
                    dataLabels: {
                      name: {
                        show: true,
                      },
                      value: {
                        show: true,
                        fontSize: '14px',
                        formatter: function (val) {
                          return val + ' %';
                        },
                      },
                      total: {
                        show: true,
                        label: 'Total',
                        formatter: () => {
                          return stats.fix_progress + ' %';
                        },
                      },
                    },
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
                },
              }"
              :height="height"
            />
          </v-col>
          <v-col>
            <apexchart
              type="donut"
              :series="
                (fixed
                  ? stats.fixed_severity_distribution
                  : stats.severity_distribution
                ).map((item) => item.count)
              "
              :options="{
                title: {
                  text: fixed
                    ? 'Fixed Vulnerabilities per Severity'
                    : 'Vulnerabilities per Severity',
                },

                labels: (fixed
                  ? stats.fixed_severity_distribution
                  : stats.severity_distribution
                ).map((item) => item.severity),
                colors: (fixed
                  ? stats.fixed_severity_distribution
                  : stats.severity_distribution
                ).map((item) => enums.severity[item.severity].dashboard),

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
                },
              }"
              :height="height"
            />
          </v-col>
        </v-row>
        <v-row justify="space-between">
          <v-col cols="7">
            <apexchart
              type="bar"
              :series="[
                {
                  name: 'Occurrences',
                  data: (fixed ? stats.top_fixed_cve : stats.top_cve).map(
                    (item) => {
                      return {
                        x: item.cve,
                        y: item.count,
                      };
                    },
                  ),
                },
              ]"
              :options="{
                title: {
                  text: fixed ? 'Most Common Fixed CVEs' : 'Most Common CVEs',
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
                colors: fixed
                  ? ['#4CAF50']
                  : stats.top_cve.map(
                      (item) => enums.severity[item.severity_value].dashboard,
                    ),
                xaxis: {
                  labels: {
                    formatter: (value) => {
                      return value > 1000
                        ? Math.floor(value / 1000).toString() + 'k'
                        : value;
                    },
                  },
                },
                chart: {
                  events: {
                    dataPointSelection: function (event, chartContext, opts) {
                      navigateTo(
                        (fixed ? stats.top_fixed_cve : stats.top_cve)[
                          opts.dataPointIndex
                        ].link,
                        { external: true, open: { target: '_blank' } },
                      );
                    },
                  },
                },
              }"
              :height="height"
            />
          </v-col>
          <v-col cols="4">
            <v-card :title="fixed ? 'Trending Fixed CVEs' : 'Trending CVEs'">
              <template #prepend>
                <v-icon
                  :icon="fixed ? 'mdi-fire-off' : 'mdi-fire'"
                  :color="fixed ? 'orange-lighten-3' : 'orange-darken-3'"
                />
              </template>
              <template #text>
                <v-container fluid>
                  <v-row justify="space-around">
                    <v-col
                      v-for="item in fixed
                        ? stats.fixed_trending_cve
                        : stats.trending_cve"
                      :key="item.cve"
                      cols="5"
                    >
                      <v-badge :content="item.count">
                        <v-chip
                          :prepend-icon="
                            enums.severity[item.severity_value].icon
                          "
                          :color="enums.severity[item.severity_value].color"
                          :href="item.link"
                          target="_blank"
                        >
                          {{ item.cve }}
                        </v-chip>
                      </v-badge>
                    </v-col>
                  </v-row>
                </v-container>
              </template>
            </v-card>
          </v-col>
        </v-row>
        <v-row justify="center">
          <v-col>
            <apexchart
              type="treemap"
              :series="[
                {
                  name: 'cwes',
                  data: (fixed
                    ? stats.fixed_cwe_distribution
                    : stats.cwe_distribution
                  ).map((item) => {
                    return {
                      x: item.cwe,
                      y: item.count,
                    };
                  }),
                },
              ]"
              :options="{
                title: { text: fixed ? 'Fixed CWEs' : 'CWEs' },
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
                chart: {
                  events: {
                    dataPointSelection: function (event, chartContext, opts) {
                      navigateTo(
                        `https://cwe.mitre.org/data/definitions/${
                          (fixed
                            ? stats.fixed_cwe_distribution
                            : stats.cwe_distribution)[opts.dataPointIndex].cwe
                            .toLowerCase()
                            .split('-')[1]
                        }.html`,
                        { external: true, open: { target: '_blank' } },
                      );
                    },
                  },
                },
              }"
              :height="height"
            />
            <!-- TODO: composable to get CWE reference -->
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
const api = useApi("/api/stats/vulnerabilities/", true);
const stats = ref(null);
const fixed = ref(false);
</script>

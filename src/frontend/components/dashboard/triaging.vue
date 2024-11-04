<template>
  <DashboardWindow
    title="Triaging"
    icon="mdi-check-all"
    icon-color="green"
    :project="project"
    :target="target"
    :loading="loading"
  >
    <v-container v-if="stats" fluid>
      <v-row justify="space-around">
        <v-col>
          <apexchart
            type="radialBar"
            :series="[stats.fp_rate]"
            :options="{
              title: {
                text: 'False positives rate',
              },
              colors: ['#4CAF50'],
              plotOptions: {
                radialBar: {
                  startAngle: -90,
                  endAngle: 90,
                  track: {
                    background: '#333',
                    startAngle: -90,
                    endAngle: 90,
                  },
                  dataLabels: {
                    name: {
                      show: false,
                    },
                    value: {
                      fontSize: '30px',
                      show: true,
                    },
                  },
                },
              },
              fill: {
                type: 'gradient',
                gradient: {
                  type: 'horizontal',
                  gradientToColors: ['#F44336'],
                  stops: [0, 100],
                },
              },
            }"
            height="700"
          />
        </v-col>
        <v-col>
          <apexchart
            type="donut"
            :series="stats.distribution.map((item) => item.count)"
            :options="{
              title: {
                text: 'Findings per triage status',
              },

              labels: stats.distribution.map((item) => item.status),
              colors: stats.distribution.map(
                (item) => enums.triage[item.status].dashboard,
              ),

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
const api = useApi("/api/stats/triaging/", true);
const stats = ref(null);
const loading = ref(true);

api
  .get(
    null,
    props.project || props.target
      ? `?${props.target ? `target=${props.target.id}` : `project=${props.project.id}`}`
      : null,
  )
  .then((response) => {
    stats.value = response;
    loading.value = false;
  });
</script>

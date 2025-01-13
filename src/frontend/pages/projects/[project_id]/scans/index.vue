<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      icon="mdi-play-network"
      empty-head="No Scans"
      empty-text="There are no scans yet. Run your first one"
      @load-data="(data) => loadData(data)"
    >
      <template #add>
        <TaskButton
          v-if="project && autz.isAuditor()"
          :project="project"
          @reload="dataset.loadData(false)"
        />
      </template>
      <template #item="{ item }">
        <v-card
          :title="item.process ? item.process.name : item.configuration.name"
          :subtitle="
            item.configuration ? item.configuration.tool.name : 'Process'
          "
          elevation="2"
          class="ma-3"
          density="comfortable"
          hover
          :to="`/projects/${route.params.project_id}/scans/${item.id}`"
        >
          <template #prepend>
            <TaskIcon :task="item" />
          </template>
          <template #append>
            <TaskTarget :task="item" />
          </template>
          <template #text>
            <v-container>
              <v-row justify="space-between" dense>
                <v-col v-if="!item.start && item.scheduled_at" cols="6">
                  <span class="text-medium-emphasis mr-2">Scheduled:</span>
                  {{
                    new Date(item.scheduled_at).toLocaleString(undefined, {
                      hour12: false,
                    })
                  }}
                </v-col>
                <v-col v-if="item.start">
                  <span class="text-medium-emphasis mr-2">Time:</span>
                  {{
                    new Date(item.start).toLocaleString(undefined, {
                      hour12: false,
                    })
                  }}
                </v-col>
                <v-col v-if="item.start && item.end && item.duration" cols="6">
                  <span class="text-medium-emphasis mr-2">Duration:</span>
                  {{ item.duration }}
                </v-col>
                <v-col v-if="item.repeat_in && item.repeat_time_unit" cols="6">
                  <span class="text-medium-emphasis">Monitor span:</span>
                  {{ item.repeat_in }}
                  {{ item.repeat_time_unit.toLowerCase() }}
                </v-col>
                <v-col cols="6">
                  <span class="text-medium-emphasis mr-2">Intensity:</span>
                  <v-chip
                    :color="enums.intensities[item.intensity].color"
                    size="x-small"
                  >
                    {{ item.intensity }}
                  </v-chip>
                </v-col>
                <v-col cols="6">
                  <span class="text-medium-emphasis mr-2">Executor:</span>
                  <UtilsOwner :entity="item" field="executor" size="x-small" />
                </v-col>
              </v-row>
            </v-container>
            <v-card-actions>
              <TaskStatus :task="item" />
              <v-spacer />
              <TaskButtonLinks :task="item" />
              <TaskButtonActions
                :api="api"
                :task="item"
                @completed="dataset.loadData(false)"
              />
            </v-card-actions>
          </template>
        </v-card>
      </template>
    </Dataset>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const dates = useDates();
const user = userStore();
const autz = useAutz();
const enums = useEnums();
const filters = useFilters();
const project = ref(null);
useApi("/api/projects/", true)
  .get(route.params.project_id)
  .then((response) => (project.value = response));
const dataset = ref(null);
const api = useApi("/api/tasks/", true, "Scan");

const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Target",
      icon: "mdi-target",
      request: useApi("/api/targets/", true).list(
        { project: route.params.project_id },
        true,
      ),
      fieldValue: "id",
      fieldTitle: "target",
      key: "target",
    },
    {
      type: "autocomplete",
      label: "Process",
      icon: "mdi-robot-angry",
      request: useApi("/api/processes/", true).list({}, true),
      fieldValue: "id",
      fieldTitle: "name",
      key: "process",
      callback: (value, definitions) => {
        const configuration = filters.getDefinitionFromKey(
          "configuration",
          definitions,
        );
        const tool = filters.getDefinitionFromKey("tool", definitions);
        if (value) {
          tool.disabled = true;
          tool.value = null;
          configuration.disabled = true;
          configuration.collection = [];
          configuration.value = null;
        } else {
          tool.disabled = false;
        }
      },
    },
    {
      type: "autocomplete",
      label: "Tool",
      icon: "mdi-rocket",
      enforceIcon: true,
      request: useApi("/api/tools/", true).list({}, true),
      fieldValue: "id",
      fieldTitle: "name",
      key: "tool",
      callback: (value, definitions) => {
        const configuration = filters.getDefinitionFromKey(
          "configuration",
          definitions,
        );
        const process = filters.getDefinitionFromKey("process", definitions);
        if (value) {
          process.disabled = true;
          process.value = null;
          useApi("/api/configurations/", true)
            .list({ tool: value }, true)
            .then((response) => {
              configuration.collection = response.items;
              configuration.disabled = false;
              filters.setValueFromQuery(configuration);
            });
        } else {
          process.disabled = false;
          process.value = null;
          configuration.disabled = true;
          configuration.collection = [];
          configuration.value = null;
        }
      },
    },
    {
      type: "autocomplete",
      label: "Configuration",
      icon: "mdi-cog",
      collection: [],
      fieldValue: "id",
      fieldTitle: "name",
      key: "configuration",
      disabled: true,
    },
    {
      type: "autocomplete",
      label: "Stage",
      icon: "mdi-stairs",
      collection: Object.entries(enums.stages).map(([k, v]) => {
        v.name = k;
        return v;
      }),
      fieldValue: "id",
      fieldTitle: "name",
      key: "stage",
    },
    {
      type: "autocomplete",
      label: "Intensity",
      icon: "mdi-volume-high",
      collection: Object.entries(enums.intensities).map(([k, v]) => {
        v.name = k;
        return v;
      }),
      fieldValue: "id",
      fieldTitle: "name",
      key: "intensity",
    },
    {
      type: "switch",
      label: "Mine",
      color: "blue",
      cols: 1,
      key: "executor",
      trueValue: user.user,
      falseValue: null,
    },
    {
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      cols: 2,
      collection: [
        "id",
        "target",
        "process",
        "configuration__tool",
        "configuration",
        "creation",
        "start",
        "end",
      ],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "-id",
    },
  ])
  .then((results) => (filtering.value = results));

function loadData(data: Array<object>): void {
  data.forEach((task) => {
    task.duration =
      task.start && task.end ? dates.getDuration(task.start, task.end) : null;
  });
  if (data.filter((t) => t.status === "Running").length > 0) {
    setTimeout(() => {
      dataset.value.loadData(false);
    }, 10 * 1000);
  }
}
</script>

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
            <v-avatar
              v-if="item.configuration && item.configuration.tool.icon"
              :image="item.configuration.tool.icon"
            />
            <v-icon v-if="item.process" icon="mdi-robot-angry" color="red" />
            <v-icon
              v-if="item.configuration && !item.configuration.tool.icon"
              icon="mdi-rocket"
              color="red"
            />
          </template>
          <template #append>
            <v-chip
              color="red"
              :to="`/projects/${route.params.project_id}/targets/${item.target.id}`"
              target="_blank"
              @click.stop
            >
              <v-icon icon="mdi-target" start />
              {{ item.target.target }}
            </v-chip>
          </template>
          <template #text>
            <v-container fluid>
              <v-row>
                <v-col>
                  <v-container>
                    <v-row class="mb-1">
                      <span class="text-medium-emphasis mr-2">Intensity:</span>
                      <v-chip
                        :color="enums.intensities[item.intensity].color"
                        size="x-small"
                      >
                        {{ item.intensity }}
                      </v-chip>
                    </v-row>
                    <v-row>
                      <span class="text-medium-emphasis mr-2">Executor:</span>
                      <UtilsOwner
                        :entity="item"
                        field="executor"
                        size="x-small"
                      />
                    </v-row>
                  </v-container>
                </v-col>
                <v-col>
                  <v-container>
                    <v-row v-if="!item.start && item.scheduled_at" class="mb-1">
                      <span class="text-medium-emphasis mr-2">Scheduled:</span>
                      {{
                        new Date(item.scheduled_at).toLocaleString(undefined, {
                          hour12: false,
                        })
                      }}
                    </v-row>
                    <v-row v-if="item.start" class="mb-1">
                      <span class="text-medium-emphasis mr-2">Time:</span>
                      {{
                        new Date(item.start).toLocaleString(undefined, {
                          hour12: false,
                        })
                      }}
                    </v-row>
                    <v-row v-if="item.start && item.end && item.duration">
                      <span class="text-medium-emphasis mr-2">Duration:</span>
                      {{ item.duration }}
                    </v-row>
                    <v-row v-if="item.repeat_in && item.repeat_time_unit">
                      <span class="text-medium-emphasis mr-2"
                        >Monitor span:</span
                      >
                      {{ item.repeat_in }}
                      {{ item.repeat_time_unit.toLowerCase() }}
                    </v-row>
                  </v-container>
                </v-col>
              </v-row>
            </v-container>
            <v-card-actions>
              <v-progress-circular
                v-if="item.status && item.status === 'Running'"
                :model-value="item.progress"
                size="50"
                width="5"
                class="mr-3"
                color="amber"
              >
                <template #default>{{ item.progress }}%</template>
              </v-progress-circular>
              <v-chip
                v-if="item.status && item.status !== 'Running'"
                class="mr-3"
                :color="enums.statuses[item.status].color"
              >
                <v-icon :icon="enums.statuses[item.status].icon" start />
                {{ item.status }}
              </v-chip>
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
  for (const task of data) {
    if (task.start && task.end) {
      task.duration = dates.getDuration(task.start, task.end);
    }
  }
  if (data.filter((t) => t.status === "Running").length > 0) {
    setTimeout(() => {
      dataset.value.loadData(false);
    }, 10 * 1000);
  }
}
</script>

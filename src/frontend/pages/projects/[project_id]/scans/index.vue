<template>
  <MenuProject>
    <!-- TODO: Keep Search, Filter and Add button always on the top of the page, and scroll only the data -->
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
          v-if="project"
          :project="project"
          @reload="dataset.loadData(false)"
        />
      </template>
      <template #data>
        <v-row justify="center" dense>
          <v-col v-for="task in tasks" :key="task.id" cols="6">
            <v-card
              :title="
                task.process ? task.process.name : task.configuration.name
              "
              :subtitle="
                task.configuration ? task.configuration.tool.name : 'Process'
              "
              :prepend-avatar="
                task.configuration ? task.configuration.tool.icon : undefined
              "
              hover
              :to="`/projects/${route.params.project_id}/scans/${task.id}`"
            >
              <template #prepend>
                <v-icon
                  v-if="task.process"
                  icon="mdi-robot-angry"
                  color="red"
                />
                <v-icon
                  v-if="task.configuration && !task.configuration.tool.icon"
                  icon="mdi-rocket"
                  color="red"
                />
              </template>
              <template #append>
                <v-progress-circular
                  v-if="task.status && task.status === 'Running'"
                  :model-value="task.progress"
                  size="50"
                  width="5"
                  class="mr-3"
                  color="amber"
                >
                  <template #default>{{ task.progress }}%</template>
                </v-progress-circular>
                <v-chip
                  v-if="task.status && task.status !== 'Running'"
                  class="mr-3"
                  :color="enums.statuses[task.status].color"
                >
                  <v-icon :icon="enums.statuses[task.status].icon" start />
                  {{ task.status }}
                </v-chip>
                <v-chip
                  color="red"
                  :to="`/projects/${route.params.project_id}/targets/${task.target.id}`"
                  target="_blank"
                  @click.stop
                >
                  <v-icon icon="mdi-target" start />
                  {{ task.target.target }}
                </v-chip>
              </template>
              <template #text>
                <!-- TODO: show dates in user time zone -> `.toLocaleString(undefined, { hour12: false })`` -->
                <p v-if="!task.start && task.scheduled_at">
                  <span class="text-medium-emphasis">Scheduled:</span>
                  {{ new Date(task.scheduled_at).toUTCString() }}
                </p>
                <p v-if="task.start">
                  <span class="text-medium-emphasis">Time:</span>
                  {{ new Date(task.start).toUTCString() }}
                </p>
                <p v-if="task.start && task.end && task.duration">
                  <span class="text-medium-emphasis">Duration:</span>
                  {{ task.duration }}
                </p>
                <p v-if="task.repeat_in && task.repeat_time_unit">
                  <span class="text-medium-emphasis">Monitor span:</span>
                  {{ task.repeat_in }} {{ task.repeat_time_unit.toLowerCase() }}
                </p>
                <div>
                  <v-divider class="mt-4 mb-4" />
                  <div class="d-flex flex-row justify-center ga-2">
                    <v-chip
                      class="mt-4"
                      :color="enums.intensities[task.intensity].color"
                    >
                      {{ task.intensity }}
                    </v-chip>
                    <UtilsCounter
                      :collection="task.wordlists"
                      tooltip="Wordlists used"
                      icon="mdi-file-word-box"
                      link="/toolkit/wordlists"
                      color="blue-grey"
                      new-tab
                    />
                    <UtilsCounter
                      :collection="task.notes"
                      tooltip="Notes"
                      icon="mdi-notebook"
                      :link="`/projects/${route.params.project_id}/notes`"
                      color="indigo-darken-1"
                      new-tab
                    />
                    <UtilsCounter
                      :collection="task.reports"
                      tooltip="Reports"
                      icon="mdi-file-document-multiple"
                      :link="`/projects/${route.params.project_id}/reports`"
                      color="blue-grey-darken-1"
                      new-tab
                    />
                    <UtilsOwner class="mt-4" :entity="task" field="executor" />
                  </div>
                </div>
              </template>
              <v-card-actions>
                <v-btn
                  v-if="task.status && task.progress === 100"
                  icon
                  variant="text"
                  @click.prevent.stop="
                    api
                      .create({}, task.id, 'repeat/')
                      .then((response) =>
                        navigateTo(
                          `/projects/${route.params.project_id}/scans/${response.id}`,
                        ),
                      )
                  "
                >
                  <v-icon icon="mdi-repeat" color="green" />
                  <v-tooltip activator="parent" text="Re-run" />
                </v-btn>
                <UtilsButtonDelete
                  v-if="
                    task.status &&
                    task.progress < 100 &&
                    task.status !== 'Cancelled'
                  "
                  :id="task.id"
                  :api="api"
                  :text="`Task '${task.title}' will be cancelled`"
                  action="Cancel"
                  @click.prevent.stop
                  @completed="dataset.loadData(false)"
                />
                <v-spacer />
                <NoteButton :project="route.params.project_id" :task="task" />
                <ReportButton :project="route.params.project_id" :task="task" />
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const dates = useDates();
const utils = useTasks();
const user = userStore();
const enums = ref(useEnums());
const filters = useFilters();
const project = ref(null);
useApi("/api/projects/", true)
  .get(route.params.project_id)
  .then((response) => (project.value = response));
const dataset = ref(null);
const api = useApi("/api/tasks/", true, "Scan");
const tasks = ref([]);

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
              filters.setValueFromQuery(tasks);
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
      collection: Object.entries(enums.value.stages).map(([k, v]) => {
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
      collection: Object.entries(enums.value.intensities).map(([k, v]) => {
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

function loadData(data) {
  tasks.value = data;
  for (let i = 0; i < tasks.value.length; i++) {
    utils.getTitle(tasks.value[i]);
    if (tasks.value[i].start && tasks.value[i].end) {
      tasks.value[i].duration = dates.getDuration(
        tasks.value[i].start,
        tasks.value[i].end,
      );
    }
  }
  if (tasks.value.filter((t) => t.status === "Running").length > 0) {
    setTimeout(() => {
      dataset.value.loadData(false);
    }, 10 * 1000);
  }
}
</script>

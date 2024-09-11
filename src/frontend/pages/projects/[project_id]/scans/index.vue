<template>
  <MenuProject>
    <!-- todo: Keep Search, Filter and Add button always on the top of the page, and scroll only the data -->
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      ordering="-id"
      icon="mdi-play-network"
      empty-head="No Scans"
      empty-text="There are no scans yet. Run your first one"
      @load-data="(data) => loadData(data)"
      @new-filter="
        (key, value) =>
          key === 'tool'
            ? filterByTool(value)
            : key === 'process'
              ? filterByProcess(value)
              : null
      "
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
              :prepend-icon="task.process ? 'mdi-robot-angry' : undefined"
              hover
              :to="`/project/${route.params.project_id}/scans/${task.id}`"
            >
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
                <!-- todo: show dates in user time zone -> `.toLocaleString(undefined, { hour12: false })`` -->
                <p v-if="task.start">
                  <span class="text-medium-emphasis">Time:</span>
                  {{ new Date(task.start).toUTCString() }}
                </p>
                <p v-if="task.start && task.end">
                  <span class="text-medium-emphasis">Duration:</span>
                  {{ task.duration }}
                </p>
                <p v-if="task.repeat_in && task.repeat_time_unit">
                  <span class="text-medium-emphasis">Monitor Span:</span>
                  {{ task.repeat_in }} {{ task.repeat_time_unit.toLowerCase() }}
                </p>
                <div>
                  <v-divider class="mt-4 mb-4" />
                  <div class="d-flex flex-row justify-center ga-2">
                    <v-chip :color="enums.intensities[task.intensity].color">
                      {{ task.intensity }}
                    </v-chip>
                    <UtilsChipCounter
                      :collection="task.wordlists"
                      entity="Wordlists Used"
                      icon="mdi-file-word-box"
                      link="/toolkit/wordlists"
                      color="blue-grey"
                      new-tab
                    />
                    <UtilsChipCounter
                      :collection="task.notes"
                      entity="Notes"
                      icon="mdi-notebook"
                      :link="`/projects/${route.params.project_id}/notes`"
                      color="indigo-darken-1"
                      new-tab
                    />
                    <UtilsChipCounter
                      :collection="task.reports"
                      entity="Reports"
                      icon="mdi-file-document-multiple"
                      :link="`/projects/${route.params.project_id}/reports`"
                      color="blue-grey-darken-1"
                      new-tab
                    />
                    <UtilsChipOwner :entity="task" field="executor" />
                  </div>
                </div>
              </template>
              <v-card-actions>
                <v-btn
                  v-if="task.status && task.progress === 100"
                  icon="mdi-repeat"
                  color="green"
                  @click.prevent.stop="
                    api
                      .create({}, task.id, 'repeat/')
                      .then((response) =>
                        navigateTo(
                          `/projects/${route.params.project_id}/scans/${response.id}`,
                        ),
                      )
                  "
                />
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
const utils = useUtils();
const user = userStore();
const enums = ref(useEnums());
const project = ref(null);
useApi("/api/projects/", true)
  .get(route.params.project_id)
  .then((response) => (project.value = response));
const dataset = ref(null);
const api = useApi("/api/tasks/", true, "Scan");
const tasks = ref([]);

const filtering = ref([
  {
    type: "autocomplete",
    label: "Target",
    icon: "mdi-target",
    collection: [],
    fieldValue: "id",
    fieldTitle: "target",
    key: "target",
    value: null,
  },
  {
    type: "autocomplete",
    label: "Process",
    icon: "mdi-robot-angry",
    collection: [],
    fieldValue: "id",
    fieldTitle: "name",
    key: "process",
    value: null,
  },
  {
    type: "autocomplete",
    label: "Tool",
    icon: "mdi-rocket",
    enforceIcon: true,
    collection: [],
    fieldValue: "id",
    fieldTitle: "name",
    key: "tool",
    value: null,
  },
  {
    type: "autocomplete",
    label: "Configuration",
    icon: "mdi-cog",
    collection: [],
    fieldValue: "id",
    fieldTitle: "name",
    key: "configuration",
    value: null,
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
    value: null,
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
    value: null,
  },
  {
    type: "switch",
    label: "Mine",
    color: "blue",
    cols: 1,
    key: "executor",
    trueValue: user.user,
    falseValue: null,
    value: null,
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
    value: "id",
  },
]);

useApi("/api/targets/", true)
  .list({}, true)
  .then((response) => {
    filtering.value[0].collection = response.items;
  });

useApi("/api/processes/", true)
  .list({}, true)
  .then((response) => {
    filtering.value[1].collection = response.items;
  });

useApi("/api/tools/", true)
  .list({}, true)
  .then((response) => {
    filtering.value[2].collection = response.items;
  });

function filterByProcess(process) {
  if (process) {
    filtering.value[2].disabled = true;
    filtering.value[3].disabled = true;
    filtering.value[3].collection = [];
  } else {
    filtering.value[2].disabled = false;
  }
}

function filterByTool(tool) {
  if (tool) {
    filtering.value[1].disabled = true;
    useApi("/api/configurations/", true)
      .list({ tool: tool }, true)
      .then((response) => {
        filtering.value[3].collection = response.items;
        filtering.value[3].disabled = false;
      });
  } else {
    filtering.value[1].disabled = false;
    filtering.value[3].disabled = true;
    filtering.value[3].collection = [];
  }
}

function loadData(data) {
  tasks.value = data;
  let autoreload = false;
  for (let i = 0; i < tasks.value.length; i++) {
    utils.getTaskTitle(tasks.value[i]);
    utils.getTaskStatus(tasks.value[i]);
    utils.getTaskDuration(tasks.value[i]);
    if (tasks.value[i].status === "Running") {
      autoreload = true;
    }
  }
  if (autoreload) {
    setTimeout(() => {
      dataset.value.loadData(false);
    }, 10 * 1000);
  }
}
</script>

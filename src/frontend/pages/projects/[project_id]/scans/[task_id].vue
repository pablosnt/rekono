<template>
  <MenuProject>
    <v-card
      v-if="task"
      class="pa-6"
      :title="task.process ? task.process.name : task.configuration.name"
      :subtitle="task.configuration ? task.configuration.tool.name : 'Process'"
      :prepend-avatar="
        task.configuration ? task.configuration.tool.icon : undefined
      "
      variant="text"
    >
      <template #prepend>
        <v-icon v-if="task.process" icon="mdi-robot-angry" color="red" />
      </template>
      <template #append>
        <v-btn
          v-if="task.status && task.progress === 100"
          icon
          variant="text"
          @click.prevent.stop="
            apiTasks
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
            task.status && task.progress < 100 && task.status !== 'Cancelled'
          "
          :id="task.id"
          :api="apiTasks"
          :text="`Task '${task.title}' will be cancelled`"
          action="Cancel"
          @click.prevent.stop
          @completed="
            loadExecutions(false);
            loadTask();
          "
        />
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
          class="mr-3"
          color="red"
          :to="`/projects/${route.params.project_id}/targets/${task.target.id}`"
          target="_blank"
          @click.stop
        >
          <v-icon icon="mdi-target" start />
          {{ task.target.target }}
        </v-chip>
        <v-chip :color="enums.intensities[task.intensity].color">
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
        <UtilsOwner :entity="task" field="executor" />
        <NoteButton :project="route.params.project_id" :task="task" />
        <ReportButton :project="route.params.project_id" :task="task" />
      </template>
      <template #text>
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
        <v-divider class="mt-4 mb-4" />
        <!-- todo: progress bars ususally get blocked when API requests are being triggered -->
        <v-progress-linear
          v-if="loading"
          height="5"
          color="red"
          indeterminate
          rounded
        />
        <v-empty-state
          v-if="stages.length === 0"
          icon="mdi-play-network"
          headline="No Executions"
          text="This task doesn't have any execution yet"
        >
          <template #media>
            <v-icon class="mb-3" color="red-darken-4" />
          </template>
        </v-empty-state>
        <div v-if="stages.length > 0" class="d-flex overflow-auto">
          <template
            v-for="(stage, index) in Object.keys(enums.stages).filter(
              (s) => executions[s] !== undefined && executions[s].length > 0,
            )"
            :key="stage"
          >
            <v-container fluid>
              <v-row>
                <!-- TODO: Chip not shown correctly, when number of stages is less than 3 -->
                <v-chip
                  class="mb-3"
                  :text="stage"
                  :prepend-icon="enums.stages[stage].icon"
                  :color="enums.stages[stage].color"
                />
                <v-timeline
                  density="dense"
                  side="end"
                  :truncate-line="
                    index === 0
                      ? 'start'
                      : index === stages.length - 1
                        ? 'end'
                        : undefined
                  "
                >
                  <v-timeline-item
                    v-for="execution in executions[stage]"
                    :key="execution.id"
                    dot-color="white"
                    hide-opposite
                    min-width="550"
                  >
                    <template #icon>
                      <v-progress-circular
                        v-if="
                          execution.status && execution.status === 'Running'
                        "
                        color="amber"
                        width="5"
                        indeterminate
                      />
                      <v-btn
                        v-if="
                          execution.status && execution.status !== 'Running'
                        "
                        icon
                        variant="text"
                        :color="enums.statuses[execution.status].color"
                      >
                        <v-icon
                          :icon="enums.statuses[execution.status].icon"
                          size="x-large"
                        />
                        <v-tooltip
                          activator="parent"
                          :text="execution.status"
                        />
                      </v-btn>
                    </template>

                    <ExecutionShow
                      v-if="['Completed', 'Error'].includes(execution.status)"
                      :api="api"
                      :execution="execution"
                      @click="
                        expand = !expand;
                        expandExecution =
                          !expand ||
                          (expandExecution && expandExecution === execution.id)
                            ? null
                            : execution;
                      "
                    />

                    <ExecutionShow
                      v-if="!['Completed', 'Error'].includes(execution.status)"
                      :api="api"
                      :execution="execution"
                    />
                  </v-timeline-item>
                </v-timeline>
              </v-row>
            </v-container>
          </template>
        </div>
      </template>
    </v-card>
    <v-navigation-drawer
      v-model="expand"
      width="800"
      location="right"
      class="position-fixed"
      temporary
      @update:model-value="!expand ? (expandExecution = null) : null"
    >
      <Dialog
        v-if="expandExecution"
        :title="expandExecution.configuration.name"
        :subtitle="expandExecution.configuration.tool.name"
        :avatar="expandExecution.configuration.tool.icon"
        elevation="0"
        @close-dialog="
          expand = false;
          expandExecution = null;
        "
      >
        <template #extra-append>
          <ExecutionReportButton :api="api" :execution="expandExecution" />
          <UtilsCounter
            :collection="expandExecution.osint"
            :icon="enums.findings.OSINT.icon"
            size="x-large"
            :link="`/projects/${route.params.project_id}/findings?tab=osint&target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="OSINT"
            new-tab
          />
          <UtilsCounter
            :collection="expandExecution.host"
            :icon="enums.findings.Host.icon"
            size="x-large"
            :link="`/projects/${route.params.project_id}/assets?target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="Assets"
            color="indigo"
            new-tab
          />
          <UtilsCounter
            :collection="expandExecution.vulnerability"
            :icon="enums.findings.Vulnerability.icon"
            size="x-large"
            :link="`/projects/${route.params.project_id}/findings?tab=vulnerabilities&target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="Findings"
            new-tab
          />
          <!-- todo: execution filter doesn´t exist yet -->
        </template>
        <v-textarea
          variant="outlined"
          bg-color="grey-darken-4"
          rows="35"
          :value="
            expandExecution.output_error
              ? expandExecution.output_error
              : expandExecution.output_plain
          "
          readonly
        />
      </Dialog>
    </v-navigation-drawer>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const enums = useEnums();
const apiTasks = useApi("/api/tasks/", true);
const api = useApi("/api/executions/", true, "Execution");
const loading = ref(false);
const task = ref(null);
const executions = ref({});
const stages = ref([]);
const expand = ref(false);
const expandExecution = ref(null);
loadExecutions(true);
loadTask();

function loadTask() {
  apiTasks.get(route.params.task_id).then((response) => {
    task.value = response;
    if (["Running", "Requested"].includes(task.value.status)) {
      setTimeout(() => {
        if (!loading.value) {
          loadExecutions(false);
        }
        loadTask();
      }, 10 * 1000);
    }
  });
}

// page: number = 1,
function loadExecutions(showLoading: boolean, stage?: string | null = null) {
  if (showLoading) {
    loading.value = true;
  }
  for (const s of stage !== null ? [stage] : Object.keys(enums.stages)) {
    api
      .list(
        {
          task: route.params.task_id,
          project: route.params.project_id,
          stage: enums.stages[s].id,
          ordering: "start,status,configuration__tool",
        },
        true,
        // false,
        // page,
      )
      .then((response) => {
        // if (page === 1) {
        if (response.items.length > 0) {
          executions.value[s] = response.items;

          stages.value.push(s);
        }
        // } else if (response.items.length > 0) {
        //   executions.value[s] = executions.value[s].concat(response.items);
        // }
        // if (response.items.length === 24) {
        //   loadExecutions(true, page + 1, s);
        // } else {
        loading.value = false;
        // }
      })
      .catch(() => (loading.value = false));
  }
}
// TODO: Loading per stage?
// TODO: Only reload those stages with Running or Requested executions
// TODO: Use automatic next page retrival on user scroll
</script>

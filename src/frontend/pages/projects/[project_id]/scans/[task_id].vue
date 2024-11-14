<template>
  <MenuProject>
    <v-card
      v-if="task"
      class="pa-6"
      :title="task.process ? task.process.name : task.configuration.name"
      :subtitle="task.configuration ? task.configuration.tool.name : 'Process'"
      :prepend-avatar="
        task.configuration && task.configuration.tool.icon
          ? task.configuration.tool.icon
          : undefined
      "
      variant="text"
    >
      <template #prepend>
        <v-icon v-if="task.process" icon="mdi-robot-angry" color="red" />
        <v-icon
          v-if="task.configuration && !task.configuration.tool.icon"
          icon="mdi-rocket"
          color="red"
        />
      </template>
      <template #append>
        <BaseButton
          v-if="task.status && task.progress === 100"
          icon="mdi-repeat"
          icon-color="green"
          tooltip="Re-run"
          @click.prevent.stop="
            apiTasks
              .create({}, task.id, 'repeat/')
              .then((response) =>
                navigateTo(
                  `/projects/${route.params.project_id}/scans/${response.id}`,
                ),
              )
          "
        />
        <UtilsDeleteButton
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
        <UtilsCounterButton
          :collection="task.wordlists"
          tooltip="Wordlists used"
          icon="mdi-file-word-box"
          link="/toolkit/wordlists"
          color="blue-grey"
          new-tab
        />
        <UtilsCounterButton
          :collection="task.notes"
          tooltip="Notes"
          icon="mdi-notebook"
          :link="`/projects/${route.params.project_id}/notes`"
          color="indigo-darken-1"
          new-tab
        />
        <UtilsCounterButton
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
        <!-- TODO: progress bars ususally get blocked when API requests are being triggered -->
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
                <v-chip
                  class="mb-3"
                  :text="stage"
                  :prepend-icon="enums.stages[stage].icon"
                  :color="enums.stages[stage].color"
                />
              </v-row>
              <v-row>
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
                      <BaseButton
                        v-if="
                          execution.status && execution.status !== 'Running'
                        "
                        :icon="enums.statuses[execution.status].icon"
                        icon-size="x-large"
                        :tooltip="execution.status"
                        :color="enums.statuses[execution.status].color"
                      />
                    </template>

                    <v-card
                      :title="execution.configuration.name"
                      :subtitle="execution.configuration.tool.name"
                      variant="outlined"
                      :hover="['Completed', 'Error'].includes(execution.status)"
                      :disabled="
                        !['Completed', 'Error'].includes(execution.status)
                      "
                      :prepend-avatar="
                        execution.configuration.tool.icon
                          ? execution.configuration.tool.icon
                          : undefined
                      "
                      @click="
                        expand = !expand;
                        expandExecution =
                          !expand ||
                          (expandExecution && expandExecution === execution.id)
                            ? null
                            : execution;
                      "
                    >
                      <template
                        v-if="!execution.configuration.tool.icon"
                        #prepend
                      >
                        <v-icon icon="mdi-rocket" color="red" />
                      </template>
                      <template #text>
                        <p v-if="execution.start">
                          <span class="text-medium-emphasis">Time:</span>
                          {{ new Date(execution.start).toUTCString() }}
                        </p>
                        <p v-if="execution.start && execution.end">
                          <span class="text-medium-emphasis">Duration:</span>
                          {{
                            dates.getDuration(execution.start, execution.end)
                          }}
                        </p>

                        <p
                          v-if="
                            execution.status === 'Skipped' &&
                            execution.skipped_reason
                          "
                          class="text-center font-weight-light"
                        >
                          {{ execution.skipped_reason }}
                        </p>
                      </template>
                      <v-card-actions>
                        <ExecutionDownload :api="api" :execution="execution" />
                        <v-spacer />
                        <UtilsCounterButton
                          :collection="execution.osint"
                          :icon="enums.findings.OSINT.icon"
                          size="x-large"
                          :link="`/projects/${route.params.project_id}/findings?tab=osint&target=${task.target.id}&task=${task.id}&execution=${execution.id}`"
                          tooltip="OSINT"
                          new-tab
                        />
                        <UtilsCounterButton
                          :collection="execution.host"
                          :icon="enums.findings.Host.icon"
                          size="x-large"
                          :link="`/projects/${route.params.project_id}/assets?target=${task.target.id}&task=${task.id}&execution=${execution.id}`"
                          tooltip="Assets"
                          color="indigo"
                          new-tab
                        />
                        <UtilsCounterButton
                          :collection="execution.vulnerability"
                          :icon="enums.findings.Vulnerability.icon"
                          size="x-large"
                          :link="`/projects/${route.params.project_id}/findings?tab=vulnerabilities&target=${task.target.id}&task=${task.id}&execution=${execution.id}`"
                          tooltip="Findings"
                          new-tab
                        />
                      </v-card-actions>
                    </v-card>
                  </v-timeline-item>
                  <div
                    v-intersect="
                      (isIntersecting, entries, observer) =>
                        isIntersecting && executions[stage].length % 24 === 0
                          ? loadExecutions(
                              true,
                              stage,
                              executions[stage].length / 24 + 1,
                            )
                          : null
                    "
                  />
                  <v-progress-circular
                    v-if="loadingStages[stage]"
                    color="red"
                    width="5"
                    indeterminate
                  />
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
      <BaseDialog
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
        <template #append>
          <ExecutionDownload :api="api" :execution="expandExecution" />
          <UtilsCounterButton
            :collection="expandExecution.osint"
            :icon="enums.findings.OSINT.icon"
            size="x-large"
            :link="`/projects/${route.params.project_id}/findings?tab=osint&target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="OSINT"
            new-tab
          />
          <UtilsCounterButton
            :collection="expandExecution.host"
            :icon="enums.findings.Host.icon"
            size="x-large"
            :link="`/projects/${route.params.project_id}/assets?target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="Assets"
            color="indigo"
            new-tab
          />
          <UtilsCounterButton
            :collection="expandExecution.vulnerability"
            :icon="enums.findings.Vulnerability.icon"
            size="x-large"
            :link="`/projects/${route.params.project_id}/findings?tab=vulnerabilities&target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="Findings"
            new-tab
          />
          <!-- TODO: execution filter doesn´t exist yet -->
        </template>
        <v-textarea
          variant="outlined"
          bg-color="grey-darken-4"
          rows="30"
          :value="
            expandExecution.output_error
              ? expandExecution.output_error
              : expandExecution.output_plain
          "
          readonly
        />
      </BaseDialog>
    </v-navigation-drawer>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const enums = useEnums();
const dates = useDates();
const apiTasks = useApi("/api/tasks/", true);
const api = useApi("/api/executions/", true, "Execution");
const task = ref(null);
const executions = ref({});
const stages = ref([]);
const expand = ref(false);
const expandExecution = ref(null);
const loadingStages = ref({});
const loading = computed(() => {
  return (
    Object.entries(loadingStages.value).filter(([_, v]) => v === true).length >
    0
  );
});
loadExecutions(true);
loadTask();

function loadTask(): void {
  apiTasks.get(route.params.task_id).then((response) => {
    task.value = response;
    if (["Running", "Requested"].includes(task.value.status)) {
      setTimeout(() => {
        for (const stage of Object.keys(enums.stages)) {
          if (
            !loadingStages.value[stage] &&
            executions.value[stage] &&
            executions.value[stage].filter((e) =>
              ["Running", "Requested"].includes(e.status),
            )
          ) {
            loadExecutions(false, stage);
          }
        }
        loadTask();
      }, 10 * 1000);
    }
  });
}

function loadExecutions(
  showLoading: boolean,
  stage?: string | null = null,
  page: number = 1,
): void {
  for (const s of stage !== null ? [stage] : Object.keys(enums.stages)) {
    if (showLoading) {
      loadingStages.value[s] = true;
    }
    api
      .list(
        {
          task: route.params.task_id,
          project: route.params.project_id,
          stage: enums.stages[s].id,
          ordering: "start,status,configuration__tool",
        },
        false,
        page,
      )
      .then((response) => {
        if (response.items.length > 0) {
          if (page === 1) {
            executions.value[s] = response.items;
            stages.value.push(s);
          } else {
            executions.value[s] = executions.value[s].concat(response.items);
          }
        }
        loadingStages.value[s] = false;
      })
      .catch(() => (loadingStages.value[s] = false));
  }
}
</script>

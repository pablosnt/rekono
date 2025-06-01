<template>
  <MenuProject>
    <v-card
      v-if="task"
      class="pa-6"
      :title="task.process ? task.process.name : task.configuration.name"
      :subtitle="task.configuration ? task.configuration.tool.name : 'Process'"
      variant="text"
    >
      <template #prepend>
        <TaskIcon :task="task" />
      </template>
      <template #append>
        <TaskStatus :task="task" />
        <TaskTarget class="ml-3 mr-3" :task="task" />
        <TaskButtonLinks :task="task" location="bottom center" />
        <TaskButtonActions :task="task" :api="api" />
      </template>
      <template #text>
        <v-container fluid>
          <v-row justify="space-around" dense>
            <v-col cols="2">
              <p v-if="!task.start && task.scheduled_at">
                <span class="text-medium-emphasis">Scheduled:</span>
                {{
                  new Date(task.scheduled_at).toLocaleString(undefined, {
                    hour12: false,
                  })
                }}
              </p>
              <p v-if="task.start">
                <span class="text-medium-emphasis">Time:</span>
                {{
                  new Date(task.start).toLocaleString(undefined, {
                    hour12: false,
                  })
                }}
              </p>
            </v-col>
            <v-col v-if="task.start && task.end && task.duration" cols="2">
              <p>
                <span class="text-medium-emphasis">Duration:</span>
                {{ task.duration }}
              </p>
            </v-col>
            <v-col v-if="task.repeat_in && task.repeat_time_unit" cols="2">
              <p>
                <span class="text-medium-emphasis">Monitor span:</span>
                {{ task.repeat_in }} {{ task.repeat_time_unit.toLowerCase() }}
              </p>
            </v-col>
            <v-col cols="2">
              <span class="text-medium-emphasis mr-2">Intensity:</span>
              <v-chip
                :color="enums.intensities[task.intensity].color"
                size="x-small"
              >
                {{ task.intensity }}
              </v-chip>
            </v-col>
            <v-col cols="2">
              <span class="text-medium-emphasis mr-2">Executor:</span>
              <UtilsOwner :entity="task" field="executor" size="x-small" />
            </v-col>
          </v-row>
          <v-row>
            <v-divider class="mt-4 mb-4" />
            <v-progress-linear
              v-if="loading"
              height="5"
              color="red"
              indeterminate
              rounded
            />
          </v-row>
          <v-row>
            <v-empty-state
              v-if="stages.length === 0"
              icon="mdi-play-network"
              headline="No Executions"
              text="This scan doesn't include any execution yet"
            >
              <template #media>
                <v-icon class="mb-3" color="red-darken-4" />
              </template>
            </v-empty-state>
          </v-row>
          <v-row>
            <div v-if="stages.length > 0" class="d-flex overflow-auto">
              <template
                v-for="(stage, index) in Object.keys(enums.stages).filter(
                  (s) =>
                    executions[s] !== undefined && executions[s].length > 0,
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
                          :hover="
                            ['Completed', 'Error'].includes(execution.status)
                          "
                          :disabled="
                            !['Completed', 'Error'].includes(execution.status)
                          "
                          @click="
                            expand = !expand;
                            expandExecution =
                              !expand ||
                              (expandExecution &&
                                expandExecution === execution.id)
                                ? null
                                : execution;
                          "
                        >
                          <template #prepend>
                            <TaskIcon :task="execution" />
                          </template>
                          <template #text>
                            <v-container fluid>
                              <v-row justify="space-between" dense>
                                <v-col class="text-center">
                                  <p v-if="execution.start">
                                    <span class="text-medium-emphasis"
                                      >Time:</span
                                    >
                                    {{
                                      new Date(execution.start).toLocaleString(
                                        undefined,
                                        { hour12: false },
                                      )
                                    }}
                                  </p>
                                </v-col>
                                <v-col class="text-center">
                                  <p
                                    v-if="
                                      execution.start &&
                                      execution.end &&
                                      execution.duration
                                    "
                                  >
                                    <span class="text-medium-emphasis"
                                      >Duration:</span
                                    >
                                    {{ execution.duration }}
                                  </p>
                                </v-col>
                              </v-row>
                              <v-row
                                v-if="
                                  execution.status === 'Skipped' &&
                                  execution.skipped_reason
                                "
                                class="mt-8 font-weight-light"
                                justify="center"
                                dense
                              >
                                {{ execution.skipped_reason }}
                              </v-row>
                            </v-container>
                          </template>
                          <v-card-actions>
                            <ExecutionDownload
                              :api="api"
                              :execution="execution"
                              icon-size="x-large"
                            />
                            <v-spacer />
                            <UtilsCounterButton
                              :collection="execution.osint"
                              :icon="enums.findings.OSINT.icon"
                              size="large"
                              :link="`/projects/${route.params.project_id}/findings?tab=osint&target=${task.target.id}&task=${task.id}&execution=${execution.id}`"
                              tooltip="OSINT"
                              new-tab
                            />
                            <UtilsCounterButton
                              :collection="execution.host"
                              :icon="enums.findings.Host.icon"
                              size="large"
                              :link="`/projects/${route.params.project_id}/assets?target=${task.target.id}&task=${task.id}&execution=${execution.id}`"
                              tooltip="Assets"
                              color="indigo"
                              new-tab
                            />
                            <UtilsCounterButton
                              :collection="execution.vulnerability"
                              :icon="enums.findings.Vulnerability.icon"
                              size="large"
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
                            isIntersecting &&
                            executions[stage].length % 24 === 0
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
          </v-row>
        </v-container>
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
          <ExecutionDownload
            :api="api"
            :execution="expandExecution"
            icon-size="x-large"
          />
          <UtilsCounterButton
            :collection="expandExecution.osint"
            :icon="enums.findings.OSINT.icon"
            size="large"
            :link="`/projects/${route.params.project_id}/findings?tab=osint&target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="OSINT"
            new-tab
          />
          <UtilsCounterButton
            :collection="expandExecution.host"
            :icon="enums.findings.Host.icon"
            size="large"
            :link="`/projects/${route.params.project_id}/assets?target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="Assets"
            color="indigo"
            new-tab
          />
          <UtilsCounterButton
            :collection="expandExecution.vulnerability"
            :icon="enums.findings.Vulnerability.icon"
            size="large"
            :link="`/projects/${route.params.project_id}/findings?tab=vulnerabilities&target=${task.target.id}&task=${task.id}&execution=${expandExecution.id}`"
            tooltip="Findings"
            new-tab
          />
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
const api = useApi("/api/executions/", true, "Execution");
const apiTasks = useApi("/api/tasks/", true);
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
    if (task.value.start && task.value.end) {
      task.value.duration = dates.getDuration(task.value.start, task.value.end);
    }
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
        response.items.forEach((execution) => {
          execution.duration =
            execution.start && execution.end
              ? dates.getDuration(execution.start, execution.end)
              : null;
        });
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

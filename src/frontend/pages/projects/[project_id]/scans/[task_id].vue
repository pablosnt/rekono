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
          v-if="executions.length === 0"
          icon="mdi-play-network"
          headline="No Executions"
          text="This task doesn't have any execution yet"
        >
          <template #media>
            <v-icon class="mb-3" color="red-darken-4" />
          </template>
        </v-empty-state>
        <div
          v-if="executions.length > 0"
          class="d-flex justify-space-around overflow-x-auto"
        >
          <v-timeline
            v-for="g in task.max_group"
            :key="g"
            density="dense"
            side="end"
            :truncate-line="
              g === 1 ? 'start' : g === task.max_group ? 'end' : undefined
            "
          >
            <v-timeline-item
              v-for="execution in executions.filter((e) => e.group === g)"
              :key="execution.id"
              dot-color="white"
              hide-opposite
              min-width="550"
            >
              <template #icon>
                <v-progress-circular
                  v-if="execution.status && execution.status === 'Running'"
                  color="amber"
                  width="5"
                  indeterminate
                />
                <v-btn
                  v-if="execution.status && execution.status !== 'Running'"
                  icon
                  variant="text"
                  :color="enums.statuses[execution.status].color"
                >
                  <v-icon
                    :icon="enums.statuses[execution.status].icon"
                    size="x-large"
                  />
                  <v-tooltip activator="parent" :text="execution.status" />
                </v-btn>
              </template>
              <v-dialog
                v-if="['Completed', 'Error'].includes(execution.status)"
                width="auto"
              >
              <!-- TODO: Replace dialog by https://vuetifyjs.com/en/components/navigation-drawers/#temporary -->
                <template #activator="{ props: activatorProps }">
                  <ExecutionShow
                    :api="api"
                    :execution="execution"
                    v-bind="activatorProps"
                  />
                </template>
                <template #default="{ isActive }">
                  <Dialog
                    :title="execution.configuration.name"
                    :subtitle="execution.configuration.tool.name"
                    :avatar="execution.configuration.tool.icon"
                    @close-dialog="isActive.value = false"
                  >
                    <template #extra-append>
                      <!-- todo: This is used also in showExecution. Should we create a common component -->
                      <v-btn
                        v-if="
                          execution.status === 'Completed' &&
                          execution.has_report
                        "
                        hover
                        variant="text"
                        icon
                        @click="api.download(execution.id, 'report/', {})"
                      >
                        <v-icon icon="mdi-download" color="primary" />
                        <v-tooltip
                          activator="parent"
                          text="Download original report"
                        />
                      </v-btn>
                      <!-- todo: Set up this as counters. Include osint  -->
                      <UtilsButtonLink
                        icon="mdi-server"
                        size="x-large"
                        :link="`/projects/${route.params.project_id}/assets?target=${task.target.id}&task=${task.id}&execution=${execution.id}`"
                        tooltip="Assets"
                        color="indigo"
                      />
                      <UtilsButtonLink
                        icon="mdi-ladybug"
                        size="x-large"
                        :link="`/projects/${route.params.project_id}/findings?target=${task.target.id}&task=${task.id}&execution=${execution.id}`"
                        tooltip="Findings"
                        color="red"
                      />
                      <!-- todo: execution filter doesn´t exist yet -->
                    </template>
                    <v-textarea
                      variant="outlined"
                      bg-color="grey-darken-4"
                      rows="25"
                      :value="
                        execution.output_error
                          ? execution.output_error
                          : execution.output_plain
                      "
                      readonly
                    />
                  </Dialog>
                </template>
              </v-dialog>
              <ExecutionShow
                v-if="!['Completed', 'Error'].includes(execution.status)"
                :api="api"
                :execution="execution"
              />
            </v-timeline-item>
          </v-timeline>
        </div>
      </template>
    </v-card>
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
const executions = ref([]);
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

function loadExecutions(showLoading: boolean, page: number = 1) {
  if (showLoading) {
    loading.value = true;
  }
  api
    .list(
      {
        task: route.params.task_id,
        project: route.params.project_id,
        ordering: "group,start,status,configuration__tool",
      },
      false,
      page,
    )
    .then((response) => {
      if (page === 1) {
        executions.value = response.items;
      } else if (response.items.length > 0) {
        executions.value = executions.value.concat(response.items);
      }
      if (response.items.length === 24) {
        loadExecutions(true, page + 1);
      } else {
        loading.value = false;
      }
    })
    .catch(() => (loading.value = false));
}
// TODO: Show one timeline per stage. Remove group. Only reload those stages with Running or Requested executions. Don't paginate to keep it simpler for now. Then, if needed, use automatic next page retrival on user scroll
</script>

<template>
  <div class="mt-3">
    <b-row>
      <b-col>
        <label class="text-muted">Target</label>
        <hr/>
        <div v-if="showTaskDetails">
          <p>{{ currentTask.target.target }}</p>
          <b-badge variant="secondary">{{ currentTask.target.type }}</b-badge>
        </div>
      </b-col>
      <b-col>
        <label class="text-muted">Execution</label>
        <hr/>
        <div v-if="showTaskDetails">
          <p v-if="currentTask.process">{{ currentTask.process.name }}</p>
          <p v-if="currentTask.tool">{{ currentTask.tool.name }}</p>
          <p v-if="currentTask.configuration">{{ currentTask.configuration.name }}</p>
          <p v-for="i in intensities" :key="i.value">
            <b-badge v-if="i.intensity_rank === currentTask.intensity_rank" :variant="i.variant">{{ currentTask.intensity_rank }}</b-badge>
          </p>
        </div>
      </b-col>
      <b-col>
        <label class="text-muted">Status</label>
        <hr/>
        <div v-if="showTaskDetails">
          <p v-for="i in statuses" :key="i.value">
            <b-badge v-if="i.value === currentTask.status" :variant="i.variant">{{ currentTask.status }}</b-badge>
          </p>
          <p v-if="currentTask.start">Started at {{ currentTask.start.replace('T', ' ').substring(0, 19) }}</p>
          <p v-if="currentTask.end">Finished at {{ currentTask.end.replace('T', ' ').substring(0, 19) }}</p>
        </div>
      </b-col>
      <b-col v-if="currentTask && currentTask.status !== 'Cancelled' && (currentTask.scheduled_at || currentTask.scheduled_in || currentTask.repeat_in)">
        <label class="text-muted">Configuration</label>
        <hr/>
        <div v-if="showTaskDetails">
          <p v-if="currentTask.status !== 'Requested' && (currentTask.scheduled_at || currentTask.scheduled_in)"><b-badge variant="success">Scheduled</b-badge></p>
          <p v-if="currentTask.status === 'Requested' && currentTask.scheduled_at">Scheduled at {{ currentTask.scheduled_at.replace('T', ' ').substring(0, 19) }}</p>
          <p v-if="currentTask.status === 'Requested' && currentTask.scheduled_in">Scheduled in {{ currentTask.scheduled_in }} {{ currentTask.scheduled_time_unit }}</p>
          <p v-if="currentTask.repeat_in"><b-badge variant="primary">Periodical</b-badge></p>
          <p v-if="currentTask.repeat_in">Every {{ currentTask.repeat_in }} {{ currentTask.repeat_time_unit }}</p>
        </div>
      </b-col>
      <b-col>
        <b-button @click="showTaskDetails = !showTaskDetails" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
          <p class="h5"><b-icon v-if="!showTaskDetails" variant="dark" icon="caret-down-fill"/></p>
          <p class="h5"><b-icon v-if="showTaskDetails" variant="dark" icon="caret-up-fill"/></p>
        </b-button>
        <b-button variant="outline" v-b-modal.cancel-task-modal v-b-tooltip.hover title="Cancel Task" v-if="currentTask && auditor.includes($store.state.role) && currentTask.status !== 'Cancelled' && (cancellable.includes(currentTask.status) || (currentTask.repeat_in && currentTask.repeat_time_unit))">
          <p class="h5"><b-icon variant="danger" icon="dash-circle-fill"/></p>
        </b-button>
        <b-button variant="outline" v-b-modal.repeat-task-modal v-b-tooltip.hover title="Execute Again" v-if="currentTask && auditor.includes($store.state.role) && currentTask.status !== 'Requested' && currentTask.status !== 'Running'">
          <p class="h5"><b-icon variant="success" icon="play-circle-fill"/></p>
        </b-button>
      </b-col>
    </b-row>
    <b-row class="ml-2">
      <b-col>
        <b-table select-mode="single" selectable hover striped borderless head-variant="dark" :fields="executionsFields" :items="executions" @row-selected="selectExecution">
          <template #cell(tool)="row">
            <div v-if="!row.item.step">
              <b-link :href="currentTask.tool.reference" target="_blank">
                <b-img :src="currentTask.tool.icon" width="30" height="30"/>
              </b-link>
              {{ currentTask.tool.name }}
            </div>
            <div v-if="row.item.step">
              <b-link :href="row.item.step.tool.reference" target="_blank">
                <b-img :src="row.item.step.tool.icon" width="30" height="30"/>
              </b-link>
              {{ row.item.step.tool.name }}
            </div>
          </template>
          <template #cell(configuration)="row">
            <p v-if="row.item.step">{{ row.item.step.configuration.name }}</p>
            <p v-if="!row.item.step">{{ currentTask.configuration.name }}</p>
          </template>
          <template #cell(stage)="row">
            <p v-if="row.item.step">{{ row.item.step.tool.stage_name }}</p>
            <p v-if="!row.item.step">{{ currentTask.tool.stage_name }}</p>
          </template>
          <template #cell(status)="row">
            <div v-for="i in statuses" :key="i.value">
              <b-badge v-if="i.value === row.item.status" :variant="i.variant">{{ row.item.status }}</b-badge>
            </div>
          </template>
          <template #cell(date)="row">
            {{ row.item.start !== null ? row.item.start.replace('T', ' ').substring(0, 19) : '' }}
          </template>
        </b-table>
      </b-col>
      <b-col>
        <b-tabs fill active-nav-item-class="font-weight-bold text-danger">
          <b-tab title-link-class="text-secondary" active :disabled="!selectedExecution || !selectedExecution.output_plain">
            <template #title>
              <b-icon icon="gear-fill"/> Output
            </template>
            <b-form-textarea class="mt-3 text-light" style="background-color: #212529;" plaintext v-if="selectedExecution && selectedExecution.output_plain" :value="selectedExecution.output_plain" size="md" rows="5" max-rows="30"></b-form-textarea>
          </b-tab>
          <b-tab title-link-class="text-secondary" v-if="selectedExecution && selectedExecution.output_error">
            <template #title>
              <b-icon icon="exclamation-triangle-fill"/> Error
            </template>
            <b-form-textarea class="mt-3 text-light" style="background-color: #212529;" plaintext :value="selectedExecution.output_error" size="md" rows="5" max-rows="30"></b-form-textarea>
          </b-tab>
          <b-tab title-link-class="text-secondary">
            <template #title>
              <b-icon icon="flag-fill"/> Findings
            </template>
          </b-tab>
        </b-tabs>
      </b-col>
    </b-row>
    <b-modal id="repeat-task-modal" @ok="repeatTask" title="Repeat Task" ok-title="Execute Now" header-bg-variant="success" header-text-variant="light" ok-variant="success">
      <p>This task will be executed right now. Are you sure?</p>
    </b-modal>
    <Deletion id="cancel-task-modal"
      title="Cancel Task"
      removeWord="cancel"
      @deletion="cancelTask"
      v-if="currentTask !== null">
      <span>selected task</span>
    </Deletion>
  </div>
</template>

<script>
import TasksApi from '@/backend/tasks'
import ExecutionsApi from '@/backend/executions'
import { auditor, intensitiesByVariant, statusesByVariant, cancellableStatuses } from '@/backend/constants'
import Deletion from '@/common/Deletion.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'taskDetails',
  mixins: [AlertMixin],
  props: {
    task: {
      type: Object,
      default: null
    }
  },
  data () {
    this.startAutoRefresh()
    return {
      auditor: auditor,
      cancellable: cancellableStatuses,
      intensities: intensitiesByVariant,
      statuses: statusesByVariant,
      currentTask: this.task ? this.task : this.fetchTask(),
      executions: this.fetchExecutions(),
      executionsFields: [
        { key: 'tool', sortable: true },
        { key: 'configuration', sortable: true},
        { key: 'stage', sortable: true },
        { key: 'status', sortable: true },
        { key: 'date', sortable: true }
      ],
      selectedExecution: null,
      showTaskDetails: false,
      autoRefresh: null
    }
  },
  components: {
    Deletion
  },
  methods: {
    startAutoRefresh () {
      if (!this.autoRefresh) {
        this.autoRefresh = setInterval(this.fetchData, 5000)
      }
    },
    stopAutoRefresh () {
      if (this.autoRefresh) {
        clearInterval(this.autoRefresh)
        this.autoRefresh = null
      }
    },
    fetchData () {
      if (this.currentTask) {
        if (this.currentTask.status === 'Running' || this.currentTask.status === 'Requested') {
          this.fetchTask()
          this.fetchExecutions()
        } else {
          this.stopAutoRefresh()
        }
      }
    },
    fetchTask () {
      TasksApi.getTask(this.$route.params.id)
        .then((data) => {
          this.currentTask = data
        })
    },
    fetchExecutions () {
      ExecutionsApi.getAllExecutionsByTask(this.$route.params.id)
        .then(results => {
          this.executions = results
          this.selectExecution(null)
        })
    },
    cancelTask () {
      const notification = this.currentTask.process ? this.currentTask.process.name : this.currentTask.tool.name
      TasksApi.cancelTask(this.currentTask.id)
        .then(() => {
          this.$bvModal.hide('cancel-task-modal')
          this.warning(notification, 'Task cancelled successfully')
          this.fetchTask()
        })
        .catch(() => {
          this.danger(notification, 'Unexpected error in task cancellation')
        })
    },
    repeatTask () {
      const notification = this.currentTask.process ? this.currentTask.process.name : this.currentTask.tool.name
      TasksApi.repeatTask(this.currentTask.id)
        .then((data) => {
          this.$bvModal.hide('repeat-task-modal')
          this.success(notification, 'Task executed again successfully')
          this.$router.push({ name: 'task', params: { id: data.id, task: data } })
        })
        .catch(() => {
          this.danger(notification, 'Unexpected error in task execution')
        })
    },
    selectExecution (items) {
      if (items && items.length > 0) {
        this.selectedExecution = items[0]
      } else {
        this.selectedExecution = this.executions.length === 1 ? this.executions[0] : null
      }
    }
  },
  beforeRouteUpdate(to, from, next) {
    this.currentTask = to.params.task ? to.params.task : this.fetchTask()
    this.fetchExecutions()
    next()
  },
  beforeDestroy () {
    this.stopAutoRefresh()
  }
}
</script>

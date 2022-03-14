<template>
  <div>
    <div class="mt-3" v-if="isFound">
      <b-row>
        <b-col>
          <p>{{ currentTask.target.target }}</p>
          <b-badge variant="secondary">{{ currentTask.target.type }}</b-badge>
        </b-col>
        <b-col>  
          <p v-if="currentTask.process">{{ currentTask.process.name }}</p>
          <p v-if="currentTask.tool">{{ currentTask.tool.name }}</p>
          <p v-if="currentTask.configuration">{{ currentTask.configuration.name }}</p>
          <p v-for="i in intensityByVariant" :key="i.value">
            <b-badge v-if="i.intensity_rank === currentTask.intensity_rank" :variant="i.variant">{{ currentTask.intensity_rank }}</b-badge>
          </p>
        </b-col>
        <b-col>
          <p v-for="i in statusByVariant" :key="i.value">
            <b-badge v-if="i.value === currentTask.status" :variant="i.variant">{{ currentTask.status }}</b-badge>
          </p>
          <p v-if="currentTask.start">Started at {{ currentTask.start.replace('T', ' ').substring(0, 19) }}</p>
          <p v-if="currentTask.end">Finished at {{ currentTask.end.replace('T', ' ').substring(0, 19) }}</p>
        </b-col>
        <b-col v-if="currentTask && currentTask.status !== 'Cancelled' && (currentTask.scheduled_at || currentTask.scheduled_in || currentTask.repeat_in)">      
          <p v-if="currentTask.status !== 'Requested' && (currentTask.scheduled_at || currentTask.scheduled_in)"><b-badge variant="success">Scheduled</b-badge></p>
          <p v-if="currentTask.status === 'Requested' && currentTask.scheduled_at">Scheduled at {{ currentTask.scheduled_at.replace('T', ' ').substring(0, 19) }}</p>
          <p v-if="currentTask.status === 'Requested' && currentTask.scheduled_in">Scheduled in {{ currentTask.scheduled_in }} {{ currentTask.scheduled_time_unit }}</p>
          <p v-if="currentTask.repeat_in"><b-badge variant="primary">Periodical</b-badge></p>
          <p v-if="currentTask.repeat_in">Every {{ currentTask.repeat_in }} {{ currentTask.repeat_time_unit }}</p>
        </b-col>
        <b-col>
          <b-button variant="outline" v-b-modal.cancel-task-modal v-b-tooltip.hover title="Cancel Task" v-if="currentTask && auditor.includes($store.state.role) && currentTask.status !== 'Cancelled' && (cancellableStatuses.includes(currentTask.status) || (currentTask.repeat_in && currentTask.repeat_time_unit))">
            <p class="h5"><b-icon variant="danger" icon="dash-circle-fill"/></p>
          </b-button>
          <b-button variant="outline" v-b-modal.repeat-task-modal v-b-tooltip.hover title="Execute Again" v-if="currentTask && auditor.includes($store.state.role) && currentTask.status !== 'Requested' && currentTask.status !== 'Running'">
            <p class="h5"><b-icon variant="success" icon="play-circle-fill"/></p>
          </b-button>
          <b-dropdown variant="outline" right v-if="auditor.includes($store.state.role)">
            <template #button-content>
              <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
            </template>
            <b-dropdown-item :disabled="!selectedExecution" v-b-modal.defect-dojo-modal @click="ddPath = 'executions'; ddItemId = selectedExecution.id; ddAlreadyReported = selectedExecution.reported_to_defectdojo">Import selected execution</b-dropdown-item>
            <b-dropdown-item :disabled="!currentTask" v-b-modal.defect-dojo-modal @click="ddPath = 'tasks'; ddItemId = currentTask.id; ddAlreadyReported = false">Import task</b-dropdown-item>
          </b-dropdown>
        </b-col>
      </b-row>
      <b-row class="ml-2 mr-2">
        <b-col>
          <b-table select-mode="single" selectable hover striped borderless head-variant="dark" :fields="executionsFields" :items="executions" @row-selected="selectExecution">
            <template #cell(tool)="row">
              <div v-if="!row.item.step">
                <b-link :href="currentTask.tool.reference" target="_blank">
                  <b-img v-if="currentTask.tool.icon" :src="currentTask.tool.icon" width="50" height="30"/>
                  <b-img v-if="!currentTask.tool.icon" src="favicon.ico"/>
                </b-link>
                {{ currentTask.tool.name }}
              </div>
              <div v-if="row.item.step">
                <b-link :href="row.item.step.tool.reference" target="_blank">
                  <b-img v-if="row.item.step.tool.icon" :src="row.item.step.tool.icon" width="50" height="30"/>
                  <b-img v-if="!row.item.step.tool.icon" src="favicon.ico"/>
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
              <div v-for="i in statusByVariant" :key="i.value">
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
            <b-tab title-link-class="text-secondary" :disabled="!selectedExecution || !selectedExecution.output_plain">
              <template #title>
                <b-icon icon="gear-fill"/> Output
              </template>
              <b-form-textarea class="mt-3 text-light" style="background-color: #212529;" plaintext v-if="selectedExecution && selectedExecution.output_plain" :value="selectedExecution.output_plain" size="md" rows="5" max-rows="30"></b-form-textarea>
            </b-tab>
            <b-tab title-link-class="text-secondary" v-if="selectedTask && selectedExecution && selectedExecution.output_error">
              <template #title>
                <b-icon icon="exclamation-triangle-fill"/> Error
              </template>
              <b-form-textarea class="mt-3 text-light" style="background-color: #212529;" plaintext :value="selectedExecution.output_error" size="md" rows="5" max-rows="30"></b-form-textarea>
            </b-tab>
            <b-tab title-link-class="text-secondary" active :disabled="!currentTask || currentTask.status === 'Requested'">
              <template #title>
                <b-icon icon="flag-fill"/> Findings
              </template>
              <findings v-if="currentTask" class="mt-3" :task="currentTask" :execution="selectedExecution" :selection="false" :cols="1"/>
            </b-tab>
          </b-tabs>
        </b-col>
      </b-row>
      <b-modal id="repeat-task-modal" @ok="repeatTask" title="Repeat Task" ok-title="Execute Now" header-bg-variant="success" header-text-variant="light" ok-variant="success">
        <p>This task will be executed right now. Are you sure?</p>
      </b-modal>
      <deletion id="cancel-task-modal" title="Cancel Task" removeWord="cancel" @deletion="cancelTask" v-if="currentTask !== null">
        <span>selected task</span>
      </deletion>
      <defect-dojo id="defect-dojo-modal" :path="ddPath" :itemId="ddItemId" :alreadyReported="ddAlreadyReported" @clean="cleanDDSelection" @confirm="cleanDDSelection"/>
    </div>
    <not-found back="/projects" v-if="!isFound"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Findings from '@/components/findings/Findings'
import DefectDojo from '@/modals/DefectDojo'
import NotFound from '@/errors/NotFound'
export default {
  name: 'taskPage',
  mixins: [RekonoApi],
  props: {
    task: Object
  },
  data () {
    this.startAutoRefresh()
    this.fetchTask()
    this.fetchExecutions()
    return {
      currentTask: this.task ? this.task : {},
      isFound: true,
      executions: [],
      executionsFields: [
        { key: 'tool', sortable: true },
        { key: 'configuration', sortable: true},
        { key: 'stage', sortable: true },
        { key: 'status', sortable: true },
        { key: 'date', sortable: true }
      ],
      selectedExecution: null,
      autoRefresh: null,
      ddPath: null,
      ddItemId: null,
      ddAlreadyReported: null
    }
  },
  components: {
    Findings,
    Deletion,
    DefectDojo,
    NotFound
  },
  methods: {
    startAutoRefresh () {
      if (!this.autoRefresh) {
        this.autoRefresh = setInterval(this.handleRefresh, 5000)
      }
    },
    stopAutoRefresh () {
      if (this.autoRefresh) {
        clearInterval(this.autoRefresh)
        this.autoRefresh = null
      }
    },
    handleRefresh () {
      if (this.currentTask) {
        if (this.currentTask.status === 'Running' || this.currentTask.status === 'Requested') {
          this.fetchTask(true)
          this.fetchExecutions()
        } else {
          this.stopAutoRefresh()
        }
      }
    },
    fetchTask (reload = false) {
      if (!this.task || reload) {
        this.get(`/api/tasks/${this.$route.params.id}/`)
          .then(response => this.currentTask = response.data)
          .catch(error => this.isFound = (error.response.status !== 404))
      }
    },
    fetchExecutions () {
      this.getAllPages('/api/executions/', { task: this.$route.params.id }).then(results => { this.executions = results })
    },
    cancelTask () {
      this.delete(`/api/tasks/${this.currentTask.id}/`, this.currentTask.process ? this.currentTask.process.name : this.currentTask.tool.name, 'Task cancelled successfully')
        .then(() => {
          this.fetchTask(true)
          this.fetchExecutions()
        })
    },
    repeatTask () {
      this.post(`/api/tasks/${this.currentTask.id}/repeat/`, { }, this.currentTask.process ? this.currentTask.process.name : this.currentTask.tool.name, 'Task executed again successfully')
        .then(data => { this.$router.push({ name: 'task', params: { id: data.id, task: data } }) })
    },
    selectExecution (items) {
      if (items && items.length > 0) {
        this.selectedExecution = items[0]
      }
    },
    cleanDDSelection () {
      this.$bvModal.hide('defect-dojo-modal')
      this.ddPath = null
      this.ddItemId = null
      this.ddAlreadyReported = null
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

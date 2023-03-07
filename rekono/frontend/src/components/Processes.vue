<template>
  <div>
    <table-header :filters="filters" add="process-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="processesFields" :items="data">
      <template #cell(tags)="row">
        <b-form-tags no-outer-focus :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id" :value="row.item.tags" placeholder="" remove-on-delete size="md" tag-variant="dark" @input="updateProcess(row.item, $event)"/>
      </template>
      <template #cell(likes)="row">
        {{ row.item.likes }}
        <b-button variant="outline">
          <b-icon variant="danger" v-if="row.item.liked" icon="heart-fill" @click="dislikeProcess(row.item.id)"/>
          <b-icon variant="danger" v-if="!row.item.liked" icon="heart" @click="likeProcess(row.item.id)"/>
        </b-button>
      </template>
      <template #cell(actions)="row">
        <b-button @click="showProcess(row)" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" variant="dark" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" variant="secondary" icon="eye-slash-fill"/>
        </b-button>
        <b-button variant="outline" class="mr-2" :disabled="row.item.steps.length === 0" v-b-tooltip.hover title="Execute" @click="taskModal(row.item)" v-b-modal.task-modal>
          <b-icon variant="success" icon="play-circle-fill"/>
        </b-button>
        <b-dropdown variant="outline" right>
          <template #button-content>
            <b-icon variant="dark" icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item @click="stepModal(row.item)" v-b-modal.step-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
            <b-icon variant="success" icon="plus-square"/>
            <label class="ml-1" variant="dark">Add Step</label>
          </b-dropdown-item>
          <b-dropdown-item variant="dark" @click="processModal(row.item)" v-b-modal.process-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
            <b-icon icon="pencil-square"/>
            <label class="ml-1">Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" @click="selectedProcess = row.item" v-b-modal.delete-process-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </template>
      <template #row-details="row">
        <b-card>
          <p>{{ row.item.description }}</p>
          <b-table striped borderless small head-variant="light" :fields="stepsFields" :items="row.item.steps">
            <template #cell(icon)="step">
              <b-link :href="step.item.tool.reference" target="_blank">
                <b-img v-if="step.item.tool.icon" :src="step.item.tool.icon" width="32"/>
                <b-img v-if="!step.item.tool.icon" src="favicon.ico" width="32"/>
              </b-link>
            </template>
            <template #cell(actions)="step">
              <b-dropdown variant="outline" right>
                <template #button-content>
                  <b-icon variant="secondary" icon="three-dots-vertical"/>
                </template>
                <b-dropdown-item variant="dark" @click="stepModal(row.item, step.item)" v-b-modal.step-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
                  <b-icon icon="pencil-square"/>
                  <label class="ml-1">Edit</label>
                </b-dropdown-item>
                <b-dropdown-item variant="danger" @click="selectStep(row.item, step.item)" v-b-modal.delete-step-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
                  <b-icon icon="trash-fill"/>
                  <label class="ml-1">Delete</label>
                </b-dropdown-item>
              </b-dropdown>
            </template>
          </b-table>
        </b-card>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="processes" @pagination="pagination"/>
    <deletion id="delete-process-modal" title="Delete Process" @deletion="deleteProcess" @clean="cleanSelection" v-if="selectedProcess !== null">
      <span><strong>{{ selectedProcess.name }}</strong> process</span>
    </deletion>
    <deletion id="delete-step-modal" title="Delete Step" @deletion="deleteStep" @clean="cleanSelection" v-if="selectedProcess !== null && selectedStep !== null">
      <span><strong>{{ this.selectedStep.tool.name }}</strong> step from <strong>{{ selectedProcess.name }}</strong> process</span>
    </deletion>
    <process id="process-modal" :process="selectedProcess" :initialized="showProcessModal" @confirm="confirm" @clean="cleanSelection"/>
    <step id="step-modal" :process="selectedProcess" :step="selectedStep" :initialized="showStepModal" @confirm="confirm" @clean="cleanSelection"/>
    <task id="task-modal" :process="selectedProcess" :initialized="showTaskModal" @clean="cleanSelection"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
import TableHeader from '@/common/TableHeader'
import Process from '@/modals/Process'
import Step from '@/modals/Step'
import Task from '@/modals/Task'
export default {
  name: 'processesPage',
  mixins: [RekonoApi],
  data () {
    this.fetchData()
    return {
      data: [],
      processesFields: [
        { key: 'name', label: 'Process', sortable: true },
        { key: 'tags', sortable: true },
        { key: 'steps.length', label: 'Steps', sortable: true },
        { key: 'creator.username', label: 'Creator', sortable: true },
        { key: 'likes', sortable: true },
        { key: 'actions', sortable: false }
      ],
      stepsFields: [
        { key: 'icon', label: '', sortable: false },
        { key: 'tool.name', label: 'Tool', sortable: true },
        { key: 'configuration.name', label: 'Configuration', sortable: true },
        { key: 'configuration.stage_name', label: 'Stage', sortable: true },
        { key: 'priority', sortable: true },
        { key: 'actions', sortable: false }
      ],
      showTaskModal: false,
      showProcessModal: false,
      showStepModal: false,
      selectedProcess: null,
      selectedStep: null,
      filters: [],
      showProcessId: null
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    Process,
    Step,
    Task
  },
  watch: {
    data () {
      this.filters = [
        { name: 'Tags', filterField: 'tags__name__in', type: 'tags' },
        { name: 'Stage', values: this.stages, valueField: 'id', textField: 'value', filterField: 'steps__configuration__stage' },
        { name: 'Creator', filterField: 'creator__username__icontains', type: 'text' },
        { name: 'Favourities', type: 'checkbox', filterField: 'liked' }
      ]
    }
  },
  methods: {
    fetchData (params = {}) {
      params.o = 'name'
      return this.getOnePage('/api/processes/', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
          if (this.showProcessId) {
            this.data.filter(process => process.id === this.showProcessId).forEach(process => process._showDetails = true)
          }
        })
    },
    showProcess (row) {
      row.toggleDetails()
      this.showProcessId = row.item._showDetails ? row.item.id : null
    },
    likeProcess (processId) {
      this.post(`/api/processes/${processId}/like/`, { }).then(() => this.fetchData())
    },
    dislikeProcess (processId) {
      this.post(`/api/processes/${processId}/dislike/`, { }).then(() => this.fetchData())
    },
    updateProcess (process, tags) {
      this.put(`/api/processes/${process.id}/`, { name: process.name, description: process.description, tags: tags })
    },
    deleteProcess () {
      this.delete(`/api/processes/${this.selectedProcess.id}/`, this.selectedProcess.name, 'Process deleted successfully').then(() => this.fetchData())
    },
    deleteStep () {
      this.delete(`/api/steps/${this.selectedStep.id}/`, `${this.selectedProcess.name} - ${this.selectedStep.tool.name}`, 'Step deleted successfully').then(() => this.fetchData())
    },
    taskModal (process) {
      this.cleanSelection()
      this.showTaskModal = true
      this.selectedProcess = process
    },
    processModal (process) {
      this.cleanSelection()
      this.showProcessModal = true
      this.selectedProcess = process
    },
    stepModal (process, step = null) {
      this.cleanSelection()
      this.showStepModal = true
      if (step !== null) {
        this.selectStep(process, step)
      } else {
        this.selectedProcess = process
      }
    },
    selectStep (process, step) {
      this.selectedProcess = process
      this.selectedStep = step
    },
    cleanSelection () {
      this.taskForm = false
      this.processForm = false
      this.stepForm = false
      this.selectedProcess = null
      this.selectedStep = null
      this.showTaskModal = false
      this.showProcessModal = false
      this.showStepModal = false
    }
  }
}
</script>

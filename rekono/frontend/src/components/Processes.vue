<template>
  <div>
    <div class="text-right">
      <b-button size="lg" variant="outline" v-b-modal.process-modal>
        <p class="h2 mb-2"><b-icon variant="success" icon="plus-square-fill"/></p>
      </b-button>
    </div>
    <b-table striped borderless head-variant="dark" :fields="processesFields" :items="processes">
      <template #cell(actions)="row">
          <b-button @click="row.toggleDetails" variant="dark" class="mr-2" v-b-tooltip.hover title="Details">
            <b-icon v-if="!row.detailsShowing" icon="eye-fill"/>
            <b-icon v-if="row.detailsShowing" icon="eye-slash-fill"/>
          </b-button>
          <b-button variant="success" class="mr-2" v-b-tooltip.hover title="Execute" @click="showExecuteForm(row.item)" v-b-modal.execute-modal>
            <b-icon icon="play-fill"/>
          </b-button>
          <b-dropdown variant="outline-primary" right>
            <template #button-content>
              <b-icon icon="three-dots-vertical"/>
            </template>
            <b-dropdown-item @click="showStepForm(row.item)" v-b-modal.step-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
              <div style="display: inline">
                <b-icon variant="success" icon="plus-square"/>
                <label variant="dark">Add Step</label>
              </div>
            </b-dropdown-item>
            <b-dropdown-item variant="dark" @click="showProcessForm(row.item)" v-b-modal.process-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
              <b-icon icon="pencil-square"/>
              <label>Edit</label>
            </b-dropdown-item>
            <b-dropdown-item variant="danger" @click="selectProcess(row.item)" v-b-modal.delete-process-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
              <b-icon icon="trash-fill"/>
              <label>Delete</label>
            </b-dropdown-item>
          </b-dropdown>
        </template>
        <template #row-details="row">
          <b-card>
            <p>{{ row.item.description }}</p>
            <b-table striped borderless small head-variant="light" :fields="stepsFields" :items="row.item.steps">
              <template #cell(icon)="step">
                <b-link :href="step.item.tool.reference" target="_blank">
                  <b-img :src="step.item.tool.icon" width="100" height="50"/>
                </b-link>
              </template>
              <template #cell(actions)="step">
                <b-dropdown variant="outline-secondary" right>
                  <template #button-content>
                    <b-icon icon="three-dots-vertical"/>
                  </template>
                  <b-dropdown-item variant="dark" @click="showStepForm(row.item, step.item)" v-b-modal.step-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
                    <b-icon icon="pencil-square"/>
                    <label>Edit</label>
                  </b-dropdown-item>
                  <b-dropdown-item variant="danger" @click="selectStep(row.item, step.item)" v-b-modal.delete-step-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
                    <b-icon icon="trash-fill"/>
                    <label>Delete</label>
                  </b-dropdown-item>
                </b-dropdown>
              </template>
            </b-table>
          </b-card>
        </template>
    </b-table>
    <Pagination :page="page" :size="size" :sizes="sizes" :total="total" name="processes" @pagination="pagination"/>
    <DeleteConfirmation id="delete-process-modal"
      title="Delete Process"
      @deletion="deleteProcess"
      @clean="cleanSelection"
      v-if="selectedProcess !== null">
      <span slot="body"><strong>{{ selectedProcess.name }}</strong> process</span>
    </DeleteConfirmation>
    <DeleteConfirmation id="delete-step-modal"
      title="Delete Step"
      @deletion="deleteStep"
      @clean="cleanSelection"
      v-if="selectedProcess !== null && selectedStep !== null">
      <span slot="body"><strong>{{ this.selectedStep.tool.name }}</strong> step from <strong>{{ selectedProcess.name }}</strong> process</span>
    </DeleteConfirmation>
    <ProcessForm id="process-modal" :process="selectedProcess" :initialized="processForm" @confirm="confirm" @clean="cleanSelection"/>
    <StepForm id="step-modal" :process="selectedProcess" :step="selectedStep" :initialized="stepForm" @confirm="confirm" @clean="cleanSelection"/>
    <TaskForm id="execute-modal" :process="selectedProcess" :initialized="taskForm" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import Processes from '../backend/processes'
import DeleteConfirmation from './common/DeleteConfirmation.vue'
import ProcessForm from './forms/ProcessForm.vue'
import StepForm from './forms/StepForm.vue'
import TaskForm from './forms/TaskForm.vue'
import Pagination from './common/Pagination.vue'
import PaginationMixin from './common/PaginationMixin.vue'
const ProcessApi = Processes.ProcessApi
const StepApi = Processes.StepApi
export default {
  name: 'processesPage',
  mixins: [PaginationMixin],
  data () {
    return {
      processes: this.fetchData(1, 25),
      processesFields: [
        {key: 'name', label: 'Process', sortable: true},
        {key: 'steps.length', label: 'Steps', sortable: true},
        {key: 'creator.username', label: 'Creator', sortable: true},
        {key: 'actions', sortable: false}
      ],
      stepsFields: [
        {key: 'icon', sortable: false},
        {key: 'tool.name', label: 'Tool', sortable: true},
        {key: 'configuration.name', label: 'Configuration', sortable: true},
        {key: 'tool.stage_name', label: 'Stage', sortable: true},
        {key: 'priority', sortable: true},
        {key: 'actions', sortable: false}
      ],
      taskForm: false,
      processForm: false,
      stepForm: false,
      selectedProcess: null,
      selectedStep: null
    }
  },
  components: {
    DeleteConfirmation,
    ProcessForm,
    StepForm,
    TaskForm,
    Pagination
  },
  methods: {
    fetchData (page = null, size = null) {
      ProcessApi.getAllProcesses(page, size).then(processes => { this.processes = processes })
    },
    deleteProcess () {
      ProcessApi.deleteProcess(this.selectedProcess.id)
        .then(() => {
          this.$bvModal.hide('delete-process-modal')
          this.$bvToast.toast('Process deleted successfully', {
            title: this.selectedProcess.name,
            variant: 'warning',
            solid: true
          })
          this.fetchData(this.page, this.size)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in process deletion', {
            title: this.selectedProcess.name,
            variant: 'danger',
            solid: true
          })
        })
    },
    deleteStep () {
      StepApi.deleteStep(this.selectedStep.id)
        .then(() => {
          this.$bvModal.hide('delete-step-modal')
          this.$bvToast.toast('Step deleted successfully', {
            title: this.processName + ' - ' + this.selectedStep.name,
            variant: 'warning',
            solid: true
          })
          this.fetchData(this.page, this.size)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in step deletion', {
            title: this.processName,
            variant: 'danger',
            solid: true
          })
        })
    },
    showExecuteForm (process, step = null) {
      this.taskForm = true
      if (step !== null) {
        this.selectStep(process, step)
      } else {
        this.selectProcess(process)
      }
    },
    showProcessForm (process, step = null) {
      this.processForm = true
      if (step !== null) {
        this.selectStep(process, step)
      } else {
        this.selectProcess(process)
      }
    },
    showStepForm (process, step = null) {
      this.stepForm = true
      if (step !== null) {
        this.selectStep(process, step)
      } else {
        this.selectProcess(process)
      }
    },
    selectProcess (process) {
      this.selectedProcess = process
    },
    selectStep (process, step) {
      this.selectProcess(process)
      this.selectedStep = step
    },
    cleanSelection () {
      this.taskForm = false
      this.processForm = false
      this.stepForm = false
      this.selectedProcess = null
      this.selectedStep = null
    }
  }
}
</script>

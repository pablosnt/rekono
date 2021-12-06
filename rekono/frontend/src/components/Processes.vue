<template>
  <div>
    <div class="text-right">
      <b-button size="lg" variant="outline" v-b-modal.process-modal>
        <p class="h2 mb-2"><b-icon variant="success" icon="plus-square-fill"/></p>
      </b-button>
    </div>
    <b-table striped borderless head-variant="dark" :fields="processesFields" :items="processesItems">
      <template #cell(actions)="row">
          <b-button @click="row.toggleDetails" variant="dark" class="mr-2" v-b-tooltip.hover title="Details">
            <b-icon v-if="!row.detailsShowing" icon="eye-fill"/>
            <b-icon v-if="row.detailsShowing" icon="eye-slash-fill"/>
          </b-button>
          <b-button variant="success" class="mr-2" v-b-tooltip.hover title="Execute">
            <b-icon icon="play-fill"/>
          </b-button>
          <b-button variant="outline-primary" class="mr-2" @click="selectProcess(row.item)" v-b-modal.step-modal v-b-tooltip.hover title="Add Step" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
            <b-icon icon="plus-square"/>
          </b-button>
          <b-button variant="secondary" class="mr-2" @click="selectProcess(row.item, true)" v-b-modal.process-modal v-b-tooltip.hover title="Edit" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
            <b-icon icon="pencil-square"/>
          </b-button>
          <b-button variant="danger" class="mr-2" @click="selectProcess(row.item)" v-b-modal.delete-process-modal v-b-tooltip.hover title="Delete" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
            <b-icon icon="trash-fill"/>
          </b-button>
        </template>
        <template #row-details="row">
          <b-card>
            <p>{{ row.item.details.description }}</p>
            <b-table striped borderless small head-variant="light" :fields="stepsFields" :items="row.item.details.steps">
              <template #cell(icon)="step">
                <b-link :href="step.item.reference" target="_blank">
                  <b-img :src="step.item.icon" width="100" height="50"/>
                </b-link>
              </template>
              <template #cell(actions)="step">
                <b-button variant="secondary" class="mr-2" @click="selectStep(row.item, step.item, true)" v-b-modal.step-modal v-b-tooltip.hover title="Edit" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
                  <b-icon icon="pencil-square"/>
                </b-button>
                <b-button variant="danger" class="mr-2" @click="selectStep(row.item, step.item)" v-b-modal.delete-step-modal v-b-tooltip.hover title="Delete" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
                  <b-icon icon="trash-fill"/>
                </b-button>
              </template>
            </b-table>
          </b-card>
        </template>
    </b-table>
    <b-modal id="delete-process-modal" @hidden="resetModal" @ok="deleteProcess" title="Delete Process" ok-title="Delete Process" header-bg-variant="danger" header-text-variant="light" ok-variant="danger">
      <p v-if="selectedProcess != null">You will remove the <strong>{{ selectedProcess.process }}</strong> process. Are you sure?</p>
    </b-modal>
    <b-modal id="process-modal" @hidden="resetModal" @ok="handleProcess" :title="processModalTitle()" :ok-title="processModalOkTitle()">
      <b-form ref="process_form" @submit.stop.prevent="createOrUpdateProcess">
        <b-form-group description="Process name" invalid-feedback="Process name is required">
          <b-form-input v-model="processName" type="text" :state="newProcessNameState" maxlength="30" required/>
        </b-form-group>
        <b-form-group invalid-feedback="Process description is required">
          <b-form-textarea v-model="processDescription" placeholder="Process description" :state="newProcessDescState" maxlength="350" required/>
        </b-form-group>
      </b-form>
    </b-modal>
    <b-modal id="delete-step-modal" @hidden="resetModal" @ok="deleteStep" title="Delete Step" ok-title="Delete Step" header-bg-variant="danger" header-text-variant="light" ok-variant="danger">
      <p v-if="selectedStep != null">You will remove the <strong>{{ this.selectedTool.name }}</strong> step from <strong>{{ selectedProcess.process }}</strong> process. Are you sure?</p>
    </b-modal>
    <b-modal id="step-modal" @hidden="resetModal" @ok="handleStep" :title="stepModalTitle()" :ok-title="stepModalOkTitle()">
      <b-form ref="step_form" @submit.stop.prevent="createOrUpdateStep">
        <b-form-group description="Tool">
          <b-input-group>
            <b-input-group-prepend is-text v-if="selectedTool != null">
              <b-link :href="selectedTool.reference" target="_blank">
                <b-img :src="selectedTool.icon" width="40" height="20"/>
              </b-link>
            </b-input-group-prepend>
            <b-form-select v-model="selectedToolId" :options="toolsItems" :disabled="edit" @change="selectTool" value-field="id" text-field="name" :state="newStepToolState" required>
              <template #first>
                <b-form-select-option :value="null" disabled>Select tool</b-form-select-option>
              </template>
            </b-form-select>
          </b-input-group>
        </b-form-group>
        <b-form-group description="Tool configuration" invalid-feedback="This step already exists in the process">
          <b-form-select v-model="selectedConfiguration" :options="selectedConfigurations" :disabled="selectedConfiguration == null || edit" value-field="id" text-field="configuration" :state="newStepConfigState" required/>
        </b-form-group>
        <b-form-group>
          <b-input-group :prepend="stepPriority.toString()">
            <b-form-input v-model="stepPriority" type="range" min="1" max="50" required/>
            <b-input-group-append is-text v-b-tooltip.hover title="The priority allows to run steps with greater value before other tools of the same stage. By default the priority is 1, so all the steps will be treated in the same way">
              <b-icon icon="info-circle-fill" variant="info"/>
            </b-input-group-append>
          </b-input-group>
          <small class="text-muted">Step priority</small>
        </b-form-group>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import { getTools } from '../backend/tools'
import { getAllProcesses, createProcess, updateProcess, deleteProcess, createStep, updateStep, deleteStep } from '../backend/processes'
export default {
  name: 'processesPage',
  data () {
    return {
      processesItems: this.processes(),
      processesFields: [
        {key: 'process', sortable: true},
        {key: 'steps', sortable: true},
        {key: 'creator', sortable: true},
        {key: 'actions', sortable: false}
      ],
      stepsFields: [
        {key: 'icon', sortable: false},
        {key: 'tool', sortable: true},
        {key: 'configuration', sortable: true},
        {key: 'stage', sortable: true},
        {key: 'priority', sortable: true},
        {key: 'actions', sortable: false}
      ],
      toolsItems: this.tools(),
      processName: null,
      processDescription: null,
      newProcessNameState: null,
      newProcessDescState: null,
      selectedProcess: null,
      selectedTool: null,
      selectedToolId: null,
      selectedConfigurations: [],
      selectedConfiguration: null,
      stepPriority: 1,
      newStepToolState: null,
      newStepConfigState: null,
      edit: false
    }
  },
  methods: {
    processes () {
      var processes = []
      getAllProcesses()
        .then(results => {
          for (var i = 0; i < results.length; i++) {
            var steps = []
            for (var s = 0; s < results[i].steps.length; s++) {
              var step = {
                id: results[i].steps[s].id,
                icon: results[i].steps[s].tool.icon,
                reference: results[i].steps[s].tool.reference,
                tool: results[i].steps[s].tool.name,
                toolId: results[i].steps[s].tool.id,
                configuration: results[i].steps[s].configuration.name,
                configurationId: results[i].steps[s].configuration.id,
                stage: results[i].steps[s].tool.stage_name,
                priority: results[i].steps[s].priority
              }
              steps.push(step)
            }
            var item = {
              id: results[i].id,
              process: results[i].name,
              creator: results[i].creator.username,
              creatorId: results[i].creator.id,
              steps: results[i].steps.length,
              details: {
                description: results[i].description,
                steps: steps
              }
            }
            processes.push(item)
          }
        })
      return processes
    },
    tools () {
      var tools = []
      getTools()
        .then(results => {
          for (var i = 0; i < results.length; i++) {
            var configurations = []
            for (var c = 0; c < results[i].configurations.length; c++) {
              var config = {
                id: results[i].configurations[c].id,
                configuration: results[i].configurations[c].name,
                default: results[i].configurations[c].default
              }
              configurations.push(config)
            }
            var item = {
              id: results[i].id,
              name: results[i].name,
              stage: results[i].stage_name,
              icon: results[i].icon,
              reference: results[i].reference,
              configurations: configurations
            }
            tools.push(item)
          }
        })
      return tools
    },
    processModalTitle () {
      if (this.edit) {
        return 'Edit Process'
      } else {
        return 'New Process'
      }
    },
    processModalOkTitle () {
      if (this.edit) {
        return 'Update Process'
      } else {
        return 'Create Process'
      }
    },
    handleProcess (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.createOrUpdateProcess()
    },
    createOrUpdateProcess () {
      if (!this.checkProcessState()) {
        return
      }
      if (this.edit) {
        updateProcess(this.selectedProcess.id, this.processName, this.processDescription)
          .then(() => {
            this.$bvModal.hide('process-modal')
            this.$bvToast.toast('Process updated successfully', {
              title: this.processName,
              variant: 'success',
              solid: true
            })
            this.processesItems = this.processes()
          })
          .catch(() => {
            this.$bvToast.toast('Unexpected error in process update', {
              title: this.processName,
              variant: 'danger',
              solid: true
            })
          })
      } else {
        createProcess(this.processName, this.processDescription)
          .then(() => {
            this.$bvModal.hide('process-modal')
            this.$bvToast.toast('New process created successfully', {
              title: this.processName,
              variant: 'success',
              solid: true
            })
            this.processesItems = this.processes()
          })
          .catch(() => {
            this.$bvToast.toast('Unexpected error in process creation', {
              title: this.processName,
              variant: 'danger',
              solid: true
            })
          })
      }
    },
    checkProcessState () {
      const valid = this.$refs.process_form.checkValidity()
      this.newProcessNameState = (this.processDescription !== null && this.processDescription.length > 0)
      this.newProcessDescState = (this.processName !== null && this.processName.length > 0)
      return valid
    },
    deleteProcess () {
      deleteProcess(this.selectedProcess.id)
        .then(() => {
          this.$bvModal.hide('delete-process-modal')
          this.$bvToast.toast('Process deleted successfully', {
            title: this.processName,
            variant: 'success',
            solid: true
          })
          this.processesItems = this.processes()
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in process deletion', {
            title: this.processName,
            variant: 'danger',
            solid: true
          })
        })
    },
    stepModalTitle () {
      if (this.selectedProcess && this.edit) {
        return 'Edit step from ' + this.selectedProcess.process
      } else if (this.selectedProcess) {
        return 'New step for ' + this.selectedProcess.process
      }
      return 'New Step'
    },
    stepModalOkTitle () {
      if (this.edit) {
        return 'Update Step'
      } else {
        return 'Create Step'
      }
    },
    handleStep (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.createOrUpdateStep()
    },
    createOrUpdateStep () {
      if (!this.checkStepState()) {
        return
      }
      if (this.edit) {
        updateStep(this.selectedStep.id, this.stepPriority)
          .then(() => {
            this.$bvModal.hide('step-modal')
            this.$bvToast.toast('Step updated successfully', {
              title: this.selectedTool.name,
              variant: 'success',
              solid: true
            })
            this.processesItems = this.processes()
          })
          .catch(() => {
            this.$bvToast.toast('Unexpected error in step update', {
              title: this.selectedTool.name,
              variant: 'danger',
              solid: true
            })
          })
      } else {
        createStep(this.selectedProcess.id, this.selectedToolId, this.selectedConfiguration, this.stepPriority)
          .then(() => {
            this.$bvModal.hide('step-modal')
            this.$bvToast.toast('New step created successfully', {
              title: this.selectedTool.name,
              variant: 'success',
              solid: true
            })
            this.processesItems = this.processes()
          })
          .catch(() => {
            this.$bvToast.toast('Unexpected error in step creation', {
              title: this.selectedTool.name,
              variant: 'danger',
              solid: true
            })
          })
      }
    },
    checkStepState () {
      const valid = this.$refs.step_form.checkValidity()
      if (!this.edit) {
        this.newStepToolState = valid
        for (var s = 0; s < this.selectedProcess.details.steps.length; s++) {
          if (this.selectedProcess.details.steps[s].toolId === this.selectedToolId && this.selectedProcess.details.steps[s].configurationId === this.selectedConfiguration) {
            this.newStepConfigState = false
            return false
          }
        }
      }
      return valid
    },
    deleteStep () {
      deleteStep(this.selectedStep.id)
        .then(() => {
          this.$bvModal.hide('delete-step-modal')
          this.$bvToast.toast('Step deleted successfully', {
            title: this.processName + ' - ' + this.selectedTool.name,
            variant: 'success',
            solid: true
          })
          this.processesItems = this.processes()
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in step deletion', {
            title: this.processName,
            variant: 'danger',
            solid: true
          })
        })
    },
    selectProcess (process, edit = false) {
      this.selectedProcess = process
      this.processName = process.process
      this.processDescription = process.details.description
      this.newProcessNameState = null
      this.newProcessDescState = null
      this.edit = edit
    },
    selectStep (process, step, edit = false) {
      this.selectProcess(process, edit)
      this.selectedStep = step
      this.stepPriority = step.priority
      for (var t = 0; t < this.toolsItems.length; t++) {
        if (this.toolsItems[t].id === step.toolId) {
          this.selectedTool = this.toolsItems[t]
          break
        }
      }
      this.selectedToolId = step.toolId
      this.selectedConfigurations = this.selectedTool.configurations
      this.selectedConfiguration = step.configurationId
      this.edit = edit
    },
    selectTool (toolId) {
      this.selectedToolId = toolId
      for (var t = 0; t < this.toolsItems.length; t++) {
        if (this.toolsItems[t].id === toolId) {
          this.selectedTool = this.toolsItems[t]
          break
        }
      }
      this.selectedConfigurations = this.selectedTool.configurations
      this.selectedConfiguration = this.selectedConfigurations[0].id
    },
    resetModal () {
      this.processName = null
      this.processDescription = null
      this.newProcessNameState = null
      this.newProcessDescState = null
      this.selectedTool = null
      this.selectedToolId = null
      this.selectedConfigurations = []
      this.selectedConfiguration = null
      this.stepPriority = 1
      this.newStepToolState = null
      this.newStepConfigState = null
      this.edit = false
    }
  }
}
</script>

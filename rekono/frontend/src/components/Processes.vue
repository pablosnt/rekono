<template>
  <div>
    <div class="text-right">
      <b-button size="lg" variant="outline" v-b-modal.new-process-modal>
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
          <b-button variant="outline-primary" class="mr-2" @click="selectProcess(row.item)" v-b-modal.new-step-modal v-b-tooltip.hover title="Add Step" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
            <b-icon icon="plus-square"/>
          </b-button>
          <b-button variant="secondary" class="mr-2" @click="selectProcess(row.item)" v-b-tooltip.hover title="Edit" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
            <b-icon icon="pencil-square"/>
          </b-button>
          <b-button variant="danger" class="mr-2" @click="selectProcess(row.item)" v-b-tooltip.hover title="Remove" v-if="$store.state.role == 'Admin' || $store.state.user == row.item.creatorId">
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
            </b-table>
          </b-card>
        </template>
    </b-table>
    <b-modal id="new-process-modal" @hidden="resetModal" @ok="handleNewProcess" title="New Process" ok-title="Create Process">
      <b-form ref="new_process_form" @submit.stop.prevent="createNewProcess">
        <b-form-group description="Process name" invalid-feedback="Process name is required">
          <b-form-input v-model="processName" type="text" :state="newProcessNameState" maxlength="30" required/>
        </b-form-group>
        <b-form-group invalid-feedback="Process description is required">
          <b-form-textarea v-model="processDescription" placeholder="Process description" :state="newProcessDescState" maxlength="350" required/>
        </b-form-group>
      </b-form>
    </b-modal>
    <b-modal id="new-step-modal" @hidden="resetModal" @ok="handleNewStep" ok-title="Create Step">
      <template #modal-title>
        New step for {{ selectedProcess.process }}
      </template>
      <b-form ref="new_step_form" @submit.stop.prevent="createNewStep">
        <b-form-group description="Tool" invalid-feedback="Tool is required">
          <b-input-group>
            <b-input-group-prepend is-text v-if="selectedTool != null">
              <b-link :href="selectedTool.reference" target="_blank">
                <b-img :src="selectedTool.icon" width="40" height="20"/>
              </b-link>
            </b-input-group-prepend>
            <b-form-select v-model="selectedToolId" :options="toolsItems" @change="selectTool" value-field="id" text-field="name" required>
              <template #first>
                <b-form-select-option :value="null" disabled>Select tool</b-form-select-option>
              </template>
            </b-form-select>
          </b-input-group>
        </b-form-group>
        <b-form-group description="Tool configuration" invalid-feedback="Tool configuration is required">
          <b-form-select v-model="selectedConfiguration" :options="selectedConfigurations" :disabled="selectedConfiguration == null" value-field="id" text-field="configuration" required/>
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
import { getAllProcesses, createNewProcess, createNewStep } from '../backend/processes'
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
        {key: 'priority', sortable: true}
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
                icon: results[i].steps[s].tool.icon,
                reference: results[i].steps[s].tool.reference,
                tool: results[i].steps[s].tool.name,
                configuration: results[i].steps[s].configuration.name,
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
    handleNewProcess (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.createNewProcess()
    },
    createNewProcess () {
      if (!this.checkNewProcessState()) {
        return
      }
      createNewProcess(this.processName, this.processDescription)
        .then(data => {
          this.$bvModal.hide('new-process-modal')
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
    },
    checkNewProcessState () {
      const valid = this.$refs.new_process_form.checkValidity()
      this.newProcessNameState = (this.processDescription != null)
      this.newProcessDescState = (this.processName != null)
      return valid
    },
    handleNewStep (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.createNewStep()
    },
    createNewStep () {
      if (!this.checkNewStepState()) {
        return
      }
      createNewStep(this.selectedProcess.id, this.selectedToolId, this.selectedConfiguration, this.stepPriority)
        .then(() => {
          this.$bvModal.hide('new-step-modal')
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
    },
    checkNewStepState () {
      const valid = this.$refs.new_step_form.checkValidity()
      this.newStepState = valid
      return valid
    },
    selectProcess (process) {
      this.selectedProcess = process
      this.processName = process.name
      this.processDescription = process.description
      this.newProcessNameState = null
      this.newProcessDescState = null
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
    }
  }
}
</script>

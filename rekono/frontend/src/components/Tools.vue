<template>
  <div>
    <b-table striped borderless head-variant="dark" :fields="toolsFields" :items="toolsItems">
      <template #cell(icon)="row">
        <b-link :href="row.item.reference" target="_blank">
          <b-img :src="row.item.icon" width="100" height="50"/>
        </b-link>
      </template>
      <template #cell(intensities)="row">
        <div v-for="item in row.item.intensities" v-bind:key="item.value" style="display: inline">
          <b-badge :variant="item.variant" v-b-tooltip.hover :title="item.value">{{ item.summary }}</b-badge>
          <span/>
        </div>
      </template>
      <template #cell(actions)="row">
        <b-button @click="row.toggleDetails" variant="dark" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" icon="eye-slash-fill"/>
        </b-button>
        <b-button variant="success" class="mr-2" v-b-tooltip.hover title="Execute">
          <b-icon icon="play-fill"/>
        </b-button>
        <b-dropdown variant="outline-primary" right v-b-tooltip.hover title="Add to Process">
          <template #button-content>
            <b-icon icon="plus-square"/>
          </template>
          <b-dropdown-item @click="selectTool(row.item)" v-b-modal.new-process-modal >New Process</b-dropdown-item>
          <b-dropdown-item @click="selectTool(row.item)" v-b-modal.new-step-modal :disabled="processesItems.length == 0">New Step</b-dropdown-item>
        </b-dropdown>
      </template>
      <template #row-details="row">
        <b-card>
          <b-table striped borderless small head-variant="light" :fields="configFields" :items="row.item.configurations">
            <template #cell(default)="config">
              <b-icon v-if="config.item.default" icon="check-circle-fill" variant="success"/>
            </template>
          </b-table>
        </b-card>
      </template>
    </b-table>
    <b-modal id="new-process-modal" @hidden="resetModal" @ok="handleNewProcess" ok-title="Create Process">
      <template #modal-title>
        New Process with {{ selectedTool.name }}
      </template>
      <b-form ref="new_process_form" @submit.stop.prevent="createNewProcess">
        <b-form-group description="Process name" invalid-feedback="Process name is required">
          <b-form-input v-model="processName" type="text" :state="newProcessNameState" maxlength="30" required/>
        </b-form-group>
        <b-form-group invalid-feedback="Process description is required">
          <b-form-textarea v-model="processDescription" placeholder="Process description" :state="newProcessDescState" maxlength="350" required/>
        </b-form-group>
        <b-form-group description="Tool configuration">
          <b-form-select v-model="selectedConfiguration" :options="selectedConfigurations" value-field="id" text-field="configuration" required/>
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
    <b-modal id="new-step-modal" @hidden="resetModal" @ok="handleNewStep" ok-title="Create Step">
      <template #modal-title>
        New Step: {{ selectedTool.name }}
      </template>
      <b-form ref="new_step_form" @submit.stop.prevent="createNewStep">
        <b-form-group description="Process" invalid-feedback="Process is required">
          <b-form-select v-model="selectedProcess" :options="processesItems" value-field="id" text-field="name" :state="newStepState" required>
            <template #first>
              <b-form-select-option :value="null" disabled>Select your process</b-form-select-option>
            </template>
          </b-form-select>
        </b-form-group>
        <b-form-group description="Tool configuration">
          <b-form-select v-model="selectedConfiguration" :options="selectedConfigurations" value-field="id" text-field="configuration" required/>
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
import { getAllProcesses, getCurrentUserProcesses, createProcess, createStep } from '../backend/processes'
export default {
  name: 'toolsPage',
  data () {
    return {
      auditor: ['Admin', 'Auditor'],
      toolsItems: this.tools(),
      toolsFields: [
        {key: 'icon', sortable: false},
        {key: 'name', sortable: true},
        {key: 'command', sortable: true},
        {key: 'stage', sortable: true},
        {key: 'intensities', sortable: true},
        {key: 'actions', sortable: false}
      ],
      configFields: [
        {key: 'configuration', sortable: true},
        {key: 'default', sortable: true},
        {key: 'inputs', sortable: true},
        {key: 'outputs', sortable: true}
      ],
      processesItems: this.processes(),
      selectedTool: null,
      selectedProcess: null,
      selectedConfigurations: [],
      selectedConfiguration: null,
      stepPriority: 1,
      processName: null,
      processDescription: null,
      newStepState: null,
      newProcessNameState: null,
      newProcessDescState: null
    }
  },
  methods: {
    tools () {
      var tools = []
      getTools()
        .then(results => {
          for (var i = 0; i < results.length; i++) {
            var configurations = []
            for (var c = 0; c < results[i].configurations.length; c++) {
              var inputs = ''
              for (var j = 0; j < results[i].configurations[c].inputs.length; j++) {
                inputs += results[i].configurations[c].inputs[j].type
                if (j + 1 < results[i].configurations[c].inputs.length) {
                  inputs += ', '
                }
              }
              var outputs = ''
              for (j = 0; j < results[i].configurations[c].outputs.length; j++) {
                outputs += results[i].configurations[c].outputs[j].type
                if (j + 1 < results[i].configurations[c].outputs.length) {
                  outputs += ', '
                }
              }
              var config = {
                id: results[i].configurations[c].id,
                configuration: results[i].configurations[c].name,
                default: results[i].configurations[c].default,
                inputs: inputs,
                outputs: outputs
              }
              configurations.push(config)
            }
            var intensities = []
            for (j = 0; j < results[i].intensities.length; j++) {
              var value = results[i].intensities[j].intensity_rank
              var variant = 'secondary'
              if (value === 'Sneaky') variant = 'info'
              else if (value === 'Low') variant = 'success'
              else if (value === 'Hard') variant = 'warning'
              else if (value === 'Insane') variant = 'danger'
              var intensity = {
                variant: variant,
                value: value,
                summary: value.charAt(0).toUpperCase()
              }
              intensities.push(intensity)
            }
            var item = {
              id: results[i].id,
              name: results[i].name,
              command: results[i].command,
              stage: results[i].stage_name,
              icon: results[i].icon,
              reference: results[i].reference,
              configurations: configurations,
              intensities: intensities
            }
            tools.push(item)
          }
        })
      return tools
    },
    async processes () {
      var processes = []
      if (this.$store.state.role !== 'Admin') {
        processes = await getCurrentUserProcesses(this.$store.state.user)
          .then(results => {
            return this.getProcesses(results)
          })
      } else {
        processes = await getAllProcesses()
          .then(results => {
            return this.getProcesses(results)
          })
      }
      return processes
    },
    getProcesses (apiData) {
      var processes = []
      for (var i = 0; i < apiData.length; i++) {
        var steps = []
        for (var s = 0; s < apiData[i].steps.length; s++) {
          var step = {
            tool: apiData[i].steps[s].tool.id,
            configuration: apiData[i].steps[s].configuration.id
          }
          steps.push(step)
        }
        var item = {
          id: apiData[i].id,
          name: apiData[i].name,
          steps: steps
        }
        processes.push(item)
      }
      return processes
    },
    handleNewStep (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.createNewStep()
    },
    createNewStep () {
      if (!this.checkNewStepState()) {
        return
      }
      createStep(this.selectedProcess, this.selectedTool.id, this.selectedConfiguration, this.stepPriority)
        .then(() => {
          this.$bvModal.hide('new-step-modal')
          this.$bvToast.toast('New step created successfully', {
            title: this.selectedTool.name,
            variant: 'success',
            solid: true
          })
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
    handleNewProcess (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.createNewProcess()
    },
    createNewProcess () {
      if (!this.checkNewProcessState()) {
        return
      }
      createProcess(this.processName, this.processDescription)
        .then(data => {
          createStep(data.id, this.selectedTool.id, this.selectedConfiguration, this.stepPriority)
            .then(() => {
              this.$bvModal.hide('new-process-modal')
              this.$bvToast.toast('New process created successfully', {
                title: this.processName,
                variant: 'success',
                solid: true
              })
            })
            .catch(() => {
              this.$bvToast.toast('Unexpected error in step creation', {
                title: this.selectedTool.name,
                variant: 'danger',
                solid: true
              })
            })
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
    selectTool (tool) {
      this.selectedTool = tool
      this.selectedConfigurations = tool.configurations
      this.selectedConfiguration = this.selectedConfigurations[0].id
    },
    resetModal () {
      this.selectedTool = null
      this.selectedProcess = null
      this.selectedConfigurations = []
      this.selectedConfiguration = null
      this.stepPriority = 1
      this.processName = null
      this.processDescription = null
      this.newStepState = null
      this.newProcessNameState = null
      this.newProcessDescState = null
    }
  }
}
</script>

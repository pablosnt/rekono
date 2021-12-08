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
        <b-button variant="success" class="mr-2" v-b-tooltip.hover title="Execute" @click="selectTool(row.item)" v-b-modal.execute-modal>
          <b-icon icon="play-fill"/>
        </b-button>
        <b-dropdown variant="outline-primary" right v-b-tooltip.hover title="Add to Process">
          <template #button-content>
            <b-icon icon="plus-square"/>
          </template>
          <b-dropdown-item @click="selectTool(row.item)" v-b-modal.new-process-modal >New Process</b-dropdown-item>
          <b-dropdown-item @click="selectTool(row.item)" v-b-modal.new-step-modal>New Step</b-dropdown-item>
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
    <ProcessForm id="new-process-modal"
      :tool="selectedTool"
      @confirm="confirm"
      @cancel="cleanSelection"/>
    <StepForm id="new-step-modal"
      :tool="selectedTool"
      @confirm="confirm"
      @cancel="cleanSelection"/>
    <!-- <b-modal id="execute-modal" @hidden="resetModal" @ok="handleExecute" ok-title="Execute" header-bg-variant="success" header-text-variant="light" ok-variant="success" size="lg">
      <template #modal-title>
        <b-link :href="selectedTool.reference" target="_blank">
          <b-img :src="selectedTool.icon" width="100" height="50"/>
        </b-link>
        Execute {{ selectedTool.name }}
      </template>
      <b-form ref="execute_form" @submit.stop.prevent="execute">
        <b-tabs fill card active-nav-item-class="text-success">
          <b-tab title-link-class="text-secondary">
            <template #title>
              <b-icon icon="play-fill"/> Basic
            </template>
            <b-form-group description="Project" invalid-feedback="Project is required">
              <b-form-select v-model="selectedProjectId" :options="projectsItems" @change="selectProject" value-field="id" text-field="name" :state="executeProjectState" required>
                <template #first>
                  <b-form-select-option :value="null" disabled>Select project</b-form-select-option>
                </template>
              </b-form-select>
            </b-form-group>
            <b-form-group description="Target" invalid-feedback="Target is required">
              <b-form-select v-model="selectedTarget" :disabled="selectedProjectId == null" :options="selectedTargets" @change="selectTarget" value-field="id" text-field="name" :state="executeTargetState" required>
                <template #first>
                  <b-form-select-option :value="null" disabled>Select target</b-form-select-option>
                </template>
              </b-form-select>
            </b-form-group>
            <b-form-group description="Tool configuration">
              <b-form-select v-model="selectedConfiguration" :options="selectedConfigurations" value-field="id" text-field="configuration" required/>
            </b-form-group>
            <b-form-group description="Execution intensity">
              <b-form-select v-model="selectedIntensity" :options="selectedIntensities" value-field="value" text-field="value" required/>
            </b-form-group>
          </b-tab>
          <b-tab title-link-class="text-secondary" v-if="checkInput('Wordlist')">
            <template #title>
              <b-icon icon="chat-left-dots-fill"/> Wordlists
            </template>
            <b-form-group>
              <b-form-select v-model="selectedWordlists" :options="wordlistsItems" multiple value-field="id" text-field="name"/>
            </b-form-group>
          </b-tab>
          <b-tab title-link-class="text-secondary">
            <template #title>
              <b-icon icon="clock-fill"/> Schedule
            </template>
            <label>Execute at specific time</label>
            <b-form-group>
              <b-form-datepicker v-model="scheduleAtDate" @input="cleanScheduledIn" :state="executeAtDateState"/>
            </b-form-group>
            <b-form-group>
              <b-form-timepicker v-model="scheduleAtTime" @input="cleanScheduledIn" :state="executeAtTimeState"/>
            </b-form-group>
            <hr/>
            <label>Execute after some time</label>
            <b-form-group description="Time value">
              <b-input-group :prepend="scheduleIn">
                <b-form-input v-model="scheduleIn" type="range" min="1" max="100" @change="cleanScheduledAt"/>
              </b-input-group>
            </b-form-group>
            <b-form-group description="Time unit">
              <b-form-select v-model="scheduleUnit" :options="timeUnits"/>
            </b-form-group>
          </b-tab>
          <b-tab title-link-class="text-secondary">
            <template #title>
              <b-icon icon="arrow-clockwise"/> Repeat
            </template>
            <label>Repeat execution periodically</label>
            <b-form-group description="Time value">
              <b-input-group :prepend="repeatIn">
                <b-form-input v-model="repeatIn" type="range" min="1" max="100"/>
              </b-input-group>
            </b-form-group>
            <b-form-group description="Time unit">
              <b-form-select v-model="repeatUnit" :options="timeUnits"/>
            </b-form-group>
          </b-tab>
          <b-tab title-link-class="text-secondary" v-if="checkInput('Host') || checkInput('Enumeration') || checkInput('Endpoint')">
            <template #title>
              <b-icon icon="clipboard-plus"/> Initial Data
            </template>
            <div class="text-right">
              <b-button size="md" variant="outline" v-b-tooltip.hover title="Add Host" @click="addInitialHost()" :disabled="!hostOptions">
                <p class="h4 mb-2"><b-icon variant="success" icon="plus-square-fill"/></p>
              </b-button>
              <b-button size="md" variant="outline" v-b-tooltip.hover title="This is an optional context to be used by the tool">
                <p class="h4 mb-2"><b-icon variant="info" icon="info-circle-fill"/></p>
              </b-button>
            </div>
            <b-container v-for="host in initialHosts" :key="host.id">
              <b-form-row>
                <b-col><b-form-input v-model="host.address" type="text" maxlength=30 placeholder="Address" :disabled="!hostOptions" @change="changeInitialData"></b-form-input></b-col>
                <b-col><b-form-select v-model="host.osType" :options="osTypes" @change="changeInitialData"/></b-col>
                <b-col>
                  <b-button size="md" variant="outline" v-b-tooltip.hover title="Add Enumeration" @click="addInitialEnumeration(host.id)" v-if="checkInput('Enumeration') || checkInput('Endpoint')" :disabled="!enumerationsOptions">
                    <b-icon variant="success" icon="plus-square-fill"/>
                  </b-button>
                  <b-button size="md" variant="outline" v-b-tooltip.hover title="Remove Host" @click="removeInitialHost(host.id)" :disabled="!hostOptions">
                    <b-icon variant="danger" icon="backspace-fill"/>
                  </b-button>
                </b-col>
              </b-form-row>
              <b-container v-for="enumeration in host.enumerations" :key="enumeration.id">
                <b-form-row>
                  <b-col lg="1"></b-col>
                  <b-col><b-form-input v-model="enumeration.port" type="number" placeholder="Port" :disabled="!enumerationsOptions" @change="changeInitialData"></b-form-input></b-col>
                  <b-col><b-form-select v-model="enumeration.protocol" :options="protocols" @change="changeInitialData"/></b-col>
                  <b-col><b-form-input v-model="enumeration.service" type="text" maxlength=50 placeholder="Service" @change="changeInitialData"></b-form-input></b-col>
                  <b-col>
                    <b-button size="md" variant="outline" v-b-tooltip.hover title="Add Endpoint" @click="addInitialEndpoint(host.id, enumeration.id)" v-if="checkInput('Endpoint')">
                      <b-icon variant="success" icon="plus-square-fill"/>
                    </b-button>
                    <b-button size="md" variant="outline" v-b-tooltip.hover title="Remove Enumeration" @click="removeInitialEnumeration(host.id, enumeration.id)">
                      <b-icon variant="danger" icon="backspace-fill"/>
                    </b-button>
                  </b-col>
                </b-form-row>
                <b-form-row v-for="endpoint in enumeration.endpoints" :key="endpoint.id">
                  <b-col lg="2"></b-col>
                  <b-col><b-form-input v-model="endpoint.endpoint" type="text" maxlength=500 placeholder="Endpoint" @change="changeInitialData"></b-form-input></b-col>
                  <b-col>
                    <b-button size="md" variant="outline" v-b-tooltip.hover title="Remove Endpoint" @click="removeInitialEndpoint(host.id, enumeration.id, endpoint.id)">
                      <b-icon variant="danger" icon="backspace-fill"/>
                    </b-button>
                  </b-col>
                </b-form-row>
              </b-container>
            </b-container>
          </b-tab>
        </b-tabs>
      </b-form>
    </b-modal> -->
  </div>
</template>

<script>
import { getTools } from '../backend/tools'
import { getCurrentUserProjects } from '../backend/projects'
import { getAllWordlists } from '../backend/resources'
import { createTask } from '../backend/tasks'
import ProcessForm from './forms/ProcessForm.vue'
import StepForm from './forms/StepForm.vue'
export default {
  name: 'toolsPage',
  data () {
    return {
      auditor: ['Admin', 'Auditor'],
      toolsItems: this.tools(),
      toolsFields: [
        {key: 'icon', sortable: false},
        {key: 'name', label: 'Tool', sortable: true},
        {key: 'command', sortable: true},
        {key: 'stage', sortable: true},
        {key: 'intensities', sortable: true},
        {key: 'actions', sortable: false}
      ],
      configFields: [
        {key: 'name', label: 'Configuration', sortable: true},
        {key: 'default', sortable: true},
        {key: 'inputs', sortable: true},
        {key: 'outputs', sortable: true}
      ],
      projectsItems: this.projects(),
      wordlistsItems: this.wordlists(),
      selectedTool: null,
      selectedConfigurations: [],
      selectedConfiguration: null,
      selectedProject: null,
      selectedProjectId: null,
      selectedTargets: [],
      selectedTarget: null,
      selectedIntensities: [],
      selectedIntensity: null,
      timeUnits: ['Weeks', 'Days', 'Hours', 'Minutes'],
      scheduleAtDate: null,
      scheduleAtTime: null,
      scheduleUnit: 'Minutes',
      scheduleIn: null,
      repeatUnit: 'Minutes',
      repeatIn: null,
      selectedWordlists: [],
      osTypes: ['Linux', 'Windows', 'MacOS', 'iOS', 'Android', 'Solaris', 'FreeBSD', 'Other'],
      protocols: ['TCP', 'UDP'],
      initialHosts: [],
      hostId: 0,
      enumerationId: 0,
      endpointId: 0,
      executeProjectState: null,
      executeTargetState: null,
      executeAtDateState: null,
      executeAtTimeState: null,
      hostOptions: true,
      enumerationsOptions: true,
      initialDataChanged: false
    }
  },
  components: {
    ProcessForm,
    StepForm
  },
  methods: {
    confirm (operation) {
      if (operation.success) {
        this.$bvModal.hide(operation.id)
        this.toolsItems = this.tools()
      }
    },
    cleanSelection () {
      this.selectedTool = null
    },
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
                name: results[i].configurations[c].name,
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
    projects () {
      var projects = []
      getCurrentUserProjects(this.$store.state.user)
        .then(results => {
          for (var p = 0; p < results.length; p++) {
            var targets = []
            for (var t = 0; t < results[p].targets.length; t++) {
              var ports = []
              for (var i = 0; i < results[p].targets[t].target_ports.length; i++) {
                ports.push(results[p].targets[t].target_ports[i].port)
              }
              var target = {
                id: results[p].targets[t].id,
                name: results[p].targets[t].target,
                type: results[p].targets[t].type,
                ports: ports
              }
              targets.push(target)
            }
            var item = {
              id: results[p].id,
              name: results[p].name,
              targets: targets
            }
            projects.push(item)
          }
        })
      return projects
    },
    wordlists () {
      var wordlists = []
      getAllWordlists()
        .then(results => {
          for (var w = 0; w < results.length; w++) {
            var item = {
              id: results[w].id,
              name: results[w].name
            }
            wordlists.push(item)
          }
        })
      return wordlists
    },
    handleExecute (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.execute()
    },
    execute () {
      if (!this.checkExecuteState()) {
        return
      }
      var initialData = []
      if (this.initialDataChanged) {
        for (var h = 0; h < this.initialHosts.length; h++) {
          if (this.initialHosts[h].address === null) {
            continue
          }
          var host = {
            address: this.initialHosts[h].address,
            os_type: this.initialHosts[h].osType,
            enumerations: []
          }
          for (var e = 0; e < this.initialHosts[h].enumerations.length; e++) {
            if (this.initialHosts[h].enumerations[e].port === null) {
              continue
            }
            var enumeration = {
              port: this.initialHosts[h].enumerations[e].port,
              protocol: this.initialHosts[h].enumerations[e].protocol,
              service: this.initialHosts[h].enumerations[e].service,
              endpoints: []
            }
            for (var end = 0; end < this.initialHosts[h].enumerations[e].endpoints.length; end++) {
              if (this.initialHosts[h].enumerations[e].endpoints[end].endpoint != null) {
                enumeration.push({ endpoint: this.initialHosts[h].enumerations[e].endpoints[end].endpoint })
              }
            }
            host.enumerations.push(enumeration)
          }
          initialData.push(host)
        }
      }
      createTask(this.selectedTarget, null, this.selectedTool.id, this.selectedConfiguration, this.selectedIntensity, this.scheduleAtDate, this.scheduleAtTime, this.scheduleIn, this.scheduleUnit, this.repeatIn, this.repeatUnit, this.wordlists, initialData)
        .then(() => {
          this.$bvModal.hide('execute-modal')
          this.$bvToast.toast('Execution requested successfully', {
            title: this.selectedTool.name,
            variant: 'success',
            solid: true
          })
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in execution request', {
            title: this.selectedTool.name,
            variant: 'danger',
            solid: true
          })
        })
    },
    checkExecuteState () {
      const valid = this.$refs.execute_form.checkValidity()
      this.executeProjectState = (this.selectedProjectId !== null)
      this.executeTargetState = (this.selectedTarget !== null)
      if (this.scheduleAtDate !== null || this.scheduleAtTime !== null) {
        this.executeAtDateState = (this.scheduleAtDate !== null)
        this.executeAtTimeState = (this.scheduleAtTime !== null)
        return valid && this.executeAtDateState && this.executeAtTimeState
      }
      return valid
    },
    cleanScheduledAt () {
      this.scheduleAtDate = null
      this.scheduleAtTime = null
    },
    cleanScheduledIn () {
      this.scheduleIn = null
    },
    checkInput (inputType) {
      if (this.selectedConfiguration !== null) {
        for (var c = 0; c < this.selectedConfigurations.length; c++) {
          if (this.selectedConfigurations[c].id === this.selectedConfiguration) {
            return this.selectedConfigurations[c].inputs.includes(inputType)
          }
        }
      }
      return false
    },
    addInitialHost () {
      this.hostId++
      var item = {
        id: this.hostId,
        address: null,
        osType: 'Other',
        enumerations: []
      }
      this.initialHosts.push(item)
    },
    removeInitialHost (hostId) {
      var index = null
      for (var i = 0; i < this.initialHosts.length; i++) {
        if (this.initialHosts[i].id === hostId) {
          index = i
          break
        }
      }
      this.initialHosts.splice(index, 1)
    },
    addInitialEnumeration (hostId) {
      this.enumerationId++
      var item = {
        id: this.enumerationId,
        port: null,
        protocol: 'TCP',
        service: null,
        endpoints: []
      }
      for (var h = 0; h < this.initialHosts.length; h++) {
        if (this.initialHosts[h].id === hostId) {
          this.initialHosts[h].enumerations.push(item)
          break
        }
      }
    },
    removeInitialEnumeration (hostId, enumerationId) {
      var hostIndex = null
      var enumIndex = null
      for (var h = 0; h < this.initialHosts.length; h++) {
        if (this.initialHosts[h].id === hostId) {
          hostIndex = h
          for (var e = 0; e < this.initialHosts[h].enumerations.length; e++) {
            if (this.initialHosts[h].enumerations[e].id === enumerationId) {
              enumIndex = e
              break
            }
          }
          break
        }
      }
      this.initialHosts[hostIndex].enumerations.splice(enumIndex, 1)
    },
    addInitialEndpoint (hostId, enumerationId) {
      this.endpointId++
      var item = {
        id: this.endpointId,
        endpoint: null
      }
      for (var h = 0; h < this.initialHosts.length; h++) {
        if (this.initialHosts[h].id === hostId) {
          for (var e = 0; e < this.initialHosts[h].enumerations.length; e++) {
            if (this.initialHosts[h].enumerations[e].id === enumerationId) {
              this.initialHosts[h].enumerations[e].endpoints.push(item)
              break
            }
          }
          break
        }
      }
    },
    removeInitialEndpoint (hostId, enumerationId, endpointId) {
      var hostIndex = null
      var enumIndex = null
      var endpointIndex = null
      for (var h = 0; h < this.initialHosts.length; h++) {
        if (this.initialHosts[h].id === hostId) {
          hostIndex = h
          for (var e = 0; e < this.initialHosts[h].enumerations.length; e++) {
            if (this.initialHosts[h].enumerations[e].id === enumerationId) {
              enumIndex = e
              for (var end = 0; end < this.initialHosts[h].enumerations[e].endpoints.length; end++) {
                if (this.initialHosts[h].enumerations[e].endpoints[end].id === endpointId) {
                  endpointIndex = end
                  break
                }
              }
              break
            }
          }
          break
        }
      }
      this.initialHosts[hostIndex].enumerations[enumIndex].endpoints.splice(endpointIndex, 1)
    },
    changeInitialData () {
      this.initialDataChanged = true
    },
    selectTool (tool) {
      this.selectedTool = tool
      this.selectedConfigurations = tool.configurations
      this.selectedConfiguration = this.selectedConfigurations[0].id
      this.selectedIntensities = tool.intensities
      for (var i = 0; i < this.selectedIntensities.length; i++) {
        if (this.selectedIntensities[i].value === 'Normal') {
          this.selectedIntensity = 'Normal'
          break
        }
      }
      if (this.selectedIntensity !== 'Normal') {
        this.selectedIntensity = this.selectedIntensities[this.selectedIntensities.length - 1].value
      }
    },
    selectProject (projectId) {
      this.selectedProjectId = projectId
      for (var p = 0; p < this.projectsItems.length; p++) {
        if (this.projectsItems[p].id === projectId) {
          this.selectedProject = this.projectsItems[p]
        }
      }
      this.selectedTargets = this.selectedProject.targets
    },
    selectTarget (targetId) {
      this.selectedTarget = targetId
      for (var t = 0; t < this.selectedTargets.length; t++) {
        if (this.selectedTargets[t].id === targetId) {
          this.selectedTargetType = this.selectedTargets[t].type
          if (this.selectedTargets[t].type !== 'Network' && this.selectedTargets[t].type !== 'IP range' && this.initialHosts.length === 0) {
            this.hostOptions = false
            var enumerations = []
            for (var p = 0; p < this.selectedTargets[t].ports.length; p++) {
              this.enumerationsOptions = false
              this.enumerationId++
              var enumeration = {
                id: this.enumerationId,
                port: this.selectedTargets[t].ports[p],
                protocol: 'TCP',
                service: null,
                endpoints: []
              }
              enumerations.push(enumeration)
            }
            this.hostId++
            var host = {
              id: this.hostId,
              address: this.selectedTargets[t].name,
              osType: 'Other',
              enumerations: enumerations
            }
            this.initialHosts.push(host)
          }
          break
        }
      }
    },
    resetModal () {
      this.selectedTool = null
      this.selectedProcess = null
      this.selectedConfigurations = []
      this.selectedConfiguration = null
      this.selectedProject = null
      this.selectedProjectId = null
      this.selectedTargets = []
      this.selectedTarget = null
      this.selectedTargetType = null
      this.selectedIntensities = []
      this.selectedIntensity = null
      this.stepPriority = 1
      this.processName = null
      this.processDescription = null
      this.newStepState = null
      this.newProcessNameState = null
      this.newProcessDescState = null
      this.scheduleAtDate = null
      this.scheduleAtTime = null
      this.scheduleUnit = 'Minutes'
      this.scheduleIn = null
      this.repeatUnit = 'Minutes'
      this.repeatIn = null
      this.selectedWordlists = []
      this.initialHosts = []
      this.hostId = 0
      this.enumerationId = 0
      this.endpointId = 0
      this.executeProjectState = null
      this.executeTargetState = null
      this.executeAtDateState = null
      this.executeAtTimeState = null
      this.hostOptions = true
      this.enumerationsOptions = true
      this.initialDataChanged = false
    }
  }
}
</script>

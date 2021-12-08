<template>
  <b-modal id="execute-modal" @hidden="cancel" @ok="confirm" header-bg-variant="success" header-text-variant="light" ok-variant="success" size="lg">
    <template #modal-title>
      <b-link :href="tool.reference" target="_blank" v-if="tool !== null">
        <b-img :src="tool.icon" width="100" height="50"/>
      </b-link>
      {{ title }}
    </template>
    <b-form ref="execute_form">
      <b-tabs fill card active-nav-item-class="text-success">
        <b-tab title-link-class="text-secondary">
          <template #title>
            <b-icon icon="play-fill"/> Basic
          </template>
          <b-form-group description="Project" invalid-feedback="Project is required">
            <b-form-select v-model="projectId" :options="projects" @change="selectProject" value-field="id" text-field="name" :state="projectState" required>
              <template #first>
                <b-form-select-option :value="null" disabled>Select project</b-form-select-option>
              </template>
            </b-form-select>
          </b-form-group>
          <b-form-group description="Target" invalid-feedback="Target is required">
            <b-form-select v-model="targetId" :options="selectedProject !== null ? selectedProject.targets : []" :disabled="selectedProject === null" value-field="id" text-field="target" :state="targetState" required>
              <template #first>
                <b-form-select-option :value="null" disabled>Select target</b-form-select-option>
              </template>
            </b-form-select>
          </b-form-group>
          <b-form-group description="Tool configuration">
            <b-form-select v-model="configurationId" :options="selectedTool !== null ? selectedTool.configurations : []" :disabled="configurationId == null" @change="selectConfiguration" value-field="id" text-field="name" required/>
          </b-form-group>
          <b-form-group description="Execution intensity">
            <b-form-select v-model="intensity" :options="intensities" value-field="value" text-field="value" required/>
          </b-form-group>
        </b-tab>
        <b-tab title-link-class="text-secondary" v-if="checkInputType('Wordlist')">
          <template #title>
            <b-icon icon="chat-left-dots-fill"/> Wordlists
          </template>
          <b-form-group>
            <b-form-select v-model="wordlistsItems" :options="wordlists" multiple value-field="id" text-field="name"/>
          </b-form-group>
        </b-tab>
        <b-tab title-link-class="text-secondary">
          <template #title>
            <b-icon icon="clock-fill"/> Schedule
          </template>
          <label>Execute at specific time</label>
          <b-form-group>
            <b-form-datepicker v-model="scheduledAtDate" @input="cleanScheduledIn" :state="scheduledAtDateState" :date-disabled-fn="dateBeforeToday" today-button reset-button close-button/>
          </b-form-group>
          <b-form-group invalid-feedback="Time is required and must be future">
            <b-form-timepicker v-model="scheduledAtTime" @input="cleanScheduledIn" :state="scheduledAtTimeState"/>
          </b-form-group>
          <hr/>
          <label>Execute after some time</label>
          <b-form-group description="Time value">
            <b-input-group :prepend="scheduledIn">
              <b-form-input v-model="scheduledIn" type="range" min="1" max="100" @change="cleanScheduledAt"/>
            </b-input-group>
          </b-form-group>
          <b-form-group description="Time unit">
            <b-form-select v-model="scheduledTimeUnit" :options="timeUnits"/>
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
            <b-form-select v-model="repeatTimeUnit" :options="timeUnits"/>
          </b-form-group>
        </b-tab>
      </b-tabs>
    </b-form>
  </b-modal>
</template>

<script>
import { getCurrentUserProjects } from '../../backend/projects'
import { getAllWordlists } from '../../backend/resources'
import { createTask } from '../../backend/tasks'
import { getAllProcesses } from '../../backend/processes'
import { getTools } from '../../backend/tools'
export default {
  name: 'taskForm',
  props: {
    id: String,
    process: {
      type: Object,
      default: null
    },
    tool: {
      type: Object,
      default: null
    }
  },
  computed: {
    title () {
      var title = 'New Task'
      if (this.process !== null) {
        title = 'Execute ' + this.process.name
      } else if (this.tool !== null) {
        title = 'Execute ' + this.tool.name
      }
      return title
    },
    projects () {
      return this.getProjects()
    },
    processes () {
      if (this.process === null) {
        return this.getProcesses()
      }
      return []
    },
    tools () {
      if (this.tools === null) {
        return this.getTools()
      }
      return []
    },
    wordlists () {
      return this.getWordlists()
    }
  },
  data () {
    return {
      intensities: ['Insane', 'Hard', 'Normal', 'Low', 'Sneaky'],
      timeUnits: ['Weeks', 'Days', 'Hours', 'Minutes'],
      selectedProject: null,
      selectedProcess: null,
      selectedTool: null,
      selectedConfiguration: null,
      projectId: null,
      targetId: null,
      processId: null,
      toolId: null,
      configurationId: null,
      intensity: null,
      wordlistsItems: [],
      scheduledAtDate: null,
      scheduledAtTime: null,
      scheduledIn: null,
      scheduledTimeUnit: 'Minutes',
      repeatIn: null,
      repeatTimeUnit: 'Days',
      projectState: null,
      targetState: null,
      scheduledAtDateState: null,
      scheduledAtTimeState: null
    }
  },
  watch: {
    process (process) {
      if (process !== null) {
        this.selectProcess(process.id, process)
      }
    },
    tool (tool) {
      if (tool !== null) {
        this.selectTool(tool.id, tool)
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.execute_form.checkValidity()
      this.projectState = (this.projectId !== null)
      this.targetState = (this.targetId !== null)
      if (this.scheduledAtDate !== null || this.scheduledAtTime !== null) {
        this.scheduledAtDateState = (this.scheduledAtDate !== null)
        if (this.scheduledAtDateState && this.scheduledAtTime !== null) {
          var today = new Date()
          var selected = Date.parse(this.scheduledAtDate + ' ' + this.scheduledAtTime)
          this.scheduledAtTimeState = (this.scheduledAtTime !== null && selected > today)
          return valid && this.scheduledAtDateState && this.scheduledAtTimeState
        }
        return false
      }
      return valid
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.create().then((success) => this.$emit('confirm', { id: this.id, success: success }))
      }
    },
    create () {
      return createTask(this.targetId, this.processId, this.toolId, this.configurationId, this.intensity, this.scheduledAtDate, this.scheduledAtTime, this.scheduledIn, this.scheduledTimeUnit, this.repeatIn, this.repeatTimeUnit, this.wordlists)
        .then(() => {
          this.$bvModal.hide('execute-modal')
          this.$bvToast.toast('Execution requested successfully', {
            title: this.selectedTool.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in execution request', {
            title: this.selectedTool.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    cancel () {
      this.intensities = ['Insane', 'Hard', 'Normal', 'Low', 'Sneaky']
      this.timeUnits = ['Weeks', 'Days', 'Hours', 'Minutes']
      this.selectedProject = null
      this.selectedProcess = null
      this.selectedTool = null
      this.selectedConfiguration = null
      this.projectId = null
      this.targetId = null
      this.processId = null
      this.toolId = null
      this.configurationId = null
      this.intensity = null
      this.wordlistsItems = []
      this.scheduledAtDate = null
      this.scheduledAtTime = null
      this.scheduledIn = null
      this.scheduledTimeUnit = 'Minutes'
      this.repeatIn = null
      this.repeatTimeUnit = 'Days'
      this.projectState = null
      this.targetState = null
      this.scheduledAtDateState = null
      this.scheduledAtTimeState = null
    },
    dateBeforeToday (value, date) {
      var today = new Date()
      date.setTime(today.getTime())
      return date < today
    },
    selectProject (projectId, project = null) {
      this.projectId = projectId
      if (project !== null) {
        this.selectedProject = project
      } else {
        this.selectedProject = this.findById(this.projects, projectId)
      }
    },
    selectProcess (processId, process = null) {
      this.processId = processId
      this.toolId = null
      this.configurationId = null
      this.intensities = ['Insane', 'Hard', 'Normal', 'Low', 'Sneaky']
      if (process !== null) {
        this.selectedProcess = process
      } else {
        this.selectedProcess = this.findById(this.processes, processId)
      }
    },
    selectTool (toolId, tool = null) {
      this.processId = null
      this.toolId = toolId
      if (tool !== null) {
        this.selectedTool = tool
      } else {
        this.selectedTool = this.findById(this.tools, toolId)
      }
      this.selectConfiguration(this.selectedTool.configurations[0].id, this.selectedTool.configurations[0])
      this.intensities = this.selectedTool.intensities
      this.intensity = null
      for (var i = 0; i < this.intensities.length; i++) {
        if (this.intensities[i].value === 'Normal') {
          this.intensity = 'Normal'
          break
        }
      }
      if (this.intensity === null) {
        this.intensity = this.intensities[this.intensities.length - 1].value
      }
    },
    selectConfiguration (configurationId, configuration = null) {
      this.configurationId = configurationId
      if (configuration !== null) {
        this.selectedConfiguration = configuration
      } else {
        this.selectedConfiguration = this.findById(this.selectedTool.configurations, configurationId)
      }
    },
    checkInputType (inputType) {
      var inputs = []
      if (this.selectedConfiguration !== null) {
        inputs = this.selectedConfiguration.inputs
      } else if (this.selectedProcess !== null) {
        for (var s = 0; s < this.selectedProcess.steps.length; s++) {
          inputs = inputs.concat(this.selectedProcess.steps[s].configuration.inputs)
        }
      }
      var check = false
      for (var i = 0; i < inputs; i++) {
        if (inputType === inputs[i].type) {
          check = true
          break
        }
      }
      return check
    },
    cleanScheduledIn () {
      this.scheduledIn = null
    },
    cleanScheduledAt () {
      this.scheduledAtDate = null
      this.scheduledAtTime = null
    },
    findById (data, id) {
      for (var i = 0; i < data.length; i++) {
        if (data[i].id === id) {
          return data[i]
        }
      }
      return null
    },
    getProjects () {
      var projects = []
      getCurrentUserProjects(this.$store.state.user)
        .then(results => {
          for (var p = 0; p < results.length; p++) {
            var targets = []
            for (var t = 0; t < results[p].targets.length; t++) {
              var target = {
                id: results[p].targets[t].id,
                target: results[p].targets[t].target,
                type: results[p].targets[t].type
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
    getWordlists () {
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
    getTools () {
      var tools = []
      getTools()
        .then(results => {
          for (var i = 0; i < results.length; i++) {
            var configurations = []
            for (var c = 0; c < results[i].configurations.length; c++) {
              var config = {
                id: results[i].configurations[c].id,
                name: results[i].configurations[c].name,
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
    getProcesses () {
      var processes = []
      getAllProcesses(this.$store.state.user)
        .then(results => {
          for (var i = 0; i < results.length; i++) {
            var steps = []
            for (var s = 0; s < results[i].steps.length; s++) {
              var step = {
                tool: results[i].steps[s].tool.id,
                configuration: results[i].steps[s].configuration.id
              }
              steps.push(step)
            }
            var item = {
              id: results[i].id,
              name: results[i].name,
              steps: steps
            }
            processes.push(item)
          }
        })
      return processes
    }
  }
}
</script>

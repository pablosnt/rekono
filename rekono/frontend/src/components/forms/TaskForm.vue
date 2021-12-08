<template>
  <b-modal id="execute-modal" @hidden="clean" @ok="confirm" header-bg-variant="success" header-text-variant="light" ok-variant="success" size="lg">
    <template #modal-title>
      <div v-if="tool !== null">
        <b-link :href="tool.reference" target="_blank">
          <b-img :src="tool.icon" width="100" height="50"/>
        </b-link>
      </div>
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
          <div v-if="tool !== null">
            <b-form-group description="Tool configuration">
              <b-form-select v-model="configurationId" :options="selectedTool !== null ? selectedTool.configurations : []" :disabled="configurationId == null" @change="selectConfiguration" value-field="id" text-field="name" required/>
            </b-form-group>
          </div>
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
            <b-form-datepicker v-model="scheduledAtDate" @input="cleanScheduledIn" :state="scheduledAtState" :min="minimumDate" today-button reset-button close-button/>
          </b-form-group>
          <b-form-group invalid-feedback="Time is required and must be future">
            <b-form-timepicker v-model="scheduledAtTime" @input="cleanScheduledIn" :state="scheduledAtState"/>
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
import { createTask } from '../../backend/tasks'
import { getCurrentUserProjects } from '../../backend/projects'
import { getAllWordlists } from '../../backend/resources'
import { getAllProcesses } from '../../backend/processes'
import { getTools } from '../../backend/tools'
import { findById } from '../../backend/utils'
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
    }
  },
  data () {
    getCurrentUserProjects(this.$store.state.user).then(projects => { this.projects = projects })
    return {
      initialized: false,
      projects: [],
      processes: [],
      tools: [],
      wordlists: [],
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
      intensity: 'Normal',
      wordlistsItems: [],
      scheduledAtDate: null,
      scheduledAtTime: null,
      scheduledIn: null,
      scheduledTimeUnit: 'Minutes',
      repeatIn: null,
      repeatTimeUnit: 'Days',
      projectState: null,
      targetState: null,
      scheduledAtState: null,
      minimumDate: new Date()
    }
  },
  watch: {
    process (process) {
      if (process !== null) {
        this.initialized = true
        this.selectProcess(process.id, process)
      }
    },
    tool (tool) {
      if (tool !== null) {
        this.initialized = true
        this.selectTool(tool.id, tool)
      }
    },
    initialized (initialized) {
      if (this.tool === null && this.process === null) {
        getTools().then(tools => { this.tools = tools })
        getAllProcesses().then(processes => { this.processes = processes })
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.execute_form.checkValidity()
      this.projectState = (this.projectId !== null)
      this.targetState = (this.targetId !== null)
      if (this.scheduledAtDate !== null || this.scheduledAtTime !== null) {
        this.scheduledAtState = false
        if (this.scheduledAtDate && this.scheduledAtTime !== null) {
          this.scheduledAtState = (Date.parse(this.scheduledAtDate + ' ' + this.scheduledAtTime) > new Date())
        }
        return valid && this.scheduledAtState
      }
      return valid
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.create().then((success) => this.$emit('confirm', { id: this.id, success: success, reload: false }))
      }
    },
    create () {
      var notification = null
      if (this.selectedTool !== null) notification = this.selectedTool.name
      else if (this.selectedProcess !== null) notification = this.selectedProcess.name
      return createTask(this.targetId, this.processId, this.toolId, this.configurationId, this.intensity, this.scheduledAtDate, this.scheduledAtTime, this.scheduledIn, this.scheduledTimeUnit, this.repeatIn, this.repeatTimeUnit, this.wordlistsItems)
        .then(() => {
          this.$bvModal.hide('execute-modal')
          this.$bvToast.toast('Execution requested successfully', {
            title: notification,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in execution request', {
            title: notification,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    clean () {
      this.initialized = false
      this.processes = []
      this.tools = []
      this.wordlists = []
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
      this.intensity = 'Normal'
      this.wordlistsItems = []
      this.scheduledAtDate = null
      this.scheduledAtTime = null
      this.scheduledIn = null
      this.scheduledTimeUnit = 'Minutes'
      this.repeatIn = null
      this.repeatTimeUnit = 'Days'
      this.projectState = null
      this.targetState = null
      this.scheduledAtState = null
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
      for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type === inputType) {
          check = true
          break
        }
      }
      return check
    },
    selectProject (projectId, project = null) {
      this.projectId = projectId
      if (project !== null) {
        this.selectedProject = project
      } else {
        this.selectedProject = findById(this.projects, projectId)
      }
    },
    selectProcess (processId, process = null) {
      const isWordlist = this.checkInputType('Wordlist')
      this.processId = processId
      this.toolId = null
      this.configurationId = null
      this.intensities = ['Insane', 'Hard', 'Normal', 'Low', 'Sneaky']
      this.intensity = 'Normal'
      if (process !== null) {
        this.selectedProcess = process
      } else {
        this.selectedProcess = findById(this.processes, processId)
      }
      if (!isWordlist && this.checkInputType('Wordlist')) {
        this.updateWordlists()
      }
    },
    selectTool (toolId, tool = null) {
      this.processId = null
      this.toolId = toolId
      if (tool !== null) {
        this.selectedTool = tool
      } else {
        this.selectedTool = findById(this.tools, toolId)
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
      const isWordlist = this.checkInputType('Wordlist')
      this.configurationId = configurationId
      if (configuration !== null) {
        this.selectedConfiguration = configuration
      } else {
        this.selectedConfiguration = findById(this.selectedTool.configurations, configurationId)
      }
      if (!isWordlist && this.checkInputType('Wordlist')) {
        this.updateWordlists()
      }
    },
    updateWordlists () {
      getAllWordlists().then(wordlists => { this.wordlists = wordlists })
    },
    cleanScheduledIn () {
      this.scheduledIn = null
    },
    cleanScheduledAt () {
      this.scheduledAtDate = null
      this.scheduledAtTime = null
    }
  }
}
</script>

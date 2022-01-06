<template>
  <b-modal id="execute-modal" @hidden="clean" @ok="confirm" :title="title" ok-title="Execute" header-bg-variant="success" header-text-variant="light" ok-variant="success" size="lg">
    <template #modal-title v-if="selectedTool">
      <b-link :href="selectedTool.reference" target="_blank">
        <b-img :src="selectedTool.icon" width="100" height="50"/>
      </b-link>
      {{ title }}
    </template>
    <b-form ref="execute_form">
      <b-tabs fill card active-nav-item-class="text-success">
        <b-tab title-link-class="text-secondary">
          <template #title>
            <b-icon icon="play-fill"/> Basic
          </template>
          <b-form-group description="Project" invalid-feedback="Project is required" v-if="!project && !target">
            <b-form-select v-model="projectId" :options="projects" @change="selectProject" value-field="id" text-field="name" :state="projectState">
              <template #first>
                <b-form-select-option :value="null" disabled>Select project</b-form-select-option>
              </template>
            </b-form-select>
          </b-form-group>
          <b-form-group description="Target" invalid-feedback="Target is required" v-if="!target">
            <b-form-select v-model="targetId" :options="targets" :disabled="!selectedProject" value-field="id" text-field="target" :state="targetState">
              <template #first>
                <b-form-select-option :value="null" disabled>Select target</b-form-select-option>
              </template>
            </b-form-select>
          </b-form-group>
          <b-form-group description="Process" v-if="!process && !tool">
            <b-form-select v-model="processId" :options="processes" @change="selectProcess" value-field="id" text-field="name" :state="processState"/>
          </b-form-group>
          <b-form-group description="Tool" v-if="!process && !tool">
            <b-form-select v-model="toolId" :options="tools" @change="selectTool" value-field="id" text-field="name" :state="toolState"/>
          </b-form-group>
          <b-form-group description="Tool configuration" v-if="!process">
            <b-form-select v-model="configurationId" :options="selectedTool ? selectedTool.configurations : []" :disabled="!configurationId" @change="selectConfiguration" value-field="id" text-field="name"/>
          </b-form-group>
          <b-form-group description="Execution intensity">
            <b-input-group>
              <b-input-group-prepend>
                <div v-for="i in intensities" :key="i.value">
                  <b-button v-if="i.intensity_rank === intensity" v-b-tooltip.hover.top="i.intensity_rank" :variant="i.variant" no-remove>{{ intensity ? intensity.charAt(0) : 'H' }}</b-button>
                </div>
              </b-input-group-prepend>
              <b-form-select v-model="intensity" :options="intensities" value-field="intensity_rank" text-field="intensity_rank" required/>
            </b-input-group>
          </b-form-group>
        </b-tab>
        <b-tab title-link-class="text-secondary" v-if="checkInputType('Wordlist')">
          <template #title>
            <b-icon icon="file-earmark-word-fill"/> Wordlists
          </template>
          <b-form-group description="Select wordlists to use">
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
import Processes from '@/backend/processes'
import ProjectApi from '@/backend/projects'
import TaskApi from '@/backend/tasks'
import ToolApi from '@/backend/tools'
import WordlistApi from '@/backend/resources'
import { intensitiesByVariant } from '@/backend/constants'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import { findById } from '@/backend/utils'
const ProcessApi = Processes.ProcessApi
export default {
  name: 'taskForm',
  mixins: [AlertMixin],
  props: {
    id: String,
    process: {
      type: Object,
      default: null
    },
    tool: {
      type: Object,
      default: null
    },
    project: {
      type: Object,
      default: null
    },
    target: {
      type: Object,
      default: null
    },
    reload: {
      type: Boolean,
      default: false
    },
    initialized: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    title () {
      let title = 'New Task'
      if (this.process !== null) {
        title = `Execute ${this.process.name}`
      } else if (this.tool !== null) {
        title = `Execute ${this.tool.name}`
      }
      return title
    }
  },
  data () {
    return {
      projects: [],
      targets: [],
      processes: [],
      tools: [],
      wordlists: [],
      intensities: intensitiesByVariant,
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
      processState: null,
      toolState: null,
      scheduledAtState: null,
      minimumDate: new Date()
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized) {
        if (this.tool) {
          this.selectTool(this.tool.id, this.tool)
        }
        if (this.process) {
          this.selectProcess(this.process.id, this.process)
        }
        if (!this.tool && !this.process) {
          ToolApi.getTools().then(data => { this.tools = data.results })
          ProcessApi.getAllProcesses().then(data => { this.processes = data.results })
        }
        if (this.target) {
          this.targetId = this.target.id
          this.targets = [this.target]
        } else if (this.project) {
          ProjectApi.getProject(this.project.id).then(data => { this.selectProject(this.project.id, data) })
        } else {
          ProjectApi.getAllProjects().then(data => { this.projects = data.results })
        }
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.execute_form.checkValidity()
      this.projectState = (this.projectId && this.projectId > 0)
      this.targetState = (this.targetId && this.targetId > 0)
      if (!this.processId && !this.toolId) {
        this.processState = false
        this.toolState = false
      }      
      if (this.scheduledAtDate || this.scheduledAtTime) {
        this.scheduledAtState = false
        if (this.scheduledAtDate && this.scheduledAtTime) {
          this.scheduledAtState = (Date.parse(`${this.scheduledAtDate} ${this.scheduledAtTime}`) > new Date())
        }
        return valid && this.scheduledAtState
      }
      return valid
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.create().then((success) => this.$emit('confirm', { id: this.id, success: success, reload: this.reload }))
      }
    },
    create () {
      let notification = null
      if (this.selectedTool !== null) notification = this.selectedTool.name
      else if (this.selectedProcess !== null) notification = this.selectedProcess.name
      return TaskApi.createTask(this.targetId, this.processId, this.toolId, this.configurationId, this.intensity, this.scheduledAtDate, this.scheduledAtTime, this.scheduledIn, this.scheduledTimeUnit, this.repeatIn, this.repeatTimeUnit, this.wordlistsItems)
        .then(() => {
          this.$bvModal.hide('execute-modal')
          this.success(notification, 'Execution requested successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(notification, 'Unexpected error in execution request')
          return Promise.resolve(false)
        })
    },
    clean () {
      this.processes = []
      this.tools = []
      this.wordlists = []
      this.intensities = intensitiesByVariant
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
      this.$emit('clean')
    },
    checkInputType (inputType) {
      let inputs = []
      if (this.selectedConfiguration) {
        inputs = this.selectedConfiguration.inputs
      } else if (this.selectedProcess) {
        for (let s = 0; s < this.selectedProcess.steps.length; s++) {
          inputs = inputs.concat(this.selectedProcess.steps[s].configuration.inputs)
        }
      }
      let check = false
      for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type === inputType) {
          check = true
          break
        }
      }
      return check
    },
    selectProject (projectId, project = null) {
      this.projectId = projectId
      if (project) {
        this.selectedProject = project
      } else {
        this.selectedProject = findById(this.projects, projectId)
      }
      this.targets = this.selectedProject.targets
    },
    selectProcess (processId, process = null) {
      const isWordlist = this.checkInputType('Wordlist')
      this.processId = processId
      this.toolId = null
      this.selectedTool = null
      this.configurationId = null
      this.selectedConfiguration = null
      this.intensities = intensitiesByVariant
      this.intensity = 'Normal'
      if (process) {
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
      this.selectedProcess = null
      this.toolId = toolId
      if (tool) {
        this.selectedTool = tool
      } else {
        this.selectedTool = findById(this.tools, toolId)
      }
      this.selectConfiguration(this.selectedTool.configurations[0].id, this.selectedTool.configurations[0])
      this.intensity = null
      this.intensities = []
      for (let i = 0; i < this.selectedTool.intensities.length; i++) {
        for (let j = 0; j < intensitiesByVariant.length; j++) {
          if (this.selectedTool.intensities[i].intensity_rank === intensitiesByVariant[j].intensity_rank) {
            this.intensities.push(intensitiesByVariant[j])
            break
          }
        }
        if (this.selectedTool.intensities[i].intensity_rank === 'Normal') {
          this.intensity = 'Normal'
        }
      }
      if (!this.intensity) {
        this.intensity = this.intensities[this.intensities.length - 1].intensity_rank
      }
    },
    selectConfiguration (configurationId, configuration = null) {
      const isWordlist = this.checkInputType('Wordlist')
      this.configurationId = configurationId
      if (configuration) {
        this.selectedConfiguration = configuration
      } else {
        this.selectedConfiguration = findById(this.selectedTool.configurations, configurationId)
      }
      if (!isWordlist && this.checkInputType('Wordlist')) {
        this.updateWordlists()
      }
    },
    updateWordlists () {
      WordlistApi.getAllWordlists().then(data => { this.wordlists = data.results })
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

<style lang="scss" scoped>
$component-active-bg: black;
$custom-range-thumb-bg: green;
@import 'bootstrap/scss/bootstrap';
</style>

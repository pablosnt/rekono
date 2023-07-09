<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" :title="title" ok-title="Execute" header-bg-variant="success" header-text-variant="light" ok-variant="success" size="lg">
    <template #modal-title v-if="selectedTool">
      <b-link :href="selectedTool.reference" target="_blank">
        <b-img v-if="selectedTool.icon" :src="selectedTool.icon" width="32"/>
        <b-img v-if="!selectedTool.icon" src="favicon.ico" width="32"/>
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
          <b-form-group description="Targets" invalid-feedback="Targets are required" v-if="!target">
            <b-form-select multiple :select-size="3" v-model="targetIds" :options="targets" :disabled="!selectedProject" value-field="id" text-field="target" :state="targetState"/>
            <b-form-checkbox switch @change="selectAllTargets" size="md">Select all</b-form-checkbox>
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
                <div v-for="i in intensitySelection" :key="i.value">
                  <b-button v-if="i.intensity_rank === intensity" v-b-tooltip.hover.top="i.intensity_rank" :variant="i.variant" no-remove>{{ intensity ? intensity.charAt(0) : 'H' }}</b-button>
                </div>
              </b-input-group-prepend>
              <b-form-select v-model="intensity" :options="intensitySelection" value-field="intensity_rank" text-field="intensity_rank" required/>
            </b-input-group>
          </b-form-group>
        </b-tab>
        <b-tab title-link-class="text-secondary" v-if="checkInputType('Wordlist')">
          <template #title>
            <b-icon icon="file-earmark-word-fill"/> Wordlists
          </template>
          <b-form-group description="Select wordlists to use">
            <b-form-select v-model="wordlistsItems" multiple :select-size="10">
              <option v-for="wordlist in wordlists" :key="wordlist.id" :value="wordlist.id">{{ wordlist.name }} - {{ wordlist.type }}</option>
            </b-form-select>
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
    <b-progress v-if="processed > 0 && targetIds.length > 1" :value="processed" :max="targetIds.length" variant="success" show-value/>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'taskModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    process: Object,
    tool: Object,
    project: Object,
    target: Object,
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
      if (this.process) {
        return `Execute ${this.process.name}`
      } else if (this.tool) {
        return `Execute ${this.tool.name}`
      }
      return 'New Task'
    },
    intensitySelection () {
      if (this.selectedTool) {
        return this.intensityByVariant.filter(intensity => this.selectedTool.intensities.find(i => i.intensity_rank === intensity.intensity_rank))
      }
      return this.intensityByVariant
    }
  },
  data () {
    return {
      isWordlist: false,
      projects: [],
      targets: [],
      processes: [],
      tools: [],
      wordlists: [],
      selectedProject: null,
      selectedProcess: null,
      selectedTool: null,
      selectedConfiguration: null,
      projectId: null,
      targetIds: [],
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
      minimumDate: new Date(),
      processed: 0
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized) {
        if (this.tool) {
          this.selectTool(this.tool.id, this.tool)
        } else if (this.process) {
          this.selectProcess(this.process.id, this.process)
        } else if (!this.tool && !this.process) {
          this.getAllPages('/api/tools/', { o: 'stage,name'}).then(results => this.tools = results)
          this.getAllPages('/api/processes/', { o: 'name' }).then(results => this.processes = results)
        }
        if (this.target) {
          this.targetIds = [this.target.id]
          this.get(`/api/projects/${this.target.project}/`).then(response => { this.selectProject(this.target.project, response.data) })
        } else if (this.project) {
          this.get(`/api/projects/${this.project.id}/`).then(response => { this.selectProject(this.project.id, response.data) })
        } else {
          this.getAllPages('/api/projects/', { o: 'name' }).then(results => this.projects = results)
        }
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.execute_form.checkValidity()
      this.projectState = (this.projectId && this.projectId > 0)
      this.targetState = this.targetIds.length > 0
      if (!this.processId && !this.toolId) {
        this.processState = false
        this.toolState = false
        return false
      }      
      if (this.scheduledAtDate || this.scheduledAtTime) {
        this.scheduledAtState = false
        if (this.scheduledAtDate && this.scheduledAtTime) {
          this.scheduledAtState = (Date.parse(`${this.scheduledAtDate} ${this.scheduledAtTime}`) > new Date())
        }
        return valid && this.scheduledAtState !== false
      }
      return valid && this.projectState && this.targetState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.create()
      }
    },
    create () {
      const data = {
        intensity_rank: this.intensity,
        scheduled_at: this.scheduledAtDate && this.scheduledAtTime ? new Date(`${this.scheduledAtDate}T${this.scheduledAtTime}`).toISOString() : null,
        scheduled_in: this.scheduledIn,
        scheduled_time_unit: this.scheduledTimeUnit,
        repeat_in: this.repeatIn,
        repeat_time_unit: this.repeatTimeUnit,
        wordlists: this.wordlistsItems
      }
      if (this.processId) {
        data.process_id = this.processId
      }
      if (this.toolId) {
        data.tool_id = this.toolId
      }
      if (this.configurationId) {
        data.configuration_id = this.configurationId
      }
      for (let index in this.targetIds) {
        data.target_id = this.targetIds[index]
        this.post('/api/tasks/', data, this.selectedTool ? this.selectedTool.name : this.selectedProcess.name, 'Execution requested successfully')
          .catch(task => { return Promise.resolve(task) })
          .then(task => {
            this.processed += 1
            if (this.processed === this.targetIds.length) {
              if (this.targetIds.length === 1) {
                this.$router.push({ name: 'task', params: { id: task.id, task: task }})
              }
              else if (this.$route.path === `/projects/${this.projectId}/tasks`) {
                this.$emit('confirm', { id: this.id, success: true, reload: true })
              }
              else {
                this.$router.push({ path: `/projects/${this.projectId}/tasks` })
              }
            }
          })
      } 
    },
    clean () {
      this.processes = []
      this.tools = []
      this.wordlists = []
      this.selectedProject = null
      this.selectedProcess = null
      this.selectedTool = null
      this.selectedConfiguration = null
      this.projectId = null
      this.targetIds = []
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
      this.processed = 0
      this.$emit('clean')
    },
    checkInputType (inputType) {
      let inputs = []
      if (this.selectedTool) {
        this.selectedTool.arguments.map(argument => argument.inputs.map(input => inputs.push(input.type.name)))
      } else if (this.selectedProcess) {
        this.selectedProcess.steps.map(step => step.tool.arguments.map(argument => argument.inputs.map(input => inputs.push(input.type.name))))
      }
      return inputs.includes(inputType)
    },
    selectProject (projectId, project = null) {
      this.projectId = projectId
      if (project) {
        this.selectedProject = project
      } else {
        this.selectedProject = this.projects.find(p => p.id === projectId)
      }
      this.targets = this.selectedProject.targets
    },
    selectProcess (processId, process = null) {
      this.processId = processId
      this.toolId = null
      this.selectedTool = null
      this.configurationId = null
      this.selectedConfiguration = null
      this.intensity = 'Normal'
      if (process) {
        this.selectedProcess = process
      } else {
        this.selectedProcess = this.processes.find(p => p.id === processId)
      }
      const isWordlist = this.checkInputType('Wordlist')
      if (!this.isWordlist && isWordlist) {
        this.isWordlist = isWordlist
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
        this.selectedTool = this.tools.find(t => t.id === toolId)
      }
      this.selectConfiguration(this.selectedTool.configurations[0].id, this.selectedTool.configurations[0])
      const normalIntensity = this.selectedTool.intensities.find(i => i.intensity_rank === 'Normal')
      if (normalIntensity) {
        this.intensity = 'Normal'
      } else {
        this.intensity = this.selectedTool.intensities[this.selectedTool.intensities.length - 1].intensity_rank
      }
      const isWordlist = this.checkInputType('Wordlist')
      if (!this.isWordlist && isWordlist) {
        this.isWordlist = isWordlist
        this.updateWordlists()
      }
    },
    selectConfiguration (configurationId, configuration = null) {
      this.configurationId = configurationId
      if (configuration) {
        this.selectedConfiguration = configuration
      } else {
        this.selectedConfiguration = this.selectedTool.configurations.find(c => c.id === configurationId)
      }
    },
    selectAllTargets (checked) {
      if (checked) {
        this.targetIds = this.targets.map(target => target.id)
      }
      else {
        this.targetIds = []
      }
    },
    updateWordlists () {
      this.getAllPages('/api/wordlists/', { o: 'type,name' }).then(results => this.wordlists = results)
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

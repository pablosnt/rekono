<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" :title="title" :ok-title="button" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <template #modal-title v-if="tool !== null">
      <b-link :href="tool.reference" target="_blank">
        <b-img :src="tool.icon" width="100" height="50"/>
      </b-link>
     {{ title }}
    </template>
    <b-form ref="step_form">
      <b-form-group description="Process" invalid-feedback="Process is required" v-if="process === null">
        <b-form-select v-model="processId" :options="processes" value-field="id" text-field="name" :state="processState" :disabled="processes.length == 0" @change="selectProcess" required>
          <template #first>
            <b-form-select-option :value="null" disabled>Select your process</b-form-select-option>
          </template>
        </b-form-select>
      </b-form-group>
      <b-form-group description="Tool" v-if="tool === null">
        <b-input-group>
          <b-input-group-prepend v-if="selectedTool !== null">
            <b-button variant="outline">
              <b-link :href="selectedTool.reference" target="_blank">
                <b-img :src="selectedTool.icon" width="50" height="30"/>
              </b-link>
            </b-button>
          </b-input-group-prepend>
          <b-form-select v-model="toolId" :options="tools" :disabled="edit && tool === null" @change="selectTool" value-field="id" text-field="name" :state="toolState" required>
            <template #first>
              <b-form-select-option :value="null" disabled>Select tool</b-form-select-option>
            </template>
          </b-form-select>
        </b-input-group>
      </b-form-group>
      <b-form-group description="Tool configuration" invalid-feedback="This step already exists in the process">
        <b-form-select v-model="configurationId" :options="selectedTool !== null ? selectedTool.configurations : []" :disabled="configurationId == null || edit" value-field="id" text-field="name" :state="configState" required/>
      </b-form-group>
      <b-form-group>
        <b-input-group :prepend="priority.toString()">
          <b-form-input v-model="priority" type="range" min="1" max="50" required/>
          <b-input-group-append v-b-tooltip.hover title="The priority allows to run steps with greater value before other tools of the same stage. By default the priority is 1, so all the steps will be treated in the same way">
            <b-button variant="outline">
              <b-icon icon="info-circle-fill" variant="info"/>
            </b-button>
          </b-input-group-append>
        </b-input-group>
        <small class="text-muted">Step priority</small>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import Processes from '@/backend/processes'
import ToolApi from '@/backend/tools'
import { findById } from '@/backend/utils'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
const ProcessApi = Processes.ProcessApi
const StepApi = Processes.StepApi
export default {
  name: 'stepForm',
  mixins: [AlertMixin],
  props: {
    id: String,
    initialized: {
      type: Boolean,
      default: false
    },
    process: {
      type: Object,
      default: null
    },
    step: {
      type: Object,
      default: null
    },
    tool: {
      type: Object,
      default: null
    }
  },
  computed: {
    edit () {
      return (this.step !== null)
    },
    title () {
      const start = this.edit ? 'Edit step from ' : 'New step for '
      if (this.process !== null) {
        return start + this.process.name
      } else if (this.tool !== null) {
        return `New step ${this.tool.name}`
      }
      return start
    },
    button () {
      return this.step !== null ? 'Update Step' : 'Create Step'
    }
  },
  data () {
    return {
      tools: [],
      processes: [],
      processId: null,
      toolId: null,
      configurationId: null,
      priority: 1,
      selectedTool: null,
      processState: null,
      toolState: null,
      configState: null
    }
  },
  watch: {
    process (process) {
      if (this.initialized && process !== null) {
        this.selectProcess(process.id, process)
      }
    },
    step (step) {
      if (this.initialized && step !== null) {
        step.tool.configurations = [step.configuration]
        this.selectTool(step.tool.id, step.tool)
        this.priority = step.priority
      }
    },
    tool (tool) {
      if (this.initialized && tool !== null) {
        this.selectTool(tool.id, tool)
      }
    },
    initialized (initialized) {
      if (initialized) {
        if (this.step === null && this.tool === null) {
          ToolApi.getAllTools().then(results => { this.tools = results })
        } else if (this.step !== null && this.tool == null) {
          this.tools = [this.selectedTool]
        }
        if (this.process === null) {
          let filter = null
          if (this.$store.state.role !== 'Admin') {
            filter = {
              creator: this.$store.state.user
            }
          }
          ProcessApi.getAllProcesses(filter).then(results => { this.processes = results })
        }
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.step_form.checkValidity()
      this.processState = (this.processId !== null)
      this.toolState = (this.toolId !== null)
      if (!this.edit && this.selectedProcess !== null) {
        for (let s = 0; s < this.selectedProcess.steps.length; s++) {
          if (this.selectedProcess.steps[s].tool.id === this.toolId && this.selectedProcess.steps[s].configuration.id === this.configurationId) {
            this.configState = false
            return false
          }
        }
      }
      return valid
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        const operation = this.edit ? this.update() : this.create()
        operation.then((success) => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    create () {
      return StepApi.createStep(this.processId, this.toolId, this.configurationId, this.priority)
        .then(() => {
          this.success(this.selectedTool.name, 'New step created successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.selectedTool.name, 'Unexpected error in step creation')
          return Promise.resolve(false)
        })
    },
    update () {
      return StepApi.updateStep(this.step.id, this.priority)
        .then(() => {
          this.success(this.selectedTool.name, 'Step updated successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.selectedTool.name, 'Unexpected error in step update')
          return Promise.resolve(false)
        })
    },
    clean () {
      this.tools = []
      this.processId = null
      this.toolId = null
      this.configurationId = null
      this.priority = 1
      this.selectedTool = null
      this.selectedProcess = null
      this.toolState = null
      this.configState = null
      this.$emit('clean')
    },
    selectProcess (processId, process = null) {
      this.processId = processId
      if (process !== null) {
        this.selectedProcess = null
      } else {
        this.selectedProcess = findById(this.processes, processId)
      }
    },
    selectTool (toolId, tool = null) {
      this.toolId = toolId
      if (tool !== null) {
        this.selectedTool = tool
      } else {
        this.selectedTool = findById(this.tools, toolId)
      }
      this.configurationId = this.selectedTool.configurations[0].id
    }
  }
}
</script>

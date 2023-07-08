<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" :title="title" :ok-title="button" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <template #modal-title v-if="tool">
      <b-link :href="tool.reference" target="_blank">
        <b-img v-if="tool.icon" :src="tool.icon" width="32"/>
        <b-img v-if="!tool.icon" src="favicon.ico" width="32"/>
      </b-link>
     {{ title }}
    </template>
    <b-form ref="step_form">
      <b-form-group description="Process" invalid-feedback="Process is required" v-if="!process">
        <b-form-select v-model="processId" :options="processes" value-field="id" text-field="name" :state="processState" :disabled="processes.length == 0" @change="selectProcess" required>
          <template #first>
            <b-form-select-option :value="null" disabled>Select your process</b-form-select-option>
          </template>
        </b-form-select>
      </b-form-group>
      <b-form-group description="Tool" v-if="!tool">
        <b-input-group>
          <b-input-group-prepend v-if="selectedTool">
            <b-button variant="outline">
              <b-link :href="selectedTool.reference" target="_blank">
                <b-img v-if="selectedTool.icon" :src="selectedTool.icon" width="32"/>
                <b-img v-if="!selectedTool.icon" src="favicon.ico" width="32"/>
              </b-link>
            </b-button>
          </b-input-group-prepend>
          <b-form-select v-model="toolId" :options="tools" :disabled="edit && !tool" @change="selectTool" value-field="id" text-field="name" :state="toolState" required>
            <template #first>
              <b-form-select-option :value="null" disabled>Select tool</b-form-select-option>
            </template>
          </b-form-select>
        </b-input-group>
      </b-form-group>
      <b-form-group description="Tool configuration" invalid-feedback="This step already exists in the process">
        <b-form-select v-model="configurationId" :options="selectedTool ? selectedTool.configurations : []" :disabled="!configurationId || edit" value-field="id" text-field="name" :state="configState" required/>
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
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'stepModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    process: Object,
    step: Object,
    tool: Object,
    initialized: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    edit () {
      return ![null, undefined].includes(this.step)
    },
    title () {
      if (this.process) {
        return this.edit ? `Edit step for ${this.process.name}` : `New step for ${this.process.name}`
      } else if (this.tool) {
        return `New step ${this.tool.name}`
      }
      return 'New step'
    },
    button () {
      return this.step ? 'Update Step' : 'Create Step'
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
    initialized (initialized) {
      if (initialized) {
        if (!this.step && !this.tool) {
          this.getAllPages('/api/tools/', { o: 'stage,name'}).then(results => this.tools = results)
        } else if (this.step && !this.tool) {
          this.priority = this.step.priority
          this.step.tool.configurations = [this.step.configuration]
          this.tools = [this.step.tool]
          this.selectTool(this.step.tool.id, this.step.tool)
        } else if (this.tool) {
          this.tools = [this.tool]
          this.selectTool(this.tool.id, this.tool)
        }
        if (!this.process) {
          let filter = { o: 'name' }
          if (this.$store.state.role !== 'Admin') {
            filter.creator = this.$store.state.user
          }
          this.getAllPages('/api/processes/', filter).then(results => this.processes = results)
        } else {
          this.selectProcess(this.process.id, this.process)
        }
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.step_form.checkValidity()
      this.processState = (this.processId !== null)
      this.toolState = (this.toolId !== null)
      if (this.toolState && !this.edit && this.selectedProcess !== null) {
        const existing_step = this.selectedProcess.steps.find(step => step.tool.id === this.toolId && step.configuration.id === this.configurationId)
        if (existing_step) {
          this.toolState = false
          this.configState = false
          return false
        }
      }
      return valid
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        const operation = this.edit ? this.update() : this.create()
        operation.then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    create () {
      return this.post(
        '/api/steps/',
        { process: this.processId, tool_id: this.toolId, configuration_id: this.configurationId, priority: this.priority },
        this.selectedTool.name, 'New step created successfully'
      )
        .then(() => { return Promise.resolve(true) })
        .catch(() => { return Promise.resolve(false) })
    },
    update () {
      return this.put(`/api/steps/${this.step.id}/`, { priority: this.priority }, this.selectedTool.name, 'Step updated successfully')
        .then(() => { return Promise.resolve(true) })
        .catch(() => { return Promise.resolve(false) })
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
        this.selectedProcess = process
      } else {
        this.selectedProcess = this.processes.find(p => p.id === processId)
      }
    },
    selectTool (toolId, tool = null) {
      this.toolId = toolId
      if (tool !== null) {
        this.selectedTool = tool
      } else {
        this.selectedTool = this.tools.find(t => t.id === toolId)
      }
      this.configurationId = this.selectedTool.configurations[0].id
    }
  }
}
</script>

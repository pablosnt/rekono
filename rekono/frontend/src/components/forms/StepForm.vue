<template>
  <b-modal :id="id" @hidden="cancel" @ok="confirm" :title="title" :ok-title="button">
    <template #modal-title v-if="tool !== null">
      <b-link :href="tool.reference" target="_blank">
        <b-img :src="tool.icon" width="100" height="50"/>
      </b-link>
     {{ title }}
    </template>
    <b-form ref="step_form">
      <b-form-group description="Process" invalid-feedback="Process is required" v-if="process === null">
        <b-form-select v-model="processId" :options="processes" value-field="id" text-field="name" :state="processState" :disabled="processes.length == 0" required>
          <template #first>
            <b-form-select-option :value="null" disabled>Select your process</b-form-select-option>
          </template>
        </b-form-select>
      </b-form-group>
      <b-form-group description="Tool" v-if="tool === null">
        <b-input-group>
          <b-input-group-prepend is-text v-if="selectedTool !== null">
            <b-link :href="selectedTool.reference" target="_blank">
              <b-img :src="selectedTool.icon" width="40" height="20"/>
            </b-link>
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
          <b-input-group-append is-text v-b-tooltip.hover title="The priority allows to run steps with greater value before other tools of the same stage. By default the priority is 1, so all the steps will be treated in the same way">
            <b-icon icon="info-circle-fill" variant="info"/>
          </b-input-group-append>
        </b-input-group>
        <small class="text-muted">Step priority</small>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import { getAllProcesses, getCurrentUserProcesses, createStep, updateStep } from '../../backend/processes'
import { getTools } from '../../backend/tools'
export default {
  name: 'stepForm',
  props: {
    id: String,
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
      var start = this.edit ? 'Edit step from ' : 'New step for '
      if (this.process !== null) {
        return start + this.process.name
      } else if (this.tool !== null) {
        return 'New step ' + this.tool.name
      }
      return start
    },
    button () {
      return this.step !== null ? 'Update Step' : 'Create Step'
    },
    tools () {
      if (this.tool === null) {
        return this.getTools()
      }
      return []
    },
    processes () {
      if (this.process === null) {
        return this.getProcesses()
      }
      return []
    }
  },
  data () {
    return {
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
      if (process) {
        this.processId = process.id
      }
    },
    step (step) {
      if (step !== null) {
        this.selectedTool = step.tool
        this.selectTool(step.tool.id)
        this.configurationId = step.configuration.id
        this.priority = step.priority
      }
    },
    tool (tool) {
      if (tool !== null) {
        this.selectedTool = tool
        this.selectTool(tool.id)
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.step_form.checkValidity()
      this.processState = (this.processId !== null)
      this.toolState = (this.toolId !== null)
      if (!this.edit && this.process !== null) {
        for (var s = 0; s < this.process.steps.length; s++) {
          if (this.process.steps[s].tool.id === this.toolId && this.process.steps[s].configuration.id === this.configurationId) {
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
        var operation = this.edit ? this.update() : this.create()
        operation.then((success) => this.$emit('confirm', { id: this.id, success: success }))
      }
    },
    create () {
      return createStep(this.processId, this.toolId, this.configurationId, this.priority)
        .then(() => {
          this.$bvToast.toast('New step created successfully', {
            title: this.selectedTool.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in step creation', {
            title: this.selectedTool.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    update () {
      return updateStep(this.step.id, this.priority)
        .then(() => {
          this.$bvToast.toast('Step updated successfully', {
            title: this.selectedTool.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in step update', {
            title: this.selectedTool.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    cancel () {
      this.processId = null
      this.toolId = null
      this.configurationId = null
      this.priority = 1
      this.selectedTool = null
      this.toolState = null
      this.configState = null
      this.$emit('cancel')
    },
    selectTool (toolId) {
      this.toolId = toolId
      for (var t = 0; t < this.tools.length; t++) {
        if (this.tools[t].id === toolId) {
          this.selectedTool = this.tools[t]
          break
        }
      }
      this.configurationId = this.selectedTool.configurations[0].id
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
      var method = null
      if (this.$store.state.role !== 'Admin') {
        method = getCurrentUserProcesses
      } else {
        method = getAllProcesses
      }
      method(this.$store.state.user)
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

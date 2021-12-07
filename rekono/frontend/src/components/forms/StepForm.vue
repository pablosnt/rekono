<template>
  <b-modal :id="id" @hidden="cancel" @ok="confirm" :title="title" :ok-title="edit ? 'Update Step' : 'Create Step'">
    <b-form ref="step_form">
      <b-form-group description="Tool">
        <b-input-group>
          <b-input-group-prepend is-text v-if="tool != null">
            <b-link :href="tool.reference" target="_blank">
              <b-img :src="tool.icon" width="40" height="20"/>
            </b-link>
          </b-input-group-prepend>
          <b-form-select v-model="toolId" :options="tools" :disabled="edit" @change="selectTool" value-field="id" text-field="name" :state="toolState" required>
            <template #first>
              <b-form-select-option :value="null" disabled>Select tool</b-form-select-option>
            </template>
          </b-form-select>
        </b-input-group>
      </b-form-group>
      <b-form-group description="Tool configuration" invalid-feedback="This step already exists in the process">
        <b-form-select v-model="configurationId" :options="tool !== null ? tool.configurations : []" :disabled="configurationId == null || edit" value-field="id" text-field="name" :state="configState" required/>
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
import { createStep, updateStep } from '../../backend/processes'
import { getTools } from '../../backend/tools'
export default {
  name: 'stepForm',
  props: ['id', 'process', 'step'],
  computed: {
    edit () {
      return (this.step !== null)
    },
    title () {
      var start = this.edit ? 'Edit step from ' : 'New step for '
      if (this.process !== null) {
        return start + this.process.name
      }
      return start
    }
  },
  data () {
    return {
      tools: this.getTools(),
      tool: null,
      toolId: null,
      configurationId: null,
      priority: 1,
      toolState: null,
      configState: null
    }
  },
  watch: {
    step (step) {
      if (step !== null) {
        this.tool = step.tool
        this.selectTool(step.tool.id)
        this.configurationId = step.configuration.id
        this.priority = step.priority
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.step_form.checkValidity()
      this.toolState = (this.toolId !== null)
      this.configState = (this.configurationId !== null)
      if (!this.edit) {
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
      if (!this.check()) {
        return
      }
      var operation = this.edit ? this.update() : this.create()
      operation.then((success) => this.$emit('confirm', { id: this.id, success: success }))
    },
    create () {
      return createStep(this.process.id, this.toolId, this.configurationId, this.priority)
        .then(() => {
          this.$bvToast.toast('New step created successfully', {
            title: this.tool.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in step creation', {
            title: this.tool.name,
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
            title: this.tool.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in step update', {
            title: this.tool.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    cancel () {
      this.tool = null
      this.toolId = null
      this.configurationId = null
      this.priority = 1
      this.toolState = null
      this.configState = null
      this.$emit('cancel')
    },
    selectTool (toolId) {
      for (var t = 0; t < this.tools.length; t++) {
        if (this.tools[t].id === toolId) {
          this.tool = this.tools[t]
          break
        }
      }
      this.configurationId = this.tool.configurations[0].id
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
    }
  }
}
</script>

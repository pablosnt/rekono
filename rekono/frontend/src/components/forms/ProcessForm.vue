<template>
  <b-modal :id="id" @hidden="cancel" @ok="confirm" :title="title" :ok-title="button">
    <template #modal-title v-if="tool !== null">
      <b-link :href="tool.reference" target="_blank">
        <b-img :src="tool.icon" width="100" height="50"/>
      </b-link>
      {{ title }}
    </template>
    <b-form ref="process_form">
      <b-form-group description="Process name" invalid-feedback="Process name is required">
        <b-form-input v-model="name" type="text" :state="nameState" maxlength="30" required/>
      </b-form-group>
      <b-form-group invalid-feedback="Process description is required">
        <b-form-textarea v-model="description" placeholder="Process description" :state="descriptionState" maxlength="350" required/>
      </b-form-group>
    </b-form>
    <b-form ref="step_form" v-if="tool !== null">
      <b-form-group description="Tool configuration">
        <b-form-select v-model="configuration" :options="tool.configurations" value-field="id" text-field="name" required/>
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
import { createProcess, updateProcess, createStep } from '../../backend/processes'
export default {
  name: 'processForm',
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
    edit () {
      return (this.process !== null)
    },
    title () {
      var title = this.process !== null ? 'Edit Process' : 'New Process'
      if (this.tool !== null) {
        title = title + ' with ' + this.tool.name
      }
      return title
    },
    button () {
      return this.process !== null ? 'Update Process' : 'Create Process'
    }
  },
  data () {
    return {
      name: null,
      description: null,
      configuration: null,
      priority: 1,
      nameState: null,
      descriptionState: null
    }
  },
  watch: {
    process (process) {
      if (process !== null) {
        this.name = process.name
        this.description = process.description
      }
    },
    tool (tool) {
      if (tool !== null) {
        this.configuration = tool.configurations[0].id
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.process_form.checkValidity()
      this.nameState = (this.description !== null && this.description.length > 0)
      this.descriptionState = (this.name !== null && this.name.length > 0)
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
      return createProcess(this.name, this.description)
        .then((data) => {
          if (this.tool === null) {
            this.$bvToast.toast('New process created successfully', {
              title: this.name,
              variant: 'success',
              solid: true
            })
            return Promise.resolve(true)
          } else {
            return createStep(data.id, this.tool.id, this.configuration, this.priority)
              .then(() => {
                this.$bvToast.toast('New process created successfully', {
                  title: this.name + ' - ' + this.tool.name,
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
              })
          }
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in process creation', {
            title: this.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    update () {
      return updateProcess(this.process.id, this.name, this.description)
        .then(() => {
          this.$bvToast.toast('Process updated successfully', {
            title: this.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in process update', {
            title: this.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    cancel () {
      this.name = null
      this.description = null
      this.configuration = null
      this.priority = 1
      this.nameState = null
      this.descriptionState = null
      this.$emit('cancel')
    }
  }
}
</script>

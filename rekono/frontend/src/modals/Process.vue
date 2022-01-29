<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" :title="title" :ok-title="button" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <template #modal-title v-if="tool">
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
    <b-form ref="step_form" v-if="tool">
      <b-form-group description="Tool configuration">
        <b-form-select v-model="configuration" :options="tool.configurations" value-field="id" text-field="name"/>
      </b-form-group>
      <b-form-group>
        <b-input-group :prepend="priority.toString()">
          <b-form-input v-model="priority" type="range" min="1" max="50" required variant="dark"/>
          <b-input-group-append v-b-tooltip.hover title="The priority allows to run steps with greater value before other tools of the same stage. By default the priority is 1, so all the steps will be treated in the same way">
            <b-button variant="outline">
              <b-icon icon="info-circle-fill" variant="info"/>
            </b-button>
          </b-input-group-append>
        </b-input-group>
        <small class="text-muted">Step priority</small>
      </b-form-group>
    </b-form>
    <b-form-group description="Tags">
        <b-form-tags no-outer-focus v-model="tags" placeholder="" remove-on-delete size="md" tag-variant="dark"/>
      </b-form-group>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'processModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    process: Object,
    tool: Object,
    initialized: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    edit () {
      return (this.process !== null)
    },
    title () {
      let title = this.process ? 'Edit Process' : 'New Process'
      if (this.tool) {
        title = `${title} with ${this.tool.name}`
      }
      return title
    },
    button () {
      return this.process ? 'Update Process' : 'Create Process'
    }
  },
  data () {
    return {
      name: null,
      description: null,
      configuration: null,
      priority: 1,
      tags: [],
      nameState: null,
      descriptionState: null
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized) {
        if (this.process) {
          this.name = this.process.name
          this.description = this.process.description
          this.tags = this.process.tags
        } else if (this.tool) {
          this.configuration = this.tool.configurations[0].id
        }
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.process_form.checkValidity()
      this.nameState = (this.name !== null && this.name.length > 0)
      this.descriptionState = (this.description !== null && this.description.length > 0)
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
      return  this.post('/api/processes/', { name: this.name, description: this.description, tags: this.tags }, this.name)
        .then(response => {
          if (this.tool === null) {
            this.success(this.name, 'New process created successfully')
            return Promise.resolve(true)
          } else {
            return this.post(
              '/api/steps/',
              { process: response.data.id, tool_id: this.tool.id, configuration_id: this.configuration, priority: this.priority },
              `${this.name} - ${this.tool.name}`,
              'New process created successfully'
            )
              .then(() => { return Promise.resolve(true) })
              .catch((error) => { console.log(error); return Promise.resolve(false) })
          }
        })
        .catch(() => { return Promise.resolve(false) })
    },
    update () {
      return this.put(
        `/api/processes/${this.process.id}/`,
        { name: this.name, description: this.description, tags: this.tags },
        this.name, 'Process updated successfully'
      )
        .then(() => { return Promise.resolve(true) })
        .catch(() => { return Promise.resolve(false) })
    },
    clean () {
      this.name = null
      this.description = null
      this.configuration = null
      this.priority = 1
      this.tags = []
      this.nameState = null
      this.descriptionState = null
      this.$emit('clean')
    }
  }
}
</script>

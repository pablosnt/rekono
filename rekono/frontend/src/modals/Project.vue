<template>
  <b-modal :id="id" @close="clean" @hidden="clean" @ok="confirm" :title="title" :ok-title="button" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="project_form">
      <b-form-group description="Project name" :invalid-feedback="invalidName">
        <b-form-input v-model="name" type="text" plaholder="Name" :state="nameState" maxlength="100" required/>
      </b-form-group>
      <b-form-group description="Project description" :invalid-feedback="invalidDescription">
        <b-form-textarea v-model="description" placeholder="Description" :state="descriptionState" maxlength="300" required/>
      </b-form-group>
      <b-form-group description="Defect-Dojo product Id">
        <b-input-group>
          <b-input-group-prepend>
            <b-button variant="outline" size="sm" v-b-tooltip.hover title="The Defect-Dojo product Id will be used to import the Rekono findings in Defect-Dojo">
              <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
            </b-button>
          </b-input-group-prepend>
          <b-form-input v-model="defectDojoId" type="number"/>
        </b-input-group>
      </b-form-group>
      <b-form-group description="Tags">
        <b-form-tags no-outer-focus v-model="tags" placeholder="" remove-on-delete size="md" tag-variant="dark"/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'projectModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    project: Object,
    initialized: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    edit () {
      return (this.project !== null)
    },
    title () {
      return this.project !== null ? 'Edit Project' : 'New Project'
    },
    button () {
      return this.project !== null ? 'Update Project' : 'Create Project'
    }
  },
  data () {
    return {
      name: null,
      description: null,
      defectDojoId: null,
      tags: [],
      nameState: null,
      descriptionState: null,
      invalidName: 'Project name is required',
      invalidDescription: 'Project description is required'
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized && this.project) {
        this.name = this.project.name
        this.description = this.project.description
        this.defectDojoId = this.project.defectdojo_product_id
        this.tags = this.project.tags
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.project_form.checkValidity()
      if (!this.name || this.name.length === 0 || !this.validateName(this.name)) {
        this.nameState = false
        this.invalidName = this.name && this.name.length > 0 ? 'Invalid project name' : 'Project name is required'
      }
      if (!this.description || this.description.length === 0 || !this.validateText(this.description)) {
        this.descriptionState = false
        this.invalidDescription = this.description && this.description.length > 0 ? 'Invalid project description' : 'Project description is required'
      }
      return valid && this.nameState !== false && this.descriptionState !== false
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
        '/api/projects/',
        { name: this.name, description: this.description, defectdojo_product_id: this.defectDojoId, tags: this.tags },
        this.name , 'New project created successfully'
      )
        .then(() => { return Promise.resolve(true) })
        .catch(() => { return Promise.resolve(false) })
    },
    update () {
      return this.put(
        `/api/projects/${this.project.id}/`,
        { name: this.name, description: this.description, defectdojo_product_id: this.defectDojoId, tags: this.tags },
        this.name , 'Project updated successfully'
      )
        .then(() => { return Promise.resolve(true) })
        .catch(() => { return Promise.resolve(false) })
    },
    clean () {
      this.name = null
      this.description = null
      this.defectDojoId = null
      this.tags = []
      this.nameState = null
      this.descriptionState = null
      this.$emit('clean')
    }
  }
}
</script>


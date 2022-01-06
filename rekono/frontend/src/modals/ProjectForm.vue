<template>
  <b-modal :id="id" @close="clean" @hidden="clean" @ok="confirm" :title="title" :ok-title="button" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="project_form">
      <b-form-group description="Project name" invalid-feedback="Project name is required">
        <b-form-input v-model="name" type="text" plaholder="Name" :state="nameState" maxlength="50" required/>
      </b-form-group>
      <b-form-group description="Project description" invalid-feedback="Project description is required">
        <b-form-textarea v-model="description" placeholder="Description" :state="descriptionState" maxlength="250" required/>
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
    </b-form>
  </b-modal>
</template>

<script>
import ProjectApi from '@/backend/projects'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'projectForm',
  mixins: [AlertMixin],
  props: {
    id: String,
    project: {
      type: Object,
      default: null
    },
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
      nameState: null,
      descriptionState: null
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized && this.project) {
        this.name = this.project.name
        this.description = this.project.description
        this.defectDojoId = this.project.defectdojo_product_id
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.project_form.checkValidity()
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
      return ProjectApi.createProject(this.name, this.description, this.defectDojoId)
        .then(() => {
          this.success(this.name , 'New project created successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.name, 'Unexpected error in project creation')
          return Promise.resolve(false)
        })
    },
    update () {
      return ProjectApi.updateProject(this.project.id, this.name, this.description, this.defectDojoId)
        .then(() => {
          this.success(this.name , 'Project updated successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.name, 'Unexpected error in project update')
          return Promise.resolve(false)
        })
    },
    clean () {
      this.name = null
      this.description = null
      this.defectDojoId = null
      this.nameState = null
      this.descriptionState = null
      this.$emit('clean')
    }
  }
}
</script>


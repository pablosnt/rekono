<template>
  <div>
    <b-row align-v="center">
      <b-col>
        <b-card>
          <b-card-text v-if="currentProject" class="text-left">{{ currentProject.description }}</b-card-text>
        </b-card>
      </b-col>
      <b-col cols="1" v-if="defectDojoUrl">
        <b-link :href="defectDojoUrl" target="_blank">
          <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
        </b-link>
      </b-col>
      <b-col cols="1">
        <b-dropdown variant="outline" right>
          <template #button-content>
            <b-icon variant="dark" icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item variant="dark" v-b-modal.project-modal @click="showEditForm = true">
            <b-icon icon="pencil-square"/>
            <label class="ml-1">Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="info" v-b-modal.defect-dojo-modal>
            <b-img src="/static/defect-dojo-favicon.ico" width="20" height="20"/>
            <label class="ml-1">Import in Defect-Dojo</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" v-b-modal.delete-project-modal>
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </b-col>
    </b-row>
    <Dashboard class="mt-3" :project="currentProject"/>
    <Deletion id="delete-project-modal"
      title="Delete Project"
      @deletion="deleteProject"
      v-if="currentProject">
      <span><strong>{{ currentProject.name }}</strong> project</span>
    </Deletion>
    <ProjectForm id="project-modal" :project="currentProject" :initialized="showEditForm" @confirm="confirm" @clean="showEditForm = false"/>
    <DefectDojoForm id="defect-dojo-modal" path="projects" :itemId="currentProject.id" :alreadyReported="false" @clean="$bvModal.hide('defect-dojo-modal')" @confirm="$bvModal.hide('defect-dojo-modal')"/>
  </div>
</template>

<script>
import ProjectsApi from '@/backend/projects'
import Dashboard from '@/components/dashboard/Dashboard.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import Deletion from '@/common/Deletion.vue'
import ProjectForm from '@/modals/ProjectForm.vue'
import DefectDojoForm from '@/modals/DefectDojoForm.vue'
export default {
  name: 'projectDetails',
  mixins: [AlertMixin],
  props: {
    project: Object
  },
  data () {
    return {
      defectDojoUrl: this.project && this.project.defectdojo_product_id ? `${process.env.VUE_APP_DEFECTDOJO_HOST}/product/${this.project.defectdojo_product_id}` : null,
      currentProject: this.project ? this.project : this.fetchProject(),
      showEditForm: false
    }
  },
  components: {
    Dashboard,
    Deletion,
    ProjectForm,
    DefectDojoForm
  },
  methods: {
    fetchProject () {
      ProjectsApi.getProject(this.$route.params.id)
        .then(data => {
          this.currentProject = data
          if (data.defectdojo_product_id) {
            this.defectDojoUrl = `${process.env.VUE_APP_DEFECTDOJO_HOST}/product/${data.defectdojo_product_id}`
          } else {
            this.defectDojoUrl = null
          }
        })
    },
    deleteProject () {
      ProjectsApi.deleteProject(this.currentProject.id)
        .then(() => {
          this.$bvModal.hide('delete-project-modal')
          this.warning(this.currentProject.name, 'Project deleted successfully')
          this.$router.push({ path: '/projects' })
        })
        .catch(() => {
          this.danger(this.currentProject.name, 'Unexpected error in project deletion')
        })
    },
    confirm (operation) {
      if (operation.success) {
        this.$bvModal.hide(operation.id)
        this.fetchProject()
      }
    }
  }
}
</script>

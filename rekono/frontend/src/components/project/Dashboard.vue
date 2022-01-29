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
    <dashboard class="mt-3" :project="currentProject"/>
    <deletion id="delete-project-modal" title="Delete Project" @deletion="deleteProject" v-if="currentProject">
      <span><strong>{{ currentProject.name }}</strong> project</span>
    </deletion>
    <project id="project-modal" :project="currentProject" :initialized="showEditForm" @confirm="confirm" @clean="showEditForm = false"/>
    <defect-dojo id="defect-dojo-modal" path="projects" :itemId="$route.params.id" :alreadyReported="false" @clean="$bvModal.hide('defect-dojo-modal')" @confirm="$bvModal.hide('defect-dojo-modal')"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Dashboard from '@/components/dashboard/Dashboard'
import Deletion from '@/common/Deletion'
import Project from '@/modals/Project'
import DefectDojo from '@/modals/DefectDojo'
export default {
  name: 'projectDashboardPage',
  mixins: [RekonoApi],
  props: {
    project: Object
  },
  data () {
    this.fetchProject()
    return {
      defectDojoUrl: this.project && this.project.defectdojo_product_id ? `${process.env.VUE_APP_DEFECTDOJO_HOST}/product/${this.project.defectdojo_product_id}` : null,
      currentProject: this.project ? this.project : null,
      showEditForm: false
    }
  },
  components: {
    Dashboard,
    Deletion,
    Project,
    DefectDojo
  },
  methods: {
    fetchProject () {
      if (!this.project) {
        this.get(`/api/projects/${this.$route.params.id}/`)
          .then(response => {
            this.currentProject = response.data
            this.defectDojoUrl = response.data.defectdojo_product_id ? `${process.env.VUE_APP_DEFECTDOJO_HOST}/product/${response.data.defectdojo_product_id}` : null
          })
      }
    },
    deleteProject () {
      this.delete(`/api/projects/${this.$route.params.id}/`, this.currentProject.name, 'Project deleted successfully').then(() => this.$router.push({ path: '/projects' }))
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

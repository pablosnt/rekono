<template>
  <div>
    <b-row align-v="center">
      <b-col>
        <b-card>
          <b-card-text class="text-left">{{ project.description }}</b-card-text>
        </b-card>
      </b-col>
      <b-col cols="1" v-if="getDefectDojoUrl()">
        <b-link :href="getDefectDojoUrl()" target="_blank">
          <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
        </b-link>
      </b-col>
      <b-col cols="1" v-if="$store.state.role === 'Admin'">
        <b-dropdown variant="outline" right>
          <template #button-content>
            <b-icon variant="dark" icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item variant="dark" v-b-modal.project-modal @click="showEditForm = true">
            <b-icon icon="pencil-square"/>
            <label class="ml-1">Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="info" v-b-modal.defect-dojo-modal @click="showDefectDojo = true" v-if="defectDojoEnabled">
            <b-img src="/static/defect-dojo-favicon.ico" width="20" height="20"/>
            <label class="ml-1">Defect-Dojo</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" v-b-modal.delete-project-modal>
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </b-col>
    </b-row>
    <dashboard class="mt-3" :project="project"/>
    <deletion id="delete-project-modal" title="Delete Project" @deletion="deleteProject">
      <span><strong>{{ project.name }}</strong> project</span>
    </deletion>
    <project id="project-modal" :project="project" :initialized="showEditForm" @confirm="confirm" @clean="showEditForm = false"/>
    <defect-dojo id="defect-dojo-modal" :project="project" :initialized="showDefectDojo" @confirm="confirm" @clean="showDefectDojo = false"/>
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
    return {
      showEditForm: false,
      showDefectDojo: false
    }
  },
  components: {
    Dashboard,
    Deletion,
    Project,
    DefectDojo
  },
  methods: {
    getDefectDojoUrl () {
      return this.project && this.project.defectdojo_product_id && this.defectDojoEnabled ? `${this.defectDojoUrl}/product/${this.project.defectdojo_product_id}` : null
    },
    deleteProject () {
      this.delete(`/api/projects/${this.$route.params.id}/`, this.project.name, 'Project deleted successfully').then(() => this.$router.push({ path: '/projects' }))
    },
    confirm (operation) {
      if (operation.success) {
        this.$bvModal.hide(operation.id)
        if (operation.reload) {
          this.fetchProject()
        }
      }
      this.showEditForm = false
      this.showDefectDojo = false
    }
  }
}
</script>

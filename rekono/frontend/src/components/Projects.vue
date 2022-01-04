<template>
  <div>
    <TableHeader :filters="filters" add="project-modal" :addAuth="$store.state.role === 'Admin'" @filter="fetchData"/>
    <b-table hover striped borderless head-variant="dark" :fields="projectsFields" :items="projects" @row-clicked="navigateToProjectDetails">
      <template #cell(defectdojo_product_id)="row">
        <b-link v-if="row.item.defectdojo_product_id !== null" :href="defectDojoUrl(row.item.defectdojo_product_id)" target="_blank">
          <b-img src="/static/brands/defect-dojo-favicon.ico" width="30" height="30"/>
        </b-link>
      </template>
      <template #cell(actions)="row" v-if="$store.state.role === 'Admin'">
        <b-dropdown variant="outline-primary" right>
          <template #button-content>
            <b-icon icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item variant="dark" @click="selectProject(row.item)" v-b-modal.project-modal>
            <b-icon icon="pencil-square"/>
            <label class="ml-1">Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" @click="selectProject(row.item)" v-b-modal.delete-project-modal>
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </template>
    </b-table>
    <Pagination :page="page" :limit="limit" :limits="limits" :total="total" name="projects" @pagination="pagination"/>
    <Deletion id="delete-project-modal"
      title="Delete Project"
      @deletion="deleteProject"
      @clean="cleanSelection"
      v-if="selectedProject !== null">
      <span><strong>{{ selectedProject.name }}</strong> project</span>
    </Deletion>
    <ProjectForm id="project-modal" :project="selectedProject" :initialized="selectedProject !== null" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import ProjectApi from '@/backend/projects'
import Deletion from '@/common/Deletion.vue'
import TableHeader from '@/common/TableHeader.vue'
import Pagination from '@/common/Pagination.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import ProjectForm from '@/modals/ProjectForm.vue'
export default {
  name: 'projectsPage',
  mixins: [AlertMixin, PaginationMixin],
  data () {
    return {
      projects: this.fetchData(),
      projectsFields: [
        { key: 'name', label: 'Project', sortable: true },
        { key: 'defectdojo_product_id', label: 'Defect-Dojo', sortable: false },
        { key: 'targets.length', label: 'Targets', sortable: true },
        { key: 'owner.username', label: 'Owner', sortable: true },
        { key: 'members.length', label: 'Members', sortable: true },
        { key: 'actions', sortable: false }
      ],
      selectedProject: null,
      filters: []
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    ProjectForm
  },
  watch: {
    projects () {
      this.filters = [
        { name: 'Owner', filterField: 'owner__username__icontains', type: 'text' }
      ]
    }
  },
  methods: {
    fetchData (filter = null) {
      ProjectApi.getPaginatedProjects(this.getPage(), this.getLimit(), filter).then(data => {
        this.total = data.count
        this.projects = data.results
      })
    },
    deleteProject () {
      ProjectApi.deleteProject(this.selectedProject.id)
        .then(() => {
          this.$bvModal.hide('delete-project-modal')
          this.warning(this.selectedProject.name, 'Project deleted successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(this.selectedProject.name, 'Unexpected error in project deletion')
        })
    },
    selectProject (project) {
      this.selectedProject = project
    },
    cleanSelection () {
      this.selectedProject = null
    },
    defectDojoUrl (productId) {
      return `${process.env.VUE_APP_DEFECTDOJO_HOST}/product/${productId}`
    },
    navigateToProjectDetails (record) {
      this.$router.push({ name: 'project', params: { id: record.id, project: record } })
    }
  }
}
</script>

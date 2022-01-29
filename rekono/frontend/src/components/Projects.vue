<template>
  <div>
    <table-header :filters="filters" add="project-modal" :addAuth="$store.state.role === 'Admin'" @filter="fetchData"/>
    <b-table hover striped borderless head-variant="dark" :fields="projectsFields" :items="data" @row-clicked="navigateToProjectDetails">
      <template #cell(tags)="row">
        <b-form-tags no-outer-focus :value="row.item.tags" placeholder="" remove-on-delete size="md" tag-variant="dark" @input="updateProject(row.item, $event)"/>
      </template>
      <template #cell(defectdojo_product_id)="row">
        <b-link v-if="row.item.defectdojo_product_id !== null" :href="defectDojoUrl(row.item.defectdojo_product_id)" target="_blank">
          <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
        </b-link>
      </template>
      <template #cell(actions)="row" v-if="$store.state.role === 'Admin'">
        <b-dropdown variant="outline" right>
          <template #button-content>
            <b-icon variant="dark" icon="three-dots-vertical"/>
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
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="projects" @pagination="pagination"/>
    <deletion id="delete-project-modal" title="Delete Project" @deletion="deleteProject" @clean="cleanSelection" v-if="selectedProject !== null">
      <span><strong>{{ selectedProject.name }}</strong> project</span>
    </deletion>
    <project id="project-modal" :project="selectedProject" :initialized="selectedProject !== null" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import TableHeader from '@/common/TableHeader'
import Pagination from '@/common/Pagination'
import Project from '@/modals/Project'
export default {
  name: 'projectsPage',
  mixins: [RekonoApi],
  data () {
    this.fetchData()
    return {
      data: [],
      projectsFields: [
        { key: 'name', label: 'Project', sortable: true },
        { key: 'defectdojo_product_id', label: 'Defect-Dojo', sortable: false },
        { key: 'tags', sortable: true },
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
    Project
  },
  watch: {
    projects () {
      this.filters = [
        { name: 'Tags', filterField: 'tags__name__in', type: 'tags' },
        { name: 'Owner', filterField: 'owner__username__icontains', type: 'text' },
      ]
    }
  },
  methods: {
    fetchData (params = null) {
      return this.getOnePage('/api/projects/?o=name', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    updateProject (project, tags) {
      this.put(`/api/projects/${project.id}/`, { name: project.name, description: project.description, defectdojo_product_id: project.defectdojo_product_id, tags: tags })
    },
    deleteProject () {
      this.delete(`/api/projects/${this.selectedProject.id}/`, this.selectedProject.name, 'Project deleted successfully').then(() => this.fetchData())
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

<template>
  <div>
    <table-header :filters="filters" add="task-modal" :addAuth="auditor.includes($store.state.role)" addIcon="play-circle-fill" @add-click="showTaskForm = true" @filter="fetchData"/>
    <b-table hover striped borderless head-variant="dark" :fields="tasksFields" :items="data" @row-clicked="navigateToTaskDetails">
      <template #cell(tool)="row">
        <div v-if="row.item.tool">
          <b-link :href="row.item.tool.reference" target="_blank">
            <b-img :src="row.item.tool.icon" width="30" height="30"/>
          </b-link>
          {{ row.item.tool.name }}
        </div>
      </template>
      <template #cell(intensity_rank)="row">
        <div v-for="i in intensityByVariant" :key="i.value">
          <b-badge v-if="i.intensity_rank === row.item.intensity_rank" :variant="i.variant">{{ row.item.intensity_rank }}</b-badge>
        </div>
      </template>
      <template #cell(status)="row">
        <div v-for="i in statusByVariant" :key="i.value">
          <b-badge v-if="i.value === row.item.status" :variant="i.variant">{{ row.item.status }}</b-badge>
        </div>
      </template>
      <template #cell(date)="row">
        {{ row.item.start !== null ? row.item.start.replace('T', ' ').substring(0, 19) : '' }}
      </template>
      <template #cell(actions)="row">
        <b-button variant="outline" @click="selectTask(row.item)" v-b-modal.cancel-task-modal v-b-tooltip.hover title="Cancel Task" v-if="auditor.includes($store.state.role) && row.item.status !== 'Cancelled' && (cancellableStatuses.includes(row.item.status) || (row.item.repeat_in && row.item.repeat_time_unit))">
          <b-icon variant="danger" icon="dash-circle-fill"/>
        </b-button>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="tasks" @pagination="pagination"/>
    <deletion id="cancel-task-modal" title="Cancel Task" removeWord="cancel" @deletion="cancelTask" @clean="cleanSelection" v-if="selectedTask !== null">
      <span>selected task</span>
    </deletion>
    <task id="task-modal" :project="currentProject" :reload="true" :initialized="showTaskForm" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import TableHeader from '@/common/TableHeader'
import Pagination from '@/common/Pagination'
import Task from '@/modals/Task'
export default {
  name: 'projectTaskPage',
  mixins: [RekonoApi],
  props: {
    project: Object
  },
  data () {
    this.fetchData()
    this.fetchProject()
    return {
      data: [],
      tasksFields: [
        { key: 'target.target', label: 'Target', sortable: true },
        { key: 'process.name', label: 'Process', sortable: true },
        { key: 'tool', sortable: true },
        { key: 'configuration.name', label: 'Configuration', sortable: true },
        { key: 'intensity_rank', label: 'Intensity', sortable: true },
        { key: 'status', sortable: true },
        { key: 'executor.username', label: 'Executor', sortable: true },
        { key: 'date', sortable: true },
        { key: 'actions', sortable: false }
      ],
      currentProject: this.project ? this.project : null,
      selectedTask: null,
      filters: [],
      showTaskForm: false
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    Task
  },
  watch: {
    tasks () {
      this.filters = [
         { name: 'Intensity', values: this.intensities, valueField: 'value', textField: 'text', filterField: 'intensity' },
         { name: 'Status', values: this.statusesByVariant, valueField: 'value', textField: 'value', filterField: 'status' },
         { name: 'Executor', filterField: 'executor__username__icontains', type: 'text' }
      ]
    }
  },
  methods: {
    fetchData (params = { }) {
      params.project = this.$route.params.id
      return this.getOnePage('/api/tasks/', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    fetchProject () {
      if (!this.project) {
        this.get(`/api/projects/${this.$route.params.id}/`).then(response => this.currentProject = response.data)
      }
    },
    cancelTask () {
      this.delete(`/api/tasks/${this.selectedTask.id}/`, this.selectedTask.process ? this.selectedTask.process.name : this.selectedTask.tool.name, 'Task cancelled successfully').then(this.fetchData())
    },
    selectTask (task) {
      this.selectedTask = task
    },
    cleanSelection () {
      this.selectedTask = null
      this.showTaskForm = false
    },
    navigateToTaskDetails (record) {
      this.$router.push({ name: 'task', params: { id: record.id, task: record }})
    }
  }
}
</script>

<template>
  <div>
    <TableHeader :filters="filters" add="execute-modal" :addAuth="auditor.includes($store.state.role)" addIcon="play-btn-fill" @add-click="showTaskForm = true" @filter="fetchData"/>
    <b-table hover striped borderless head-variant="dark" :fields="tasksFields" :items="tasks" @row-clicked="navigateToTaskDetails">
      <template #cell(tool_data)="row">
        <div v-if="row.item.tool_data">
          <b-link :href="row.item.tool_data.reference" target="_blank">
            <b-img :src="row.item.tool_data.icon" width="30" height="30"/>
          </b-link>
          {{ row.item.tool_data.name }}
        </div>
      </template>
      <template #cell(intensity_rank)="row">
        <div v-for="i in intensities" :key="i.value">
          <b-badge v-if="i.intensity_rank === row.item.intensity_rank" :variant="i.variant" no-remove>{{ row.item.intensity_rank }}</b-badge>
        </div>
      </template>
      <template #cell(status)="row">
        <div v-for="i in statuses" :key="i.value">
          <b-badge v-if="i.value === row.item.status" :variant="i.variant" no-remove>{{ i.value }}</b-badge>
        </div>
      </template>
      <template #cell(start)="row">
        {{ row.item.start !== null ? row.item.start.replace('T', ' ').substring(0, 19) : '' }}
      </template>
      <template #cell(actions)="row">
        <b-button variant="outline" @click="selectTask(row.item)" v-b-modal.cancel-task-modal v-b-tooltip.hover title="Cancel Task" v-if="auditor.includes($store.state.role) && (cancellable.includes(row.item.status) || (row.item.repeat_in && row.item.repeat_time_unit))">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
      </template>
    </b-table>
    <Pagination :page="page" :limit="limit" :limits="limits" :total="total" name="tasks" @pagination="pagination"/>
    <Deletion id="cancel-task-modal"
      title="Cancel Task"
      removeWord="cancel"
      @deletion="cancelTask"
      @clean="cleanSelection"
      v-if="selectedTask !== null">
      <span>selected task</span>
    </Deletion>
    <TaskForm id="execute-modal" :project="currentProject" :initialized="showTaskForm" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import TasksApi from '@/backend/tasks'
import ProjectsApi from '@/backend/projects'
import { auditor, intensitiesByVariant, intensitiesByValue, statusesByVariant, cancellableStatuses } from '@/backend/constants'
import Deletion from '@/common/Deletion.vue'
import TableHeader from '@/common/TableHeader.vue'
import Pagination from '@/common/Pagination.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import TaskForm from '@/modals/TaskForm.vue'
export default {
  name: 'projectTaskPage',
  mixins: [AlertMixin, PaginationMixin],
  props: {
    project: Object
  },
  data () {
    return {
      auditor: auditor,
      intensities: intensitiesByVariant,
      statuses: statusesByVariant,
      cancellable: cancellableStatuses,
      tasks: this.fetchData(),
      tasksFields: [
        { key: 'target_data.target', label: 'Target', sortable: true },
        { key: 'process_data.name', label: 'Process', sortable: true },
        { key: 'tool_data', sortable: true },
        { key: 'configuration_data.name', label: 'Configuration', sortable: true },
        { key: 'intensity_rank', label: 'Intensity', sortable: true },
        { key: 'status', sortable: true },
        { key: 'executor.username', label: 'Executor', sortable: true },
        { key: 'start', label: 'Date', sortable: true },
        { key: 'actions', sortable: false }
      ],
      currentProject: this.getProject(),
      selectedTask: null,
      filters: [],
      showTaskForm: false
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    TaskForm
  },
  watch: {
    tasks () {
      this.filters = [
         { name: 'Intensity', values: intensitiesByValue, valueField: 'value', textField: 'text', filterField: 'intensity' },
         { name: 'Status', values: statusesByVariant, valueField: 'value', textField: 'value', filterField: 'status' },
         { name: 'Executor', filterField: 'executor__username__icontains', type: 'text' }
      ]
    }
  },
  methods: {
    fetchData (filters = null) {
      if (!filters) {
        filters = {}
      }
      filters.project = this.$route.params.id
      TasksApi.getAllTasks(this.getPage(), this.getLimit(), filters)
        .then(data => {
          this.total = data.count
          this.tasks = data.results
        })
    },
    cancelTask () {
      const notification = this.selectedTask.process_data ? this.selectedTask.process_data.name : this.selectedTask.tool_data.name
      TasksApi.cancelTask(this.selectedTask.id)
        .then(() => {
          this.$bvModal.hide('cancel-task-modal')
          this.warning(notification, 'Task cancelled successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(notification, 'Unexpected error in task cancellation')
        })
    },
    selectTask (task) {
      this.selectedTask = task
    },
    cleanSelection () {
      this.selectedTask = null
      this.showTaskForm = false
    },
    getProject () {
      if (this.project) {
        this.currentProject = this.project
      } else {
        ProjectsApi.getProject(this.$route.params.id)
          .then(data => {
            this.currentProject = data
          })
      }
    },
    navigateToTaskDetails (record) {
      this.$router.push({ name: 'task', params: { id: record.id, task: record }})
    }
  }
}
</script>

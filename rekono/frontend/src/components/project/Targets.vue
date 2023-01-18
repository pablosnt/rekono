<template>
  <div>
    <table-header :filters="filters" add="add-target-modal" :showAdd="auditor.includes($store.state.role)" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="targetsFields" :items="data">
      <template #cell(defectdojo_engagement_id)="row">
        <b-link v-if="row.item.defectdojo_engagement_id !== null && defectDojoEnabled" :href="`${defectDojoUrl}/engagement/${row.item.defectdojo_engagement_id}`" target="_blank">
          <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
        </b-link>
      </template>
      <template #cell(actions)="row">
        <b-button variant="outline" class="mr-2" v-b-tooltip.hover title="Configuration" @click="selectedTarget = row.item" v-b-modal.target-details-modal>
          <b-icon variant="dark" icon="nut-fill"/>
        </b-button>
        <b-button variant="outline" class="mr-2" v-b-tooltip.hover title="Execute" @click="selectedTarget = row.item" v-b-modal.task-modal v-if="auditor.includes($store.state.role)">
          <b-icon variant="success" icon="play-circle-fill"/>
        </b-button>
        <b-button variant="outline" class="mr-2" v-b-tooltip.hover title="Delete" @click="selectedTarget = row.item" v-b-modal.delete-target-modal v-if="auditor.includes($store.state.role)">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="targets" @pagination="pagination"/>
    <deletion id="delete-target-modal" title="Delete Target" @deletion="deleteTarget" @clean="selectedTarget = null" v-if="selectedTarget !== null">
      <span><strong>{{ selectedTarget.target }}</strong> target</span>
    </deletion>
    <target id="add-target-modal" :projectId="$route.params.id" @confirm="confirm"/>
    <target-details v-if="selectedTarget !== null" id="target-details-modal" :target="selectedTarget" @close="fetchData(); selectedTarget = null"/>
    <task id="task-modal" :target="selectedTarget" :initialized="selectedTarget !== null" @clean="selectedTarget = null"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
import TableHeader from '@/common/TableHeader'
import Target from '@/modals/targets/Target'
import TargetDetails from '@/modals/targets/TargetDetails'
import Task from '@/modals/Task'
export default {
  name: 'projectTargetsPage',
  mixins: [RekonoApi],
  props: {
    project: Object
  },
  computed: {
    targetsFields () {
      let fields = [
        { key: 'target', sortable: true },
        { key: 'type', sortable: true },
        { key: 'target_ports.length', label: 'Target Ports', sortable: true },
        { key: 'tasks.length', label: 'Tasks', sortable: true },
        { key: 'actions', sortable: false }
      ]
      if (this.defectDojoEnabled) {
        fields.splice(2, 0, { key: 'defectdojo_engagement_id', label: 'Defect-Dojo', sortable: false })
      }
      return fields
    }
  },
  data () {
    this.fetchData()
    this.getSettings()
    return {
      data: [],
      selectedTarget: null,
      filters: []
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    Target,
    TargetDetails,
    Task
  },
  watch: {
    data () {
      this.filters = [
        { name: 'Type', values: this.targetTypes, valueField: 'value', textField: 'value', filterField: 'type' }
      ]
    }
  },
  methods: {
    fetchData (params = {}) {
      params.project = this.$route.params.id
      params.o = 'target'
      return this.getOnePage('/api/targets/', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    deleteTarget () {
      this.delete(`/api/targets/${this.selectedTarget.id}/`).then(() => this.fetchData())
    },
    selectTarget (target) {
      this.selectedTarget = target
    }
  }
}
</script>

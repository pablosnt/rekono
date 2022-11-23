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
        <b-button :disabled="row.item.target_ports.length === 0" @click="showTarget(row)" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.item._showDetails" variant="dark" icon="eye-fill"/>
          <b-icon v-if="row.item._showDetails" variant="secondary" icon="eye-slash-fill"/>
          <label style="display: none">{{ showTargetId }}</label>
        </b-button>
        <b-button variant="outline" class="mr-2" v-b-tooltip.hover title="Execute" @click="selectTarget(row.item)" v-b-modal.task-modal v-if="auditor.includes($store.state.role)">
          <b-icon variant="success" icon="play-circle-fill"/>
        </b-button>
        <b-dropdown variant="outline" right v-if="auditor.includes($store.state.role)">
          <template #button-content>
            <b-icon variant="dark" icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item @click="selectTarget(row.item)" v-b-modal.add-target-port-modal>
            <b-icon variant="success" icon="plus-square"/>
            <label class="ml-1" variant="dark">Add Port</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" @click="selectTarget(row.item)" v-b-modal.delete-target-modal>
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete Target</label>
          </b-dropdown-item>
        </b-dropdown>
      </template>
      <template #row-details="row">
        <b-card>
          <b-table striped borderles head-variant="light" :fields="targetPortsFields" :items="row.item.target_ports">
            <template #cell(actions)="port">
              <b-button @click="showTargetPort = port.item.id; selectTargetPort(row.item, port.item)" variant="outline" class="mr-2" v-b-tooltip.hover title="Details" v-b-modal.target-port-details>
                <b-icon v-if="showTargetPort !== port.item.id" variant="dark" icon="eye-fill"/>
                <b-icon v-if="showTargetPort === port.item.id" variant="dark" icon="eye-slash-fill"/>
              </b-button>
              <b-button variant="outline" @click="selectTargetPort(row.item, port.item)" v-b-tooltip.hover title="Delete Port" v-b-modal.delete-target-port-modal>
                <b-icon variant="danger" icon="trash-fill"/>
              </b-button>
            </template>
          </b-table>
        </b-card>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="targets" @pagination="pagination"/>
    <deletion id="delete-target-modal" title="Delete Target" @deletion="deleteTarget" @clean="cleanSelection" v-if="selectedTarget !== null">
      <span><strong>{{ selectedTarget.target }}</strong> target</span>
    </deletion>
    <deletion id="delete-target-port-modal" title="Delete Target Port" @deletion="deleteTargetPort" @clean="cleanSelection" v-if="selectedTargetPort !== null">
      <span><strong>{{ selectedTargetPort.port }}</strong> port</span>
    </deletion>
    <target id="add-target-modal" :projectId="$route.params.id" @confirm="confirm"/>
    <target-port v-if="selectedTarget !== null" id="add-target-port-modal" :targetId="selectedTarget.id" @confirm="confirm"/>
    <target-port-details v-if="selectedTargetPort !== null" id="target-port-details" :targetPort="selectedTargetPort" @close="showTargetPort = null; fetchData()"/>
    <task id="task-modal" :target="selectedTarget" :initialized="selectedTarget !== null" @clean="cleanSelection"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
import TableHeader from '@/common/TableHeader'
import Target from '@/modals/Target'
import TargetPort from '@/modals/TargetPort'
import TargetPortDetails from '@/modals/TargetPortDetails'
import Task from '@/modals/Task'
export default {
  name: 'projectTargetsPage',
  mixins: [RekonoApi],
  props: {
    project: Object
  },
  computed: {
    targetsFields () {
      var fields = [
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
      targetPortsFields: [
        { key: 'port', sortable: true },
        { key: 'target_technologies.length', label: 'Technologies', sortable: false},
        { key: 'target_vulnerabilities.length', label: 'Vulnerabilities', sortable: false},
        { key: 'actions', sortable: false },
      ],
      selectedTarget: null,
      selectedTargetPort: null,
      showTargetId: null,
      showTargetPort: null,
      filters: []
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    Target,
    TargetPort,
    TargetPortDetails,
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
    fetchData (params = { }) {
      params.project = this.$route.params.id
      return this.getOnePage('/api/targets/?o=target', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
          if (this.showTargetId) {
            this.data.filter(target => target.id === this.showTargetId).forEach(target => target._showDetails = true)
          }
        })
    },
    showTarget (row) {
      row.toggleDetails()
      this.showTargetId = row.item._showDetails ? row.item.id : null
    },
    deleteTarget () {
      this.delete(`/api/targets/${this.selectedTarget.id}/`).then(() => this.fetchData())
    },
    deleteTargetPort () {
      this.delete(`/api/target-ports/${this.selectedTargetPort.id}/`).then(() => this.fetchData())
    },
    selectTarget (target) {
      this.selectedTarget = target
    },
    selectTargetPort (target, targetPort) {
      this.selectTarget(target)
      this.selectedTargetPort = targetPort
    },
    cleanSelection () {
      this.selectedTarget = null
      this.selectedTargetPort = null
      this.showTargetPort = null
    }
  }
}
</script>

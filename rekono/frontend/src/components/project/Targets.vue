<template>
  <div>
    <table-header :filters="filters" add="add-target-modal" :addAuth="auditor.includes($store.state.role)" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="targetsFields" :items="data">
      <template #cell(actions)="row">
        <b-button :disabled="row.item.target_ports.length === 0" @click="row.toggleDetails" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" variant="dark" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" variant="secondary" icon="eye-slash-fill"/>
        </b-button>
        <b-button variant="outline" class="mr-2" v-b-tooltip.hover title="Execute" @click="selectTarget(row.item)" v-b-modal.task-modal>
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
            <template #cell(endpoints)="port">
              <b-table bordered small thead-class="d-none" :fields="targetEndpointsFields" :items="port.item.target_endpoints">
                <template #cell(actions)="endpoint" v-if="auditor.includes($store.state.role)">
                  <b-button variant="outline" @click="selectTargetEndpoint(row.item, port.item, endpoint.item)" v-b-modal.delete-target-endpoint-modal v-b-tooltip.hover title="Delete Endpoint">
                    <b-icon variant="danger" icon="trash-fill"/>
                  </b-button>
                </template>
              </b-table>
            </template>
            <template #cell(actions)="port" v-if="auditor.includes($store.state.role)">
              <b-dropdown variant="outline" right v-if="auditor.includes($store.state.role)">
                <template #button-content>
                  <b-icon variant="dark" icon="three-dots-vertical"/>
                </template>
                <b-dropdown-item @click="selectTargetPort(row.item, port.item)" v-b-modal.add-target-endpoint-modal>
                  <b-icon variant="success" icon="plus-square"/>
                  <label class="ml-1" variant="dark">Add Endpoint</label>
                </b-dropdown-item>
                <b-dropdown-item variant="danger" @click="selectTargetPort(row.item, port.item)" v-b-modal.delete-target-port-modal>
                  <b-icon icon="trash-fill"/>
                  <label class="ml-1">Delete Port</label>
                </b-dropdown-item>
              </b-dropdown>
            </template>
          </b-table>
        </b-card>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="targets" @pagination="pagination"/>
    <deletion id="delete-target-modal" title="Delete Target" @deletion="deleteTarget" @clean="cleanSelection" v-if="selectedTarget !== null">
      <span><strong>{{ selectedTarget.target }}</strong> target</span>
    </deletion>
    <deletion id="delete-target-port-modal" title="Delete Port" @deletion="deleteTargetPort" @clean="cleanSelection" v-if="selectedTargetPort !== null">
      <span><strong>{{ selectedTargetPort.port }}</strong> port</span>
    </deletion>
    <deletion id="delete-target-endpoint-modal" title="Delete Endpoint" @deletion="deleteTargetEndpoint" @clean="cleanSelection" v-if="selectedTargetEndpoint !== null">
      <span><strong>{{ selectedTargetEndpoint.endpoint }}</strong> endpoint</span>
    </deletion>
    <target id="add-target-modal" :projectId="$route.params.id" @confirm="confirm"/>
    <target-port v-if="selectedTarget !== null" id="add-target-port-modal" :targetId="selectedTarget.id" @confirm="confirm"/>
    <target-endpoint v-if="selectedTargetPort !== null" id="add-target-endpoint-modal" :targetPortId="selectedTargetPort.id" @confirm="confirm"/>
    <task id="task-modal" :target="selectedTarget" :initialized="selectedTarget !== null" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import TableHeader from '@/common/TableHeader'
import Pagination from '@/common/Pagination'
import Target from '@/modals/Target'
import TargetPort from '@/modals/TargetPort'
import TargetEndpoint from '@/modals/TargetEndpoint'
import Task from '@/modals/Task'
export default {
  name: 'projectTargetsPage',
  mixins: [RekonoApi],
  props: {
    project: Object
  },
  data () {
    this.fetchData()
    return {
      data: [],
      targetsFields: [
        { key: 'target', sortable: true },
        { key: 'type', sortable: true },
        { key: 'target_ports.length', label: 'Target Ports', sortable: true },
        { key: 'tasks.length', label: 'Tasks', sortable: true },
        { key: 'actions', sortable: false }
      ],
      targetPortsFields: [
        { key: 'port', sortable: true },
        { key: 'endpoints', sortable: false},
        { key: 'actions', sortable: false },
      ],
      targetEndpointsFields: [
        { key: 'endpoint' },
        { key: 'actions' }
      ],
      selectedTarget: null,
      selectedTargetPort: null,
      selectedTargetEndpoint: null,
      filters: []
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    Target,
    TargetPort,
    TargetEndpoint,
    Task
  },
  watch: {
    targets () {
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
        })
    },
    deleteTarget () {
      this.delete(`/api/targets/${this.selectedTarget.id}/`).then(() => this.fetchData())
    },
    deleteTargetPort () {
      this.delete(`/api/target-ports/${this.selectedTargetPort.id}/`).then(() => this.fetchData())
    },
    deleteTargetEndpoint () {
      this.delete(`/api/target-endpoints/${this.selectedTargetEndpoint.id}/`).then(() => this.fetchData())
    },
    selectTarget (target) {
      this.selectedTarget = target
    },
    selectTargetPort (target, targetPort) {
      this.selectTarget(target)
      this.selectedTargetPort = targetPort
    },
    selectTargetEndpoint (target, targetPort, targetEndpoint) {
      this.selectTargetPort(target, targetPort)
      this.selectedTargetEndpoint = targetEndpoint
    },
    cleanSelection () {
      this.selectedTarget = null
      this.selectedTargetPort = null
      this.selectedTargetEndpoint = null
    }
  }
}
</script>

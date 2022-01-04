<template>
  <div>
    <TableHeader :filters="filters" add="add-target-modal" :addAuth="auditor.includes($store.state.role)" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="targetsFields" :items="targets">
      <template #cell(actions)="row">
        <b-button :disabled="row.item.target_ports.length === 0" @click="row.toggleDetails" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" variant="dark" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" variant="secondary" icon="eye-slash-fill"/>
        </b-button>
        <b-button variant="outline" class="mr-2" v-b-tooltip.hover title="Execute" @click="selectTarget(row.item)" v-b-modal.execute-modal>
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
    <Pagination :page="page" :limit="limit" :limits="limits" :total="total" name="targets" @pagination="pagination"/>
    <Deletion id="delete-target-modal"
      title="Delete Target"
      @deletion="deleteTarget"
      @clean="cleanSelection"
      v-if="selectedTarget !== null">
      <span><strong>{{ selectedTarget.target }}</strong> target</span>
    </Deletion>
    <Deletion id="delete-target-port-modal"
      title="Delete Port"
      @deletion="deleteTargetPort"
      @clean="cleanSelection"
      v-if="selectedTargetPort !== null">
      <span><strong>{{ selectedTargetPort.port }}</strong> port</span>
    </Deletion>
    <Deletion id="delete-target-endpoint-modal"
      title="Delete Endpoint"
      @deletion="deleteTargetEndpoint"
      @clean="cleanSelection"
      v-if="selectedTargetEndpoint !== null">
      <span><strong>{{ selectedTargetEndpoint.endpoint }}</strong> endpoint</span>
    </Deletion>
    <TargetForm id="add-target-modal" :projectId="$route.params.id" @confirm="confirm"/>
    <TargetPortForm v-if="selectedTarget !== null" id="add-target-port-modal" :targetId="selectedTarget.id" @confirm="confirm"/>
    <TargetEndpointForm v-if="selectedTargetPort !== null" id="add-target-endpoint-modal" :targetPortId="selectedTargetPort.id" @confirm="confirm"/>
    <TaskForm id="execute-modal" :target="selectedTarget" :initialized="selectedTarget !== null" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import Targets from '@/backend/targets'
import { targetTypes, auditor } from '@/backend/constants'
import Deletion from '@/common/Deletion.vue'
import TableHeader from '@/common/TableHeader.vue'
import Pagination from '@/common/Pagination.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import TargetForm from '@/modals/TargetForm.vue'
import TargetPortForm from '@/modals/TargetPortForm.vue'
import TargetEndpointForm from '@/modals/TargetEndpointForm.vue'
import TaskForm from '@/modals/TaskForm.vue'
const TargetsApi = Targets.TargetsApi
const TargetPortsApi = Targets.TargetPortsApi
const TargetEndpointsApi = Targets.TargetEndpointsApi
export default {
  name: 'projectTargetsPage',
  mixins: [AlertMixin, PaginationMixin],
  props: {
    project: Object
  },
  data () {
    return {
      auditor: auditor,
      targets: this.fetchData(),
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
    TargetForm,
    TargetPortForm,
    TargetEndpointForm,
    TaskForm
  },
  watch: {
    targets () {
      this.filters = [
        { name: 'Type', values: targetTypes, valueField: 'value', textField: 'value', filterField: 'type' }
      ]
    }
  },
  methods: {
    fetchData (filters = null) {
      if (!filters) {
        filters = {}
      }
      filters.project = this.$route.params.id
      TargetsApi.getAllTargets(this.getPage(), this.getLimit(), filters)
        .then(data => {
          this.total = data.count
          this.targets = data.results
        })
    },
    deleteTarget () {
      TargetsApi.deleteTarget(this.selectedTarget.id)
        .then(() => {
          this.$bvModal.hide('delete-target-modal')
          this.warning(this.selectedTarget.target, 'Target deleted successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(this.selectedTarget.target, 'Unexpected error in target deletion')
        })
    },
    deleteTargetPort () {
      TargetPortsApi.deleteTargetPort(this.selectedTargetPort.id)
        .then(() => {
          this.$bvModal.hide('delete-target-port-modal')
          this.warning(`${this.selectedTarget.target} - ${this.selectedTargetPort.port}`, 'Target port deleted successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(`${this.selectedTarget.target} - ${this.selectedTargetPort.port}`, 'Unexpected error in target port deletion')
        })
    },
    deleteTargetEndpoint () {
      TargetEndpointsApi.deleteTargetEndpoint(this.selectedTargetEndpoint.id)
        .then(() => {
          this.$bvModal.hide('delete-target-endpoint-modal')
          this.warning(`${this.selectedTarget.target} - ${this.selectedTargetEndpoint.endpoint}`, 'Target endpoint deleted successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(`${this.selectedTarget.target} - ${this.selectedTargetEndpoint.endpoint}`, 'Unexpected error in target endpoint deletion')
        })
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

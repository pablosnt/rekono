<template>
  <div>
    <table-header :filters="filters" add="add-target-modal" :showAdd="auditor.includes($store.state.role)" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="targetsFields" :items="data">
      <template #cell(defectdojo_engagement_id)="row">
        <b-link v-if="row.item.defectdojo_engagement_id !== null && defectDojoEnabled" :href="`${defectDojoHost}/engagement/${row.item.defectdojo_engagement_id}`" target="_blank">
          <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
        </b-link>
      </template>
      <template #cell(actions)="row">
        <b-button :disabled="row.item.target_ports.length === 0" @click="showTarget(row)" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" variant="dark" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" variant="secondary" icon="eye-slash-fill"/>
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
              <b-button :disabled="port.item.target_endpoints.length === 0 && port.item.target_technologies.length === 0 && port.item.target_vulnerabilities.length === 0" @click="showTargetPort(port)" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
                <b-icon v-if="!port.detailsShowing" variant="dark" icon="eye-fill"/>
                <b-icon v-if="port.detailsShowing" variant="secondary" icon="eye-slash-fill"/>
              </b-button>
              <b-dropdown variant="outline" right v-if="auditor.includes($store.state.role)">
                <template #button-content>
                  <b-icon variant="dark" icon="three-dots-vertical"/>
                </template>
                <b-dropdown-item @click="selectTargetPort(row.item, port.item)" v-b-modal.add-target-endpoint-modal>
                  <b-icon variant="success" icon="plus-square"/>
                  <label class="ml-1" variant="dark">Add Endpoint</label>
                </b-dropdown-item>
                <b-dropdown-item @click="selectTargetPort(row.item, port.item)" v-b-modal.add-target-technology-modal>
                  <b-icon variant="success" icon="plus-square"/>
                  <label class="ml-1" variant="dark">Add Technology</label>
                </b-dropdown-item>
                <b-dropdown-item @click="selectTargetPort(row.item, port.item)" v-b-modal.add-target-vulnerability-modal>
                  <b-icon variant="success" icon="plus-square"/>
                  <label class="ml-1" variant="dark">Add Vulnerability</label>
                </b-dropdown-item>
                <b-dropdown-item variant="danger" @click="selectTargetPort(row.item, port.item)" v-b-modal.delete-target-port-modal>
                  <b-icon icon="trash-fill"/>
                  <label class="ml-1">Delete Port</label>
                </b-dropdown-item>
              </b-dropdown>
            </template>
            <template #row-details="port">
              <b-card>
                <b-table striped borderles head-variant="ligth" :fields="targetEndpointsFields" :items="port.item.target_endpoints" v-if="port.item.target_endpoints.length > 0">
                  <template #cell(actions)="endpoint" v-if="auditor.includes($store.state.role)">
                    <b-button variant="outline" @click="selectTargetEndpoint(row.item, port.item, endpoint.item)" v-b-modal.delete-target-endpoint-modal v-b-tooltip.hover title="Delete Target Endpoint">
                      <b-icon variant="danger" icon="trash-fill"/>
                    </b-button>
                  </template>
                </b-table>
                <b-table striped borderles head-variant="ligth" :fields="targetTechnologiesFields" :items="port.item.target_technologies" v-if="port.item.target_technologies.length > 0">
                  <template #cell(actions)="technology" v-if="auditor.includes($store.state.role)">
                    <b-button variant="outline" @click="selectTargetTechnology(row.item, port.item, technology.item)" v-b-modal.delete-target-technology-modal v-b-tooltip.hover title="Delete Target Technology">
                      <b-icon variant="danger" icon="trash-fill"/>
                    </b-button>
                  </template>
                </b-table>
                <b-table striped borderles head-variant="ligth" :fields="targetVulnerabilitiesFields" :items="port.item.target_vulnerabilities" v-if="port.item.target_vulnerabilities.length > 0">
                  <template #cell(actions)="vulnerability" v-if="auditor.includes($store.state.role)">
                    <b-button variant="outline" @click="selectTargetVulnerability(row.item, port.item, vulnerability.item)" v-b-modal.delete-target-vulnerability-modal v-b-tooltip.hover title="Delete Target Vulnerability">
                      <b-icon variant="danger" icon="trash-fill"/>
                    </b-button>
                  </template>
                </b-table>
              </b-card>
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
    <deletion id="delete-target-endpoint-modal" title="Delete Target Endpoint" @deletion="deleteTargetEndpoint" @clean="cleanSelection" v-if="selectedTargetEndpoint !== null">
      <span><strong>{{ selectedTargetEndpoint.endpoint }}</strong> endpoint</span>
    </deletion>
    <deletion id="delete-target-technology-modal" title="Delete Target Technology" @deletion="deleteTargetTechnology" @clean="cleanSelection" v-if="selectedTargetTechnology !== null">
      <span><strong>{{ selectedTargetTechnology.name }} {{ selectedTargetTechnology.version }}</strong> technology</span>
    </deletion>
    <deletion id="delete-target-vulnerability-modal" title="Delete Target Vulnerability" @deletion="deleteTargetVulnerability" @clean="cleanSelection" v-if="selectedTargetVulnerability !== null">
      <span><strong>{{ selectedTargetVulnerability.cve }}</strong> vulnerability</span>
    </deletion>
    <target id="add-target-modal" :projectId="$route.params.id" @confirm="confirm"/>
    <target-port v-if="selectedTarget !== null" id="add-target-port-modal" :targetId="selectedTarget.id" @confirm="confirm"/>
    <target-endpoint v-if="selectedTargetPort !== null" id="add-target-endpoint-modal" :targetPortId="selectedTargetPort.id" @confirm="confirm"/>
    <target-technology v-if="selectedTargetPort !== null" id="add-target-technology-modal" :targetPortId="selectedTargetPort.id" @confirm="confirm"/>
    <target-vulnerability v-if="selectedTargetPort !== null" id="add-target-vulnerability-modal" :targetPortId="selectedTargetPort.id" @confirm="confirm"/>
    <task id="task-modal" :target="selectedTarget" :initialized="selectedTarget !== null" @clean="cleanSelection"/>
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
import TargetTechnology from '@/modals/TargetTechnology'
import TargetVulnerability from '@/modals/TargetVulnerability'
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
        { key: 'defectdojo_engagement_id', label: 'Defect-Dojo', sortable: false },
        { key: 'target_ports.length', label: 'Target Ports', sortable: true },
        { key: 'tasks.length', label: 'Tasks', sortable: true },
        { key: 'actions', sortable: false }
      ],
      targetPortsFields: [
        { key: 'port', sortable: true },
        { key: 'target_endpoints.length', label: 'Target Endpoints', sortable: false},
        { key: 'target_technologies.length', label: 'Target Technologies', sortable: false},
        { key: 'target_vulnerabilities.length', label: 'Target Vulnerabilities', sortable: false},
        { key: 'actions', sortable: false },
      ],
      targetEndpointsFields: [
        { key: 'endpoint' },
        { key: 'actions' }
      ],
      targetTechnologiesFields: [
        { key: 'name', label: 'Technology' },
        { key: 'version' },
        { key: 'actions' }
      ],
      targetVulnerabilitiesFields: [
        { key: 'cve', label: 'CVE' },
        { key: 'actions' }
      ],
      selectedTarget: null,
      selectedTargetPort: null,
      selectedTargetEndpoint: null,
      selectedTargetTechnology: null,
      selectedTargetVulnerability: null,
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
    TargetTechnology,
    TargetVulnerability,
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
            let showedTarget = this.data.filter(target => target.id === this.showTargetId)
            showedTarget.forEach(target => target._showDetails = true)
            if (this.showTargetPortId) {
              showedTarget.forEach(target => target.target_ports.filter(tp => tp.id === this.showTargetPortId).forEach(tp => tp._showDetails = true))
            }
          }
        })
    },
    showTarget (row) {
      row.toggleDetails()
      this.showTargetId = row.item._showDetails ? row.item.id : null
    },
    showTargetPort (row) {
      row.toggleDetails()
      this.showTargetPortId = row.item._showDetails ? row.item.id : null
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
    deleteTargetTechnology () {
      this.delete(`/api/target-technologies/${this.selectedTargetTechnology.id}/`).then(() => this.fetchData())
    },
    deleteTargetVulnerability () {
      this.delete(`/api/target-vulnerabilities/${this.selectedTargetVulnerability.id}/`).then(() => this.fetchData())
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
    selectTargetTechnology (target, targetPort, targetTechnology) {
      this.selectTargetPort(target, targetPort)
      this.selectedTargetTechnology = targetTechnology
    },
    selectTargetVulnerability (target, targetPort, targetVulnerability) {
      this.selectTargetPort(target, targetPort)
      this.selectedTargetVulnerability = targetVulnerability
    },
    cleanSelection () {
      this.selectedTarget = null
      this.selectedTargetPort = null
      this.selectedTargetEndpoint = null
    }
  }
}
</script>

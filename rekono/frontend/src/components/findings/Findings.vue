<template>
  <div>
    <b-row>
      <b-col>
        <TableHeader :addAuth="false" @filter="setSearchFilter"/>
      </b-col>
      <b-col v-if="!task" cols="3">
        <b-form-select v-model="selectedTarget" :options="targets" value-field="id" text-field="target"/>
      </b-col>
      <b-col cols="3">
        <b-form-select v-model="selectedFindings" :options="findings" multiple :select-size="2" value-field="value" text-field="value"/>
      </b-col>
      <b-col cols="2" class="d-inline">
        <b-button variant="outline" v-b-tooltip.hover title="You can select one finding and the related findings will be showed. You can also select the finding types that you want to be displayed">
          <b-icon icon="info-circle-fill" variant="info"/>
        </b-button>
        <b-dropdown variant="outline-primary" right disabled>
          <template #button-content>
            <b-icon icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item>
            <!-- Enable finding (if selected finding is disabled) -->
          </b-dropdown-item>
          <b-dropdown-item>
            <!-- Disable finding (if selected finding is enabled) -->
          </b-dropdown-item>
          <b-dropdown-item>
            <!-- Send finding to Defect-Dojo (if selected finding is enabled) -->
          </b-dropdown-item>
          <b-dropdown-item>
            <!-- Create target from finding (if selected finding type is OSINT and there are no targets with this data) -->
          </b-dropdown-item>
        </b-dropdown>
      </b-col>
    </b-row>
    <b-row cols="2" class="mt-3">
      <Finding name="hosts" :fields="hosts" :details="hostDetails" @finding-selected="selectFinding" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
      <Finding name="enumerations" :fields="enumerations" :details="enumerationDetails" @finding-selected="selectFinding" :selection="hostFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
      <Finding name="endpoints" :fields="endpoints" :details="endpointDetails" :selection="enumerationFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
      <Finding name="technologies" :fields="technologies" @finding-selected="selectFinding" :selection="enumerationFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
      <Finding name="vulnerabilities" :fields="vulnerabilities" :details="vulnerabilityDetails" @finding-selected="selectFinding" :selection="technologyAndEnumerationFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
      <Finding name="exploits" :fields="exploits" :details="exploitDetails" :selection="vulnerabilityAndTechnologyFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
      <Finding name="osint" :fields="osint" :details="osintDetails" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
      <Finding name="credentials" :fields="credentials" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search"/>
    </b-row>
  </div>
</template>

<script>
import Targets from '@/backend/targets'
import { portStatusByVariant } from '@/backend/constants'
// import Deletion from '@/common/Deletion.vue'
import TableHeader from '@/common/TableHeader.vue'
import Finding from '@/components/findings/Finding.vue'
const TargetsApi = Targets.TargetsApi
export default {
  name: 'findingsPage',
  props: {
    task: Object
  },
  computed: {
    hostFilter () {
      if (this.selectedHost) {
        return { host: this.selectedHost }
      } else {
        return { host__isnull: true }
      }
      
    },
    enumerationFilter () {
      if (this.selectedEnumeration) {
        return { enumeration: this.selectedEnumeration }
      } else {
        return { enumeration__isnull: true}
      }
    },
    technologyAndEnumerationFilter () {
      if (this.selectedTechnology) {
        return { technology: this.selectedTechnology }
      } else if (this.selectedEnumeration) {
        return { enumeration: this.selectedEnumeration }
      } else {
        return { technology__isnull: true, enumeration__isnull: true }
      }
    },
    vulnerabilityAndTechnologyFilter () {
      if (this.selectedVulnerability) {
        return { vulnerability: this.selectedVulnerability }
      } else if (this.selectedTechnology) {
        return { technology: this.selectedTechnology }
      } else {
        return { vulnerability__isnull: true, technology__isnull: true }
      }
    }
  },
  data () {
    return {
      findings: ['OSINT', 'Credentials', 'Hosts', 'Enumerations', 'Endpoints', 'Technologies', 'Vulnerabilities', 'Exploits'],
      targets: this.fetchTargets(),
      selectedFindings: [],
      selectedTarget: null,
      search: null,
      selectedHost: null,
      selectedEnumeration: null,
      selectedTechnology: null,
      selectedVulnerability: null,
      osint: [
        { key: 'data', sortable: true },
        { key: 'data_type', sortable: true }
      ],
      osintDetails: [
        { field: 'source', title: 'Source', type: 'text' },
        { field: 'reference', title: 'Reference', type: 'link' }
      ],
      hosts: [
        { key: 'address', sortable: true },
        { key: 'os_type', sortable: true }
      ],
      hostDetails: [
        { field: 'os', title: 'OS', type: 'text' }
      ],
      enumerations: [
        { key: 'port', sortable: true },
        { key: 'service', sortable: true}
      ],
      enumerationDetails: [
        { field: 'port_status', title: 'Port Status', type: 'badge', variants: portStatusByVariant }
      ],
      endpoints: [
        { key: 'endpoint', sortable: true }
      ],
      endpointDetails: [
        { field: 'status', title: 'Status', type: 'text'}
      ],
      technologies: [
        { key: 'name', label: 'Technology', sortable: true },
        { key: 'version', sortable: true }
      ],
      technologyDetails: [
        { field: 'description', type: 'text' },
        { field: 'reference', title: 'Reference', type: 'link' }
      ],
      vulnerabilities: [
        { key: 'name', label: 'Vulnerability', sortable: true },
        { key: 'severity', sortable: true },
        { key: 'cve', label: 'CVE', sortable: true }
      ],
      vulnerabilityDetails: [
        { field: 'description', type: 'text' },
        { field: 'cwe', type: 'badge', variant: 'primary' },
        { field: 'osvdb', type: 'badge', variant: 'sedondary' },
        { field: 'reference', title: 'Reference', type: 'link' }
      ],
      credentials: [
        { key: 'email', sortable: true },
        { key: 'username', sortable: true },
        { key: 'secret', sortable: true }
      ],
      exploits: [
        { key: 'name', label: 'Exploit', sortable: true },
        { key: 'reference', sortable: true }
      ],
      exploitDetails: [
        { field: 'description', type: 'text' },
        { field: 'checked', title: 'Checked', type: 'boolean' }
      ]
    }
  },
  components: {
    // Deletion,
    TableHeader,
    Finding
  },
  methods: {
    fetchTargets () {
      if (!this.task) {
        TargetsApi.getAllTargets(null, null, { project: this.$route.params.id })
          .then(data => {
            this.targets = data.results
            if (data.results.length > 0) {
              this.selectedTarget = data.results[0].id
            }
          })
      }
    },
    setSearchFilter (filter) {
      this.search = filter ? filter.search : null
    },
    selectFinding (selection) {
      const id = selection.finding ? selection.finding.id : null
      if (selection.type === 'hosts') {
        this.selectedHost = id
        this.selectedEnumeration = null
        this.selectedTechnology = null
        this.selectedVulnerability = null
      } else if (selection.type === 'enumerations') {
        this.selectedEnumeration = id
        this.selectedTechnology = null
        this.selectedVulnerability = null
      } else if (selection.type === 'technologies') {
        this.selectedTechnology = id
        this.selectedVulnerability = null
      } else if (selection.type === 'vulnerabilities') {
        this.selectedVulnerability = id
      }
    }
  }
}
</script>

<template>
  <div>
    <b-row>
      <b-col>
        <table-header :addAuth="false" @filter="setSearchFilter"/>
      </b-col>
      <b-col v-if="!task && !execution" cols="2">
        <b-form-select v-model="selectedTarget" :options="targets" value-field="id" text-field="target"/>
      </b-col>
      <b-col :cols="!task && !execution ? 2 : 3">
        <b-form-select v-model="selectedFindings" :options="findingTypes" multiple :select-size="2" value-field="value" text-field="value"/>
      </b-col>
      <b-col :cols="!task && !execution ? 1 : 2">
        <b-form-select v-model="activeFilter" :options="activeOptions"/>
      </b-col>
      <b-col cols="1">
        <b-button variant="outline" v-b-tooltip.hover title="You can select one finding and the related findings will be showed. You can also select the finding types that you want to be displayed">
          <b-icon icon="question-circle-fill" variant="info"/>
        </b-button>
      </b-col>
    </b-row>
    <b-row :cols="cols" class="mt-3">
      <finding name="hosts" :fields="hosts" :details="hostDetails" @finding-selected="selectFinding" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :execution="execution ? execution.id : null" :search="search" :active="activeFilter"/>
      <finding name="enumerations" :fields="enumerations" :details="enumerationDetails" @finding-selected="selectFinding" :selection="hostFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search" :active="activeFilter"/>
      <finding name="endpoints" :fields="endpoints" :details="endpointDetails" :selection="enumerationFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search" :active="activeFilter"/>
      <finding name="technologies" :fields="technologies" @finding-selected="selectFinding" :selection="enumerationFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search" :active="activeFilter"/>
      <finding name="vulnerabilities" :fields="vulnerabilities" :details="vulnerabilityDetails" @finding-selected="selectFinding" :selection="technologyAndEnumerationFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search" :active="activeFilter"/>
      <finding name="exploits" :fields="exploits" :details="exploitDetails" :selection="vulnerabilityAndTechnologyFilter" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search" :active="activeFilter"/>
      <finding name="osint" :fields="osint" :details="osintDetails" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search" :active="activeFilter"/>
      <finding name="credentials" :fields="credentials" :findingTypes="selectedFindings" :target="selectedTarget" :task="task ? task.id : null" :search="search" :active="activeFilter"/>
    </b-row>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import TableHeader from '@/common/TableHeader'
import Finding from '@/components/findings/Finding'
export default {
  name: 'findingsPage',
  mixins: [RekonoApi],
  props: {
    task: Object,
    execution: Object,
    cols: {
      type: Number,
      default: 2
    }
  },
  computed: {
    hostFilter () {
      return this.selectedHost ? { host: this.selectedHost } : { host__isnull: true }
    },
    enumerationFilter () {
      return this.selectedEnumeration ? { enumeration: this.selectedEnumeration } : { enumeration__isnull: true}
    },
    technologyAndEnumerationFilter () {
      return this.selectedTechnology ? { technology: this.selectedTechnology } : this.selectedEnumeration ? { enumeration: this.selectedEnumeration } : { technology__isnull: true, enumeration__isnull: true }
    },
    vulnerabilityAndTechnologyFilter () {
      return this.selectedVulnerability ? { vulnerability: this.selectedVulnerability } : this.selectedTechnology ? { technology: this.selectedTechnology } : { vulnerability__isnull: true, technology__isnull: true }
    }
  },
  data () {
    return {
      activeOptions: [{ value: null, text: 'All' }, { value: 'true', text: 'Active' }, { value: 'false', text: 'Disabled' }],
      targets: this.fetchTargets(),
      selectedFindings: [],
      selectedTarget: null,
      search: null,
      activeFilter: null,
      selectedHost: null,
      selectedEnumeration: null,
      selectedTechnology: null,
      selectedVulnerability: null,
      osint: [
        { key: 'data', sortable: true },
        { key: 'data_type', label: 'Type', sortable: true }
      ],
      osintDetails: [
        { field: 'source', title: 'Source', type: 'text' },
        { field: 'reference', title: 'Reference', type: 'link' }
      ],
      hosts: [
        { key: 'address', sortable: true },
        { key: 'os_type', label: 'OS', sortable: true }
      ],
      hostDetails: [
        { field: 'os', title: 'OS', type: 'text' }
      ],
      enumerations: [
        { key: 'port', sortable: true },
        { key: 'service', sortable: true}
      ],
      enumerationDetails: [
        { field: 'port_status', title: 'Port Status', type: 'badge', variants: this.portStatusByVariant }
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
    TableHeader,
    Finding
  },
  methods: {
    fetchTargets () {
      if (!this.task) {
        this.getAllPages('/api/targets/?o=target', { project: this.$route.params.id })
          .then(response => {
            this.targets = response.data.results
            if (response.data.results.length > 0) {
              this.selectedTarget = response.data.results[0].id
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

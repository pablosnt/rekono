<template>
  <div>
    <b-row>
      <b-col>
        <table-header :showAdd="false" @filter="setSearchFilter"/>
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
      <b-col cols="1" v-if="selection">
        <b-button variant="outline" v-b-tooltip.hover title="You can select one finding and the related findings will be showed. You can also select the finding types that you want to see">
          <b-icon icon="question-circle-fill" variant="info"/>
        </b-button>
      </b-col>
    </b-row>
    <b-spinner v-if="loading > 0" variant="danger"/>
    <b-row :cols="cols" class="mt-3" style="height: 40rem; overflow-y: scroll">
      <finding name="hosts" :fields="hosts" :details="hostDetails" @finding-selected="selectFinding" :id="selectedHost" order="address" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
      <finding name="ports" :fields="ports" @finding-selected="selectFinding" :id="selectedPort" :filter="hostFilter" order="-status" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
      <finding name="paths" :fields="paths" :details="pathDetails" :filter="portFilter" order="type" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
      <finding name="technologies" :fields="technologies" :details="technologyDetails" @finding-selected="selectFinding" :id="selectedTechnology" :filter="portFilter" order="name" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
      <finding name="credentials" :fields="credentials" :details="credentialDetails" :filter="technologyFilter" order="email,username" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
      <finding name="vulnerabilities" :fields="vulnerabilities" :details="vulnerabilityDetails" @finding-selected="selectFinding" :id="selectedVulnerability" :filter="technologyAndPortFilter" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
      <finding name="exploits" :fields="exploits" :details="exploitDetails" :filter="vulnerabilityAndTechnologyFilter" order="title" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
      <finding name="osint" :fields="osint" :details="osintDetails" order="data_type" :selectedFindingTypes="selectedFindings" :target="selectedTarget" :task="selectedTask" :execution="selectedExecution" :search="search" :active="activeFilter" :reload="reload" @start="loading += 1" @end="loading -= 1"/>
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
    selection: {
      type: Boolean,
      default: true
    },
    cols: {
      type: Number,
      default: 2
    },
    reload: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    selectedTask () {
      return this.task ? this.task.id : null
    },
    selectedExecution () {
      return this.execution ? this.execution.id : null
    },
    hostFilter () {
      if (this.selection) {
        return this.selectedHost ? { host: this.selectedHost } : { host__isnull: true }
      }
      return null
    },
    portFilter () {
      if (this.selection) {
        return this.selectedPort ? { port: this.selectedPort } : { port__isnull: true}
      }
      return null
    },
    technologyFilter () {
      if (this.selection) {
        return this.selectedTechnology ? { technology: this.selectedTechnology } : { technology__isnull: true }
      }
      return null
    },
    technologyAndPortFilter () {
      if (this.selection) {
        if (this.selectedTechnology) {
          return { technology: this.selectedTechnology }
        } else if (this.selectedPort) {
          return { port: this.selectedPort }
        } else {
          return { technology__isnull: true, port__isnull: true }
        }
      }
      return null
    },
    vulnerabilityAndTechnologyFilter () {
      if (this.selection) {
        if (this.selectedVulnerability) {
          return { vulnerability: this.selectedVulnerability }
        } else if (this.selectedTechnology) {
          return { technology: this.selectedTechnology }
        } else {
          return { vulnerability__isnull: true, technology__isnull: true }
        }
      }
      return null
    }
  },
  data () {
    this.fetchTargets()
    return {
      activeOptions: [{ value: null, text: 'All' }, { value: 'true', text: 'Active' }, { value: 'false', text: 'Disabled' }],
      targets: [],
      selectedFindings: this.$route.query.types ? this.$route.query.types.split(',') : [],
      selectedTarget: this.$route.query.target ? parseInt(this.$route.query.target) : null,
      activeFilter: this.$route.query.active ? this.$route.query.active : true,
      search: null,
      selectedHost: null,
      selectedPort: null,
      selectedTechnology: null,
      selectedVulnerability: null,
      osint: [
        { key: 'data', sortable: true, tdClass: 'text-left' },
        { key: 'data_type', label: 'Type', sortable: true }
      ],
      osintDetails: [
        { field: 'source', title: 'Source', type: 'text' },
        { field: 'reference', title: 'Reference', type: 'link' }
      ],
      hosts: [
        { key: 'address', sortable: true, tdClass: 'text-left' },
        { key: 'os_type', label: 'OS', sortable: true }
      ],
      hostDetails: [
        { field: 'os', title: 'OS', type: 'text' }
      ],
      ports: [
        { key: 'port', sortable: true },
        { key: 'protocol', sortable: true },
        { key: 'status', sortable: true },
        { key: 'service', sortable: true, tdClass: 'text-left' }
      ],
      paths: [
        { key: 'path', sortable: true, tdClass: 'text-left' },
        { key: 'type', sortable: true },
      ],
      pathDetails: [
        { field: 'status', title: 'Status', type: 'text' },
        { field: 'extra', type: 'text' },
      ],
      technologies: [
        { key: 'name', label: 'Technology', sortable: true, tdClass: 'text-left' },
        { key: 'version', sortable: true }
      ],
      technologyDetails: [
        { field: 'description', type: 'text' },
        { field: 'reference', title: 'Reference', type: 'link' }
      ],
      credentials: [
        { key: 'email', sortable: true, tdClass: 'text-left' },
        { key: 'username', sortable: true, tdClass: 'text-left' },
        { key: 'secret', sortable: true, tdClass: 'text-left' }
      ],
      credentialDetails: [
        { field: 'context', type: 'text' },
      ],
      vulnerabilities: [
        { key: 'name', label: 'Vulnerability', sortable: true, tdClass: 'text-left' },
        { key: 'severity', sortable: true },
        { key: 'cve', label: 'CVE', sortable: true }
      ],
      vulnerabilityDetails: [
        { field: 'description', type: 'text' },
        { field: 'cwe', type: 'badge', variant: 'primary' },
        { field: 'osvdb', type: 'badge', variant: 'sedondary' },
        { field: 'reference', title: 'Reference', type: 'link' }
      ],
      exploits: [
        { key: 'title', label: 'Exploit', sortable: true, tdClass: 'text-left' },
        { key: 'edb_id', label: 'EDB-ID', sortable: true }
      ],
      exploitDetails: [
        { field: 'reference', title: 'Reference', type: 'text'}
      ],
      loading: 0
    }
  },
  components: {
    TableHeader,
    Finding
  },
  watch: {
    selectedFindings () {
      this.changeHashParam('types', this.selectedFindings.join(','))
    },
    selectedTarget () {
      this.changeHashParam('target', this.selectedTarget)
    },
    activeFilter () {
      this.changeHashParam('active', this.activeFilter)
    }
  },
  methods: {
    fetchTargets () {
      if (!this.task) {
        this.getAllPages('/api/targets/', { project: this.$route.params.id, o: 'target' })
          .then(results => {
            this.targets = results
            if (results.length > 0) {
              this.selectedTarget = results[0].id
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
        this.selectedPort = null
        this.selectedTechnology = null
        this.selectedVulnerability = null
      } else if (selection.type === 'ports') {
        this.selectedPort = id
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

<template>
  <div>
    <b-card-group deck>
      <b-card bg-variant="dark" text-variant="white">
        <b-row align-v="center" class="text-right">
          <b-col>
            <p class="h1 text-center">
              <b-icon v-if="!project" icon="box"/>
              <b-icon v-if="project" icon="geo-fill"/>
            </p>
          </b-col>
          <b-col v-if="!project">
            <b-card-title class="text-right" @click="$router.push('projects')">{{ projects }} Projects</b-card-title>
            <b-card-text class="text-right">{{ targets }} Targets</b-card-text>
          </b-col>
          <b-col v-if="project">
            <b-card-title class="text-right">{{ targets }} Targets</b-card-title>
          </b-col>
        </b-row>
      </b-card>
      <b-card bg-variant="success" text-variant="white" class="text-right">
        <b-row align-v="center">
          <b-col>
            <p class="h1 text-center"><b-icon icon="play-circle-fill"/></p>
          </b-col>
          <b-col>
            <b-card-title class="text-right">{{ tasks }} Tasks</b-card-title>
            <b-card-text class="text-right">{{ executions }} Executions</b-card-text>
          </b-col>
        </b-row>
      </b-card>
      <b-card bg-variant="danger" text-variant="white">
        <b-row align-v="center">
          <b-col>
            <p class="h1 text-center"><b-icon icon="flag-fill"/></p>
          </b-col>
          <b-col>
            <b-card-title class="text-right">{{ findings }} Findings</b-card-title>
            <b-card-text class="text-right">{{ vulnerabilities }} Vulnerabilities</b-card-text>
          </b-col>
        </b-row>
      </b-card>
    </b-card-group>
    <b-card-group deck class="mt-3 mb-2">
      <b-card style="min-width: 20rem;">
        <tasks-by-status :height="250" :requested="requested" :skipped="skipped" :running="running" :cancelled="cancelled" :error="error" :completed="completed"/>
      </b-card>
      <b-card style="min-width: 20rem;">
        <findings-by-type :height="250" :osint="osint" :credentials="credentials" :hosts="hosts" :ports="ports" :paths="paths" :technologies="technologies" :vulnerabilities="vulnerabilities" :exploits="exploits"/>
      </b-card>
    </b-card-group>
    <hr/>
    <b-row align-h="around" v-if="vulnerabilities > 0">
      <h2>Vulnerabilities</h2>
      <b-col cols="3">
        <b-form-select v-model="timeFilter" :options="timeOptions" @change="countVulnerabilities">
          <template #first>
            <b-form-select-option :value="null">All time</b-form-select-option>
          </template>
        </b-form-select>
      </b-col>
    </b-row>
    <b-card-group deck class="mt-3" v-if="vulnerabilities > 0">
      <b-card style="min-width: 20rem;">
        <vulnerabilities-by-severity :height="500" label="Vulnerabilities by severity" :critical="critical" :high="high" :medium="medium" :low="low" :info="info"/>
      </b-card>
      <b-card style="min-width: 20rem;">
        <vulnerabilities-by-severity :height="500" label="Vulnerabilities with exploit by severity" :critical="criticalExploit" :high="highExploit" :medium="mediumExploit" :low="lowExploit" :info="infoExploit"/>
      </b-card>
    </b-card-group>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import FindingsByType from './FindingsByType'
import TasksByStatus from './TasksByStatus'
import VulnerabilitiesBySeverity from './VulnerabilitiesBySeverity'
export default {
  name: 'dashboard',
  mixins: [RekonoApi],
  props: {
    project: Object
  },
  data () {
    this.countProjects()
    this.countTargets()
    this.countExecutions()
    return {
      timeOptions: [
        { value: 7, text: 'Last 7 days'},
        { value: 15, text: 'Last 15 days'},
        { value: 30, text: 'Last 30 days'}
      ], 
      timeFilter: null,
      projects: 0,
      targets: 0,
      requested: 0,
      skipped: 0,
      running: 0,
      cancelled: 0,
      error: 0,
      completed: 0,
      tasks: 0,
      executions: 0,
      osint: 0,
      credentials: 0,
      hosts: 0,
      ports: 0,
      paths: 0,
      technologies: 0,
      critical: 0,
      criticalExploit: 0,
      high: 0,
      highExploit: 0,
      medium: 0,
      mediumExploit: 0,
      low: 0,
      lowExploit: 0,
      info: 0,
      infoExploit: 0,
      vulnerabilities: 0,
      exploits: 0,
      findings: 0
    }
  },
  components: {
    FindingsByType,
    TasksByStatus,
    VulnerabilitiesBySeverity
  },
  watch: {
    executions () {
      this.countTasks()
      this.countVulnerabilities()
      this.countFindings()
    }
  },
  methods: {
    getFilter (field, filter = null) {
      if (this.project) {
        filter = { [field]: this.project.id }
      }
      return filter
    },
    countProjects () {
      if (!this.project) {
        this.get('/api/projects/', 1, 1).then(response => { this.projects = response.data.count })
      } else {
        this.projects = 1
      }
    },
    countTargets () {
      this.get('/api/targets/', 1, 1, this.getFilter('project')).then(response => { this.targets = response.data.count })
    },
    countTasks () {
      let filter = this.getFilter('target__project', { })
      this.statuses.forEach(status => {
        filter.status = status
        this.get('/api/tasks/', 1, 1, filter).then(response => { this[status.toLowerCase()] = response.data.count; this.tasks = (this.tasks ? this.tasks : 0) + response.data.count })
      })
    },
    countExecutions () {
      this.get('/api/executions/', 1, 1, this.getFilter('task__project')).then(response => { this.executions = response.data.count })
    },
    countFindings () {
      let filter = this.getFilter('executions__task__target__project', { })
      filter.is_active = 'true'
      this.findingTypes.forEach(type => {
        this.get(`/api/${type.toLowerCase()}/`, 1, 1, filter).then(response => { this[type.toLowerCase()] = response.data.count; this.findings = (this.findings ? this.findings : 0) + response.data.count })
      })
    },
    countVulnerabilities () {
      let filter = this.getFilter('executions__task__target__project', { })
      filter.is_active = 'true'
      if (this.timeFilter) {
        let date = new Date()
        date.setDate(date.getDate() - this.timeFilter)
        filter.last_seen__gte = date.toISOString().replace('T', ' ').split('.', 1)[0]
      }
      this.severities.forEach(severity => {
        filter.severity = severity
        this.get('/api/vulnerabilities/', 1, 1, filter).then(response => this[severity.toLowerCase()] = response.data.count)
      })
      filter.exploit__isnull = 'false'
      this.severities.forEach(severity => {
        filter.severity = severity
        this.get('/api/vulnerabilities/', 1, 1, filter).then(response => this[`${severity.toLowerCase()}Exploit`] = response.data.count)
      })
    }
  }
}
</script>

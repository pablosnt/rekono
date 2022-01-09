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
        <tasks-by-status :height="height" :requested="requested" :skipped="skipped" :running="running" :cancelled="cancelled" :error="error" :completed="completed"/>
      </b-card>
      <b-card style="min-width: 20rem;">
        <findings-by-type :height="height" :osint="osint" :credentials="credentials" :hosts="hosts" :enumerations="enumerations" :endpoints="endpoints" :technologies="technologies" :vulnerabilities="vulnerabilities" :exploits="exploits"/>
      </b-card>
    </b-card-group>
    <hr/>
    <b-row align-h="around">
      <h2>Vulnerabilities</h2>
      <b-col cols="3">
        <b-form-select v-model="timeFilter" :disabled="vulnerabilities === 0" :options="timeOptions" @change="countVulnerabilities">
          <template #first>
            <b-form-select-option :value="null">All time</b-form-select-option>
          </template>
        </b-form-select>
      </b-col>
    </b-row>
    <b-card-group deck class="mt-3">
      <b-card style="min-width: 20rem;">
        <vulnerabilities-by-severity :height="height" label="Vulnerabilities by severity" :critical="critical" :high="high" :medium="medium" :low="low" :info="info"/>
      </b-card>
      <b-card style="min-width: 20rem;">
        <vulnerabilities-by-severity :height="height" label="Vulnerabilities with exploit by severity" :critical="criticalExploit" :high="highExploit" :medium="mediumExploit" :low="lowExploit" :info="infoExploit"/>
      </b-card>
    </b-card-group>
  </div>
</template>

<script>
import ProjectsApi from '@/backend/projects'
import Targets from '@/backend/targets'
import TasksApi from '@/backend/tasks'
import ExecutionsApi from '@/backend/executions'
import FindingsApi from '@/backend/findings'
import { severities, statuses } from '@/backend/constants'
import FindingsByType from './FindingsByType.vue'
import TasksByStatus from './TasksByStatus.vue'
import VulnerabilitiesBySeverity from './VulnerabilitiesBySeverity.vue'
const TargetsApi = Targets.TargetsApi
export default {
  name: 'dashboard',
  props: ['project'],
  data () {
    return {
      height: 250,
      timeOptions: [
        { value: 7, text: 'Last 7 days'},
        { value: 15, text: 'Last 15 days'},
        { value: 30, text: 'Last 30 days'}
      ], 
      timeFilter: null,
      projects: this.countProjects(),
      targets: this.countTargets(),
      requested: 0,
      skipped: 0,
      running: 0,
      cancelled: 0,
      error: 0,
      completed: 0,
      tasks: this.countTasks(),
      executions: this.countExecutions(),
      osint: 0,
      credentials: 0,
      hosts: 0,
      enumerations: 0,
      endpoints: 0,
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
      infoExploit: this.countVulnerabilities(),
      vulnerabilities: 0,
      exploits: 0,
      findings: this.countFindings()
    }
  },
  components: {
    FindingsByType,
    TasksByStatus,
    VulnerabilitiesBySeverity
  },
  methods: {
    getFilter (field) {
      let filter = null
      if (this.project) {
        filter = { [field]: this.project.id }
      }
      return filter
    },
    countProjects () {
      if (!this.project) {
        ProjectsApi.countProjects().then(count => { this.projects = count })
      } else {
        this.projects = 1
      }
    },
    countTargets () {
      TargetsApi.countTargets(this.getFilter('project')).then(count => { this.targets = count })
    },
    countTasks () {
      let filter = this.getFilter('project')
      if (filter === null) {
        filter = {}
      }
      for (let i in statuses) {
        filter.status = statuses[i]
        TasksApi.countTasks(filter).then(count => { this[statuses[i].toLowerCase()] = count; this.tasks = (this.tasks ? this.tasks : 0) + count })
      }
    },
    countExecutions () {
      ExecutionsApi.countExecutions(this.getFilter('task__project')).then(count => { this.executions = count })
    },
    countFindings () {
      let filter = this.getFilter('execution__task__target__project')
      if (filter === null) {
        filter = {}
      }
      filter.is_active = 'true'
      const types = ['osint', 'credentials', 'hosts', 'enumerations', 'endpoints', 'technologies', 'vulnerabilities', 'exploits']
      for (let i in types) {
        FindingsApi.countFindings(types[i], filter).then(count => { this[types[i]] = count; this.findings = (this.findings ? this.findings : 0) + count })
      }
    },
    countVulnerabilities () {
      let filter = this.getFilter('execution__task__target__project')
      if (filter === null) {
        filter = {}
      }
      filter.is_active = 'true'
      if (this.timeFilter) {
        let date = new Date()
        date.setDate(date.getDate() - this.timeFilter)
        filter.creation__gte = date.toISOString().replace('T', ' ').split('.', 1)[0]
      }
      for (let i in severities) {
        filter.severity = severities[i]
        FindingsApi.countFindings('vulnerabilities', filter).then(count => { this[severities[i].toLowerCase()] = count })
      }
      filter.exploit__isnull = 'false'
      for (let i in severities) {
        filter.severity = severities[i]
        FindingsApi.countFindings('vulnerabilities', filter).then(count => { this[`${severities[i].toLowerCase()}Exploit`] = count })
      }
    }
  }
}
</script>

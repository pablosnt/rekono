<template>
  <main-tabs @click="changeMainTab">
    <template v-slot:projects>
      <b-tabs fill card active-nav-item-class="font-weight-bold text-danger">
        <b-tab lazy active @click="changeSubTab('details')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="bar-chart-line-fill"/> Details
          </template>
          <projectSummary :project="project"/>
        </b-tab>
        <b-tab lazy :active="path.includes('targets')" @click="changeSubTab('targets')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="geo-fill"/> Targets
          </template>
          <targets :project="project"/>
        </b-tab>
         <b-tab lazy :active="path.includes('tasks')" @click="changeSubTab('tasks')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="collection-play-fill"/> Tasks
          </template>
          <tasks :project="project"/>
        </b-tab>
         <b-tab lazy :active="path.includes('findings')" @click="changeSubTab('findings')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="flag-fill"/> Findings
          </template>
          <findings :project="project"/>
        </b-tab>
         <b-tab lazy :active="path.includes('members')" @click="changeSubTab('members')" title-link-class="text-secondary" v-if="$store.state.role === 'Admin'">
          <template #title>
            <b-icon icon="people-fill"/> Members
          </template>
          <members :project="project"/>
        </b-tab>
      </b-tabs>
    </template>
  </main-tabs>
</template>

<script>
import MainTabs from '@/common/MainTabs.vue'
import Summary from '@/components/project/Summary.vue'
import Targets from '@/components/project/Targets.vue'
import Tasks from '@/components/project/Tasks.vue'
import Findings from '@/components/project/Findings.vue'
import Members from '@/components/project/Members.vue'
export default {
  name: 'projectDetails',
  props: {
    project: {
      type: Object,
      default: null
    }
  },
  data () {
    return {
      path: window.location.hash
    }
  },
  components: {
    mainTabs: MainTabs,
    projectSummary: Summary,
    targets: Targets,
    tasks: Tasks,
    findings: Findings,
    members: Members
  },
  methods: {
    changeMainTab (tab) {
      this.$router.push(`/${tab}`)
    },
    changeSubTab (tab) {
      window.location.hash = `projects/${this.$route.params.id}/${tab}`
    }
  }
}
</script>

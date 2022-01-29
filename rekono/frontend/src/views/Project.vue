<template>
  <main-tabs @click="changeMainTab">
    <template v-slot:projects>
      <b-tabs fill active-nav-item-class="font-weight-bold text-danger">
        <b-tab lazy :active="path.includes('details')" @click="changeSubTab('details')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="bar-chart-line-fill"/> Dashboard
          </template>
          <dashboard class="mt-3" :project="project"/>
        </b-tab>
        <b-tab lazy :active="path.includes('targets')" @click="changeSubTab('targets')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="geo-fill"/> Targets
          </template>
          <targets class="mt-3" :project="project"/>
        </b-tab>
         <b-tab lazy :active="path.includes('tasks')" @click="changeSubTab('tasks')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="collection-play-fill"/> Tasks
          </template>
          <tasks class="mt-3" :project="project"/>
        </b-tab>
         <b-tab lazy :active="path.includes('findings')" @click="changeSubTab('findings')" title-link-class="text-secondary">
          <template #title>
            <b-icon icon="flag-fill"/> Findings
          </template>
          <findings class="mt-3" :project="project"/>
        </b-tab>
         <b-tab lazy :active="path.includes('members')" @click="changeSubTab('members')" title-link-class="text-secondary" v-if="$store.state.role === 'Admin'">
          <template #title>
            <b-icon icon="people-fill"/> Members
          </template>
          <members class="mt-3" :project="project"/>
        </b-tab>
      </b-tabs>
    </template>
  </main-tabs>
</template>

<script>
import MainTabs from '@/common/MainTabs'
import Dashboard from '@/components/project/Dashboard'
import Targets from '@/components/project/Targets'
import Tasks from '@/components/project/Tasks'
import Findings from '@/components/findings/Findings'
import Members from '@/components/project/Members'
export default {
  name: 'projectPage',
  props: {
    project: Object
  },
  data () {
    return {
      path: window.location.hash
    }
  },
  components: {
    MainTabs,
    Dashboard,
    Targets,
    Tasks,
    Findings,
    Members
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

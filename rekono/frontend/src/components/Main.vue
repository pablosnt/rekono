<template>
  <b-card fluid>
    <b-tabs fill card vertical active-nav-item-class="font-weight-bold text-danger">
      <b-tab lazy @click="changeHref('dasboard')" active title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="bar-chart-line-fill"/> Dashboard
        </template>
        <dashboard/>
      </b-tab>
      <b-tab lazy :active="activeTab === 'projects'" @click="changeHref('projects')" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="briefcase-fill"/> Projects
        </template>
        <projects/>
      </b-tab>
      <b-tab lazy :active="activeTab === 'tools'" @click="changeHref('tools')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="tools"/> Tools
        </template>
        <tools/>
      </b-tab>
      <b-tab lazy :active="activeTab === 'processes'" @click="changeHref('processes')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="nut-fill"/> Processes
        </template>
        <processes/>
      </b-tab>
      <b-tab lazy :active="activeTab === 'wordlists'" @click="changeHref('wordlists')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="chat-left-dots-fill"/> Wordlists
        </template>
        <wordlists/>
      </b-tab>
      <b-tab lazy :active="activeTab === 'users'" @click="changeHref('users')" v-if="$store.state.role === 'Admin'" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="person-fill"/> Users
        </template>
        <users/>
      </b-tab>
    </b-tabs>
  </b-card>
</template>

<script>
import Dashboard from './Dashboard.vue'
import Projects from './Projects.vue'
import Tools from './Tools.vue'
import Processes from './Processes.vue'
import Wordlists from './Wordlists.vue'
import Users from './Users.vue'
export default {
  name: 'mainPage',
  data () {
    return {
      auditor: ['Admin', 'Auditor'],
      activeTab: window.location.hash.replace('#/', '')
    }
  },
  components: {
    'dashboard': Dashboard,
    'projects': Projects,
    'tools': Tools,
    'processes': Processes,
    'wordlists': Wordlists,
    'users': Users
  },
  methods: {
    changeHref (href) {
      window.location.hash = href
    }
  }
}
</script>

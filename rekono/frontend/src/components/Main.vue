<template>
  <b-card fluid>
    <b-tabs id="main" pills card vertical>
      <b-tab title="Dashboard" lazy @click="changeHref('dasboard')" active>
          <dashboard/>
      </b-tab>
      <b-tab title="Projects" lazy :active="activeTab === 'projects'" @click="changeHref('projects')">
        <projects/>
      </b-tab>
      <b-tab title="Tools" lazy :active="activeTab === 'tools'" @click="changeHref('tools')" v-if="auditor.includes($store.state.role)">
        <tools/>
      </b-tab>
      <b-tab title="Processes" lazy :active="activeTab === 'processes'" @click="changeHref('processes')" v-if="auditor.includes($store.state.role)">
        <processes/>
      </b-tab>
      <b-tab title="Resources" lazy :active="activeTab === 'resources'" @click="changeHref('resources')" v-if="auditor.includes($store.state.role)">
        <resources/>
      </b-tab>
      <b-tab title="Users" lazy :active="activeTab === 'users'" @click="changeHref('users')" v-if="$store.state.role === 'Admin'">
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
import Resources from './Resources.vue'
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
    'resources': Resources,
    'users': Users
  },
  methods: {
    changeHref (href) {
      window.location.hash = href
    }
  }
}
</script>

<style scoped>
body {
  background-color: #fff;
}
</style>

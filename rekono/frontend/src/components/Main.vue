<template>
  <b-card fluid>
    <b-tabs id="main" pills card vertical>
      <b-tab title="Dashboard" active>
          <dashboard/>
      </b-tab>
      <b-tab title="Projects">
        <projects/>
      </b-tab>
      <b-tab title="Tools" v-if="auditor.includes($store.state.role)">
        <tools/>
      </b-tab>
      <b-tab title="Processes" v-if="auditor.includes($store.state.role)">
        <processes/>
      </b-tab>
      <b-tab title="Resources" v-if="auditor.includes($store.state.role)">
        <resources/>
      </b-tab>
      <b-tab title="Users" v-if="$store.state.role === 'Admin'">
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
      auditor: ['Admin', 'Auditor']
    }
  },
  components: {
    'dashboard': Dashboard,
    'projects': Projects,
    'tools': Tools,
    'processes': Processes,
    'resources': Resources,
    'users': Users
  }
}
</script>

<style scoped>
body {
  background-color: #fff;
}
</style>

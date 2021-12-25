<template>
  <tabs @click="changeTab">
    <template v-slot:dashboard>
      <dashboard/>
    </template>
    <template v-slot:projects>
      <projects/>
    </template>
    <template v-slot:tools>
      <tools/>
    </template>
    <template v-slot:processes>
      <processes/>
    </template>
    <template v-slot:wordlists>
      <wordlists/>
    </template>
    <template v-slot:users>
      <users/>
    </template>
  </tabs>
</template>

<script>
import MainTabs from '@/common/MainTabs.vue'
import Dashboard from '@/components/Dashboard.vue'
import Projects from '@/components/Projects.vue'
import Tools from '@/components/Tools.vue'
import Processes from '@/components/Processes.vue'
import Wordlists from '@/components/Wordlists.vue'
import Users from '@/components/Users.vue'
export default {
  name: 'mainPage',
  components: {
    tabs: MainTabs,
    dashboard: Dashboard,
    projects: Projects,
    tools: Tools,
    processes: Processes,
    wordlists: Wordlists,
    users: Users
  },
  methods: {
    changeTab (tab) {
      window.location.hash = tab
    }
  }
}
</script>

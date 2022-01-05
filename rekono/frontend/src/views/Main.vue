<template>
  <MainTabs @click="changeTab">
    <template v-slot:dashboard>
      <Dashboard/>
    </template>
    <template v-slot:projects>
      <Projects/>
    </template>
    <template v-slot:tools>
      <Tools/>
    </template>
    <template v-slot:processes>
      <Processes/>
    </template>
    <template v-slot:wordlists>
      <Wordlists/>
    </template>
    <template v-slot:users>
      <Users/>
    </template>
  </MainTabs>
</template>

<script>
import MainTabs from '@/common/MainTabs.vue'
import Dashboard from '@/components/dashboard/Dashboard.vue'
import Projects from '@/components/Projects.vue'
import Tools from '@/components/Tools.vue'
import Processes from '@/components/Processes.vue'
import Wordlists from '@/components/Wordlists.vue'
import Users from '@/components/Users.vue'
export default {
  name: 'mainPage',
  components: {
    MainTabs,
    Dashboard,
    Projects,
    Tools,
    Processes,
    Wordlists,
    Users
  },
  methods: {
    changeTab (tab) {
      window.location.hash = tab
    }
  }
}
</script>

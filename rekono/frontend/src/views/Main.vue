<template>
  <main-tabs @click="changeTab">
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
  </main-tabs>
</template>

<script>
import MainTabs from '@/common/MainTabs'
import Dashboard from '@/components/dashboard/Dashboard'
import Projects from '@/components/Projects'
import Tools from '@/components/Tools'
import Processes from '@/components/Processes'
import Wordlists from '@/components/Wordlists'
import Users from '@/components/Users'
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

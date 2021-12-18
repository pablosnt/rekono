<template>
  <div>
    <commonHeader v-if="$store.state.user != null"/>
    <div id="app">
      <router-view/>
    </div>
  </div>
</template>

<script>
import Header from '@/common/Header.vue'
export default {
  name: 'App',
  components: {
    'commonHeader': Header
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>

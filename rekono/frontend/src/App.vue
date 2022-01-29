<template>
  <div>
    <main-header v-if="$store.state.user != null"/>
    <div id="app">
      <router-view/>
    </div>
  </div>
</template>

<script>
import MainHeader from './common/MainHeader'
export default {
  name: 'App',
  components: {
    MainHeader
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

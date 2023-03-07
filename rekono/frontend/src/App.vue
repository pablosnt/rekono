<template>
  <div class="d-flex flex-column min-vh-100">
    <main-header v-if="$store.state.user != null"/>
    <div id="app" class="flex-fill">
      <router-view/>
    </div>
    <footer class="text-muted text-center mb-2">
      <b-container>
        <label>© 2022 Rekono Mantainers. All rights reserved</label>
      </b-container>
    </footer>
  </div>
</template>

<script>
import MainHeader from './common/MainHeader';
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

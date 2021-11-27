<template>
  <div>
    <b-navbar type="dark" variant="dark">
      <b-navbar-brand href="/" style="margin-left: 15px">
        <img src="/static/logo.png" width="30" height="30" class="d-inline-block align-top" alt="Rekono">
        Rekono
      </b-navbar-brand>
      <b-navbar-nav class="ml-auto">
        <b-nav-item-dropdown right>
          <template #button-content>
            <b-icon style="width: 30px; height: 30px;" icon="person-fill"/>
          </template>
          <b-dropdown-item href="#">Profile</b-dropdown-item>
          <b-dropdown-item v-on:click.prevent="handleLogout">Logout</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>
import store from '../store/'
export default {
  name: 'commonHeader',
  methods: {
    handleLogout (event) {
      store.dispatch('logoutAction').then(
        this.$router.push('/login')
      )
    }
  }
}
</script>

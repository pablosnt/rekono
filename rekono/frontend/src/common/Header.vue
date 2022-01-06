<template>
  <div>
    <b-navbar type="dark" variant="dark">
      <b-navbar-brand href="/" style="margin-left: 15px">
        <img src="/static/logo-white.png" width="120" height="30" class="d-inline-block align-top" alt="Rekono">
      </b-navbar-brand>
      <b-navbar-nav class="ml-auto">
        <b-nav-item-dropdown right>
          <template #button-content>
            <b-icon style="width: 20px; height: 20px;" icon="person-fill" variant="light"/>
          </template>
          <b-dropdown-item @click="$router.push('/profile')">Profile</b-dropdown-item>
          <b-dropdown-item href="/api/schema/swagger-ui.html?docExpansion=none" target="_blank">Rekono API Rest</b-dropdown-item>
          <b-dropdown-item @click="handleLogout">Logout</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>
export default {
  name: 'commonHeader',
  methods: {
    handleLogout (event) {
      event.preventDefault()
      this.$store.dispatch('logoutAction')
    }
  }
}
</script>

<style lang="scss" scoped>
$dark: black;
@import 'bootstrap/scss/bootstrap';
</style>

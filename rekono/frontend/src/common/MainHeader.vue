<template>
  <div>
    <b-navbar type="dark" variant="dark">
      <b-button variant="outline" @click="$router.back()" :disabled="!backButton" v-if="showBackButton">
        <b-icon variant="white" icon="chevron-left"/>
      </b-button>
      <b-navbar-brand to="/dashboard" replace style="margin-left: 15px">
        <img src="/static/logo-white.png" width="100" class="d-inline-block align-top" alt="Rekono">
      </b-navbar-brand>
      <b-navbar-nav class="ml-auto">
        <b-nav-item-dropdown right>
          <template #button-content>
            <b-icon icon="person-fill" variant="light"/>
          </template>
          <b-dropdown-item @click="$router.push('/profile')">
            <b-icon variant="black" icon="person-fill"/>
            <label class="ml-2">Profile</label>
          </b-dropdown-item>
          <b-dropdown-item @click="$router.push('/settings')" v-if="$store.state.role === 'Admin'">
            <b-icon variant="black" icon="sliders"/>
            <label class="ml-2">Settings</label>
          </b-dropdown-item>
          <b-dropdown-item :href="getUrl('/api/schema/swagger-ui.html')" target="_blank">
            <b-icon variant="danger" icon="code-slash"/>
            <label class="ml-2">Rekono API Rest</label>
          </b-dropdown-item>
          <b-dropdown-item @click.native.prevent="logout">
            <b-icon variant="secondary" icon="box-arrow-right"/>
            <label class="ml-2">Logout</label>
          </b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import { refreshTokenKey } from '@/backend/tokens'

export default {
  name: 'mainHeader',
  mixins: [RekonoApi],
  methods: {
    logout () {
      this.post('/api/logout/', { refresh_token: sessionStorage.getItem(refreshTokenKey) })
      this.$store.dispatch('logout')
    }
  },
  data () {
    return {
      backButton: false,
      showBackButton: process.env.IS_ELECTRON
    }
  },
  watch: {
    $route (to, from){
      if (from && from.name) {
        this.backButton = true
      } else {
        this.backButton = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
$dark: black;
@import 'bootstrap/scss/bootstrap';
</style>

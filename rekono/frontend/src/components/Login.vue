<template>
<!-- TODO: Replace Vue.JS logo by Rekono logo -->
  <div class="fixed-top d-flex align-items-center justify-content-center" style="bottom: 0">
    <b-card id="login-form" title="Welcome to Rekono!" img-src="https://vuejs.org/images/logo.png" img-top img-height="150" class="mb-3">
      <b-alert v-model="loginError" variant="danger">
        <b-icon icon="exclamation-circle-fill" variant="danger"></b-icon>
        Invalid credentials
      </b-alert>
      <form v-on:submit.prevent="handleLogin">
        <b-input-group size="lg" class="mb-3">
          <b-input-group-prepend is-text>
            <div class="h4"><b-icon icon="person-fill"/></div>
          </b-input-group-prepend>
          <b-form-input type="text" v-model="username" required placeholder="Username" :state="usernameState" autofocus/>
        </b-input-group>
        <b-input-group size="lg" class="mb-3">
          <b-input-group-prepend is-text>
            <div class="h4"><b-icon icon="key-fill"/></div>
          </b-input-group-prepend>
          <b-form-input type="password" v-model="password" required placeholder="Password" :state="passwordState"/>
        </b-input-group>
        <b-button type="submit" variant="dark">Login</b-button>
      </form>
    </b-card>
  </div>
</template>

<script>
import store from '../store/'
export default {
  name: 'loginForm',
  computed: {
    usernameState () {
      return this.username.length > 0 ? true : null
    },
    passwordState () {
      return this.password.length > 0 ? true : null
    }
  },
  data () {
    return {
      username: '',
      password: '',
      loginError: false
    }
  },
  methods: {
    handleLogin (event) {
      if (this.username !== '' && this.password !== '') {
        store.dispatch('loginAction', { username: this.username, password: this.password })
          .then(() => {
            this.loginError = false
            this.$router.push('/dashboard')
          })
          .catch(() => {
            this.loginError = true
          })
      }
    }
  }
}
</script>

<style>
body {
  background-image: url('~@/assets/art.jpg');
  background-size: cover;
}
#login-form {
  background: white;
}
</style>

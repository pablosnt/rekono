<template>
  <div id="login-page" class="fixed-top d-flex align-items-center justify-content-center" style="bottom: 0">
    <b-card id="login-form" img-src="/static/logo-black.png" img-top img-height="150" class="mb-3">
      <b-alert v-model="loginError" variant="danger">
        <b-icon icon="exclamation-circle-fill" variant="danger"></b-icon>
        Invalid credentials
      </b-alert>
      <form v-on:submit.prevent="handleLogin">
        <b-input-group size="lg" class="mb-3">
          <b-input-group-prepend is-text>
            <b-icon icon="person-fill"/>
          </b-input-group-prepend>
          <b-form-input type="text" v-model="username" placeholder="Username" :state="usernameState" autofocus required/>
        </b-input-group>
        <b-input-group size="lg" class="mb-3">
          <b-input-group-prepend is-text>
            <b-icon icon="key-fill"/>
          </b-input-group-prepend>
          <b-form-input type="password" v-model="password" placeholder="Password" :state="passwordState" required/>
        </b-input-group>
        <b-button type="submit" variant="dark" size="lg">Login</b-button>
      </form>
    </b-card>
  </div>
</template>

<script>
export default {
  name: 'loginForm',
  data () {
    return {
      username: null,
      password: null,
      usernameState: null,
      passwordState: null,
      loginError: false
    }
  },
  methods: {
    handleLogin () {
      this.usernameState = (this.username !== null)
      this.passwordState = (this.password !== null)
      if (this.usernameState && this.passwordState) {
        this.$store.dispatch('loginAction', { username: this.username, password: this.password })
          .then(() => {
            this.loginError = false
            this.$router.push('/')
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
#login-page {
  height: 100%;
  background-image: url('/static/background.jpg');
  background-size: cover;
}
#login-form {
  background: white;
}
</style>

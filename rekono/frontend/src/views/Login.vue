<template>
  <public-form>
    <template>
      <b-alert v-model="loginError" variant="danger">
        <b-icon icon="exclamation-circle-fill" variant="danger"></b-icon>
        Invalid credentials
      </b-alert>
      <b-form @submit="login">
        <b-input-group size="lg" class="mb-3">
          <b-input-group-prepend is-text>
            <b-icon icon="person-fill"/>
          </b-input-group-prepend>
          <b-form-input type="text" v-model="username" placeholder="Username" :state="usernameState" max-length="100" autofocus/>
        </b-input-group>
        <b-input-group size="lg" class="mb-3">
          <b-input-group-prepend is-text>
            <b-icon icon="key-fill"/>
          </b-input-group-prepend>
          <b-form-input type="password" v-model="password" placeholder="Password" :state="passwordState"/>
        </b-input-group>
        <b-row>
          <b-col cols="6">
            <b-link @click="$router.push('/reset-password')">Forgot your password?</b-link>
          </b-col>
          <b-col cols="6">
            <b-button type="submit" variant="dark" size="lg">Login</b-button>
          </b-col>
        </b-row>
      </b-form>
    </template>
  </public-form>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import PublicForm from '@/common/PublicForm'
export default {
  name: 'loginPage',
  mixins: [RekonoApi],
  data () {
    return {
      username: null,
      password: null,
      usernameState: null,
      passwordState: null,
      loginError: false
    }
  },
  components: {
    PublicForm
  },
  methods: {
    login (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/token/', { username: this.username, password: this.password }, false)
          .then(data => {
            this.$store.dispatch('login', { tokens: data })
            this.loginError = false
            this.$router.push('/')
          })
          .catch(() => {
            this.loginError = true
            this.password = null
            this.usernameState = false
            this.passwordState = false
          })
      }
    },
    check () {
      this.usernameState = this.validateName(this.username)
      this.passwordState = (this.password !== null)
      return this.usernameState && this.passwordState
    }
  }
}
</script>

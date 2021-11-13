<template>
  <div>
    <form v-on:submit.prevent="handleLogin">
      <b-form-group label="" label-for="username">
        <input type="text" v-model="username" required placeholder="Username">
      </b-form-group>
      <b-form-group label="" label-for="password">
        <input type="password" v-model="password" required placeholder="Password">
      </b-form-group>
      <b-button type="submit" variant="primary">Login</b-button>
    </form>
  </div>
</template>

<script>
import store from '../store/'
export default {
  name: 'loginForm',
  data () {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    handleLogin (event) {
      if (this.username !== '' && this.password !== '') {
        store.dispatch('loginAction', { username: this.username, password: this.password })
          .then(() => {
            alert('Loged In!')
          })
      }
    }
  }
}
</script>

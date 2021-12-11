import Vue from 'vue'
import Vuex from 'vuex'
import AuthenticationApi from '../backend/authentication'
import { accessTokenKey } from '../backend/utils'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: null,
    role: null
  },
  mutations: {
    login (state, userData) {
      state.user = userData.user
      state.role = userData.role
    },
    logout (state) {
      state.user = null
      state.role = null
    }
  },
  actions: {
    checkState ({ commit }) {
      var accessToken = localStorage.getItem(accessTokenKey)
      if (accessToken) {
        commit('login', AuthenticationApi.decodeToken(accessToken))
      }
    },
    loginAction ({ commit }, { username, password }) {
      return AuthenticationApi.login(username, password)
        .then(data => {
          commit('login', data)
          return Promise.resolve()
        })
        .catch(error => {
          return Promise.reject(error)
        })
    },
    logoutAction ({ commit }) {
      return AuthenticationApi.logout()
        .then(() => {
          commit('logout')
          this.redirectToLogin()
          return Promise.resolve()
        })
        .catch(error => {
          return Promise.reject(error)
        })
    },
    redirectToLogin () {
      this.$router.push('/login')
    }
  }
})

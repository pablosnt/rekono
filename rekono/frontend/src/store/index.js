import Vue from 'vue'
import Vuex from 'vuex'
import { login, logout } from '../backend/authentication'

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
    loginAction ({ commit }, { username, password }) {
      return login(username, password)
        .then(data => {
          commit('login', data)
          return Promise.resolve()
        })
        .catch(error => {
          return Promise.reject(error)
        })
    },
    logoutAction ({ commit }) {
      return logout()
        .then(() => {
          commit('logout')
          return Promise.resolve()
        })
        .catch(error => {
          return Promise.reject(error)
        })
    }
  }
})

import Vue from 'vue'
import Vuex from 'vuex'
import router from '@/router'
import AuthenticationApi from '@/backend/authentication'
import { accessTokenKey } from '@/backend/constants'

Vue.use(Vuex)

const showMainTabs = 'show-main-tabs'

export default new Vuex.Store({
  state: {
    user: null,
    role: null,
    mainTabs: true,
    refreshing: false,
  },
  mutations: {
    login (state, userData) {
      state.user = userData.user
      state.role = userData.role
    },
    logout (state) {
      state.user = null
      state.role = null
    },
    showMainTabs (state) {
      state.mainTabs = true
    },
    hideMainTabs (state) {
      state.mainTabs = false
    },
    startRefreshingToken (state) {
      state.refreshing = true
    },
    finishRefreshingToken (state) {
      state.refreshing = false
    }
  },
  actions: {
    checkState ({ commit }) {
      // commit('finishRefreshingToken')
      const accessToken = localStorage.getItem(accessTokenKey)
      if (accessToken) {
        commit('login', AuthenticationApi.decodeToken(accessToken))
      } else {
        commit('login', { user: null, role: null })
      }
      const mainTabs = localStorage.getItem(showMainTabs)
      if (mainTabs === 'true') {
        commit('showMainTabs')
      } else {
        commit('hideMainTabs')
      }
    },
    loginAction ({ commit }, { username, password }) {
      return AuthenticationApi.login(username, password)
        .then(data => {
          commit('login', data)
          return Promise.resolve()
        })
    },
    logoutAction ({ commit, dispatch }) {
      return AuthenticationApi.logout()
        .then(() => {
          commit('logout')
          dispatch('redirectToLogin')
          return Promise.resolve()
        })
    },
    redirectToLogin ({ dispatch }) {
      dispatch('checkState')
      router.push({ name: 'login' })
    },
    changeMainTabs ({ state, commit }) {
      if (state.mainTabs) {
        commit('hideMainTabs')
        localStorage.setItem(showMainTabs, false)
      } else {
        commit('showMainTabs')
        localStorage.setItem(showMainTabs, true)
      }
    },
    startRefreshingToken ({ commit }) {
      commit('startRefreshingToken')
    },
    finishRefreshingToken ({ commit }) {
      commit('finishRefreshingToken')
    }
  }
})

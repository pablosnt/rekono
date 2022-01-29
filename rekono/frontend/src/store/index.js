import Vue from 'vue'
import Vuex from 'vuex'
import router from '@/router'
import { accessTokenKey, removeTokens, decodeToken, processTokens } from '@/backend/tokens'

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
    authenticateUser (state, userData) {
      state.user = userData.user
      state.role = userData.role
    },
    changeMainTabs (state) {
      state.mainTabs = !state.mainTabs
    },
    changeRefreshStatus (state) {
      state.refreshing = !state.refreshing
    }
  },
  actions: {
    checkState ({ state, commit }) {
      const accessToken = localStorage.getItem(accessTokenKey)
      if (accessToken) {
        commit('authenticateUser', decodeToken(accessToken))
      } else {
        commit('authenticateUser', { user: null, role: null })
      }
      const mainTabs = localStorage.getItem(showMainTabs)
      if (mainTabs && mainTabs !== state.mainTabs) {
        commit('changeRefreshStatus')
      }
    },
    login ({ commit }, { tokens }) {
      commit('authenticateUser', processTokens(tokens))
    },
    logout ({ commit, dispatch }) {
      removeTokens()
      commit('authenticateUser', { user: null, role: null })
      dispatch('redirectToLogin')
    },
    redirectToLogin ({ dispatch }) {
      dispatch('checkState')
      router.push({ name: 'login' })
    },
    changeMainTabs ({ state, commit }) {
      localStorage.setItem(showMainTabs, !state.mainTabs)
      commit('changeMainTabs')
    },
    changeRefreshStatus ({ commit }) {
      commit('changeRefreshStatus')
    }
  }
})

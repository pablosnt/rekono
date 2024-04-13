import { defineStore } from 'pinia'
import { useJwt } from '@vueuse/integrations/useJwt'

export const userStore = defineStore('user', {
  state: () => ({ user: null, role: null }),
  actions: {
    login(token) {
      const { header, payload } = useJwt(token)
      user = payload.user_id
      role = payload.role
    },
    logout() {
      user = null
      role = null
    }
  }
})

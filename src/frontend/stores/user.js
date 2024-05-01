import { jwtDecode } from 'jwt-decode'

export const userStore = defineStore('user', {
  state: () => ({ user: null, role: null }),
  actions: {
    login(token) {
      const payload = jwtDecode(token)
      this.user = payload.user_id
      this.role = payload.role
    },
    logout() {
      this.user = null
      this.role = null
    },
    check() {
      const tokens = useTokens()
      const token = tokens.get().access
      if (token !== null && this.user === null) {
        this.login(token)
      }
    }
  }
})

import RekonoApi from './api'
import { refreshTokenKey } from './constants'

class Authentication extends RekonoApi {
  login (username, password) {
    return super.post('/api/token/', { username: username, password: password }, false)
      .then(response => {
        return Promise.resolve(super.processTokens(response.data))
      })
  }

  logout () {
    return super.post('/api/logout/', { refresh_token: localStorage[refreshTokenKey] })
      .then(() => {
        super.removeTokens()
        return Promise.resolve()
      })
      .catch(error => {
        super.removeTokens()
        return Promise.reject(error)
      })
  }
}

export default new Authentication()

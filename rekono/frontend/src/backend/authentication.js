import { accessTokenKey, refreshTokenKey, decodeToken, headers } from './utils'
import axios from 'axios'

const removeTokens = () => {
  localStorage.removeItem(accessTokenKey)
  localStorage.removeItem(refreshTokenKey)
}

const processTokens = (tokens) => {
  localStorage.setItem(accessTokenKey, tokens.access)
  localStorage.setItem(refreshTokenKey, tokens.refresh)
  return decodeToken(tokens.access)
}

const login = (username, password) => {
  return axios
    .post('/api/token/', { username: username, password: password }, { headers: headers(false) })
    .then(response => {
      var claims = processTokens(response.data)
      return Promise.resolve(claims)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const refresh = () => {
  return axios
    .post('/api/token/refresh/', { refresh: localStorage[refreshTokenKey] }, { headers: headers() })
    .then(response => {
      var claims = processTokens(response.data)
      return Promise.resolve(claims)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const logout = () => {
  return axios
    .post('/api/logout/', { refresh_token: localStorage[refreshTokenKey] }, { headers: headers() })
    .then(response => {
      removeTokens()
      return Promise.resolve()
    })
    .catch(error => {
      removeTokens()
      return Promise.reject(error)
    })
}

export {
  login, logout, refresh
}

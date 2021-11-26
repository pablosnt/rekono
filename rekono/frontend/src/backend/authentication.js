import { headers } from './utils'
import axios from 'axios'
import jwtDecode from 'jwt-decode'
import { accessTokenKey, refreshTokenKey } from './constants'

const decodeToken = (accessToken) => {
  var decoded = jwtDecode(accessToken)
  return {
    user: decoded.user_id,
    role: decoded.role
  }
}

const processTokens = (tokens) => {
  localStorage.setItem(accessTokenKey, tokens.access)
  localStorage.setItem(refreshTokenKey, tokens.refresh)
  return decodeToken(tokens.access)
}

const login = (username, password) => {
  return axios
    .post('/api/token/', { username: username, password: password }, headers())
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
    .post('/api/token/refresh/', { refresh: localStorage[refreshTokenKey] }, headers())
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
    .$post('/api/logout/', { refresh: localStorage[refreshTokenKey] }, headers())
    .then(response => {
      localStorage.removeItem(accessTokenKey)
      localStorage.removeItem(refreshTokenKey)
      return Promise.resolve()
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export {
  decodeToken, login, logout, refresh
}

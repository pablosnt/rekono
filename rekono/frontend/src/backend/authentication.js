import { headers } from './utils'
import axios from 'axios'
import jwtDecode from 'jwt-decode'

const processTokens = (tokens) => {
  localStorage.setItem('access_token', tokens.access)
  localStorage.setItem('refresh_token', tokens.refresh)
  var decoded = jwtDecode(tokens.access)
  return {
    user: decoded.user_id,
    role: decoded.role
  }
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
    .post('/api/token/refresh/', { refresh: localStorage['refresh_token'] }, headers())
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
    .$post('/api/logout/', { refresh: localStorage['refresh_token'] }, headers())
    .then(response => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      return Promise.resolve()
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export {
  login, logout, refresh
}

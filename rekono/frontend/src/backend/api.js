import axios from 'axios'
import jwtDecode from 'jwt-decode'
import store from '../store'
import { accessTokenKey, refreshTokenKey } from './utils'

class RekonoApi {
  removeTokens () {
    localStorage.removeItem(accessTokenKey)
    localStorage.removeItem(refreshTokenKey)
  }

  decodeToken (accessToken) {
    var decoded = jwtDecode(accessToken)
    return {
      user: decoded.user_id,
      role: decoded.role
    }
  }

  processTokens (tokens) {
    localStorage.setItem(accessTokenKey, tokens.access)
    localStorage.setItem(refreshTokenKey, tokens.refresh)
    return this.decodeToken(tokens.access)
  }

  headers (requiredAuth = true, extraHeaders = null) {
    var requestHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
    if (store.state.user !== null && requiredAuth) {
      var accessToken = localStorage[accessTokenKey]
      requestHeaders['Authorization'] = 'Bearer ' + accessToken
    }
    if (extraHeaders !== null) {
      requestHeaders = Object.assign({}, requestHeaders, extraHeaders)
    }
    return requestHeaders
  }

  refresh () {
    return this.post('/api/token/refresh/', { refresh: localStorage[refreshTokenKey] })
      .then(response => {
        console.log(response.data)
        var claims = this.processTokens(response.data)
        return Promise.resolve(claims)
      })
  }

  request (method, endpoint, headers, data = null, retry = false) {
    var req = null
    if (data !== null) {
      req = method(endpoint, data, { headers: headers })
    } else {
      req = method(endpoint, { headers: headers })
    }
    return req
      .then(response => { return Promise.resolve(response) })
      .catch(error => {
        if (error.response && error.response.status === 401) {
          if (retry) {
            store.dispatch('redirectToLogin')
          } else {
            return this.refresh()
              .then(() => { return this.request(method, endpoint, headers, data, true) })
              .catch(() => { store.dispatch('redirectToLogin') })
          }
        }
        return Promise.reject(error)
      })
  }

  get (endpoint, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.get, endpoint, this.headers(requiredAuth, extraHeaders))
  }

  post (endpoint, data, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.post, endpoint, this.headers(requiredAuth, extraHeaders), data)
  }

  put (endpoint, data, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.put, endpoint, this.headers(requiredAuth, extraHeaders), data)
  }

  delete (endpoint, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.delete, endpoint, this.headers(requiredAuth, extraHeaders))
  }
}

export default RekonoApi

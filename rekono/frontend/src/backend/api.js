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
    return axios.post('/api/token/refresh/', { refresh: localStorage[refreshTokenKey] }, this.headers())
      .then(response => {
        this.removeTokens()
        var claims = this.processTokens(response.data)
        return Promise.resolve(claims)
      })
  }

  request (method, endpoint, data = null, requiredAuth = true, extraHeaders = null, retry = false) {
    var req = null
    if (data !== null) {
      req = method(endpoint, data, { headers: this.headers(requiredAuth, extraHeaders) })
    } else {
      req = method(endpoint, { headers: this.headers(requiredAuth, extraHeaders) })
    }
    return req
      .then(response => { return Promise.resolve(response) })
      .catch(error => {
        if (error.response && error.response.status === 401) {
          if (retry) {
            this.removeTokens()
            store.dispatch('redirectToLogin')
          } else {
            return this.refresh()
              .then(() => { return this.request(method, endpoint, data, requiredAuth, extraHeaders, true) })
              .catch(() => {
                this.removeTokens()
                store.dispatch('redirectToLogin')
              })
          }
        }
        return Promise.reject(error)
      })
  }

  get (endpoint, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.get, endpoint, null, requiredAuth, extraHeaders)
  }

  paginatedGet (endpoint, page = null, size = null, requiredAuth = true, extraHeaders = null) {
    if (page !== null && size !== null) {
      endpoint += '&page=' + page + '&size=' + size
    }
    return this.get(endpoint, requiredAuth, extraHeaders)
  }

  post (endpoint, data, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.post, endpoint, data, requiredAuth, extraHeaders)
  }

  put (endpoint, data, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.put, endpoint, data, requiredAuth, extraHeaders)
  }

  delete (endpoint, requiredAuth = true, extraHeaders = null) {
    return this.request(axios.delete, endpoint, null, requiredAuth, extraHeaders)
  }
}

export default RekonoApi

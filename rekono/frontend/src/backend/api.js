import axios from 'axios'
import jwtDecode from 'jwt-decode'
import store from '@/store'
import { accessTokenKey, refreshTokenKey } from './constants'

class RekonoApi {
  removeTokens () {
    localStorage.removeItem(accessTokenKey)
    localStorage.removeItem(refreshTokenKey)
  }

  decodeToken (accessToken) {
    const decoded = jwtDecode(accessToken)
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
    let requestHeaders = {
      'Content-Type': 'application/json',
      Accept: 'application/json'
    }
    if (store.state.user !== null && requiredAuth) {
      requestHeaders.Authorization = `Bearer ${localStorage[accessTokenKey]}`
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
        return Promise.resolve(this.processTokens(response.data))
      })
  }

  request (method, endpoint, queryData = null, bodydata = null, requiredAuth = true, extraHeaders = null, allowUnauth = false, retry = false) {
    let req = null
    if (bodydata) {
      req = method(endpoint, bodydata, { headers: this.headers(requiredAuth, extraHeaders) })
    } else if (queryData) {
      req = method(endpoint, { params: queryData, headers: this.headers(requiredAuth, extraHeaders) })
    } else {
      req = method(endpoint, { headers: this.headers(requiredAuth, extraHeaders) })
    }
    return req
      .then(response => { return Promise.resolve(response) })
      .catch(error => {
        if (requiredAuth && error.response && error.response.status === 401 && !retry) {
          return this.refresh()
            .then(() => { return this.request(method, endpoint, queryData, bodydata, requiredAuth, extraHeaders, allowUnauth, true) })
            .catch(error => {
              if (requiredAuth && !allowUnauth) {
                this.removeTokens()
                store.dispatch('redirectToLogin')
              } else {
                return Promise.reject(error)
              }
            })
        }
        return Promise.reject(error)
      })
  }

  get (endpoint, page = null, limit = null, filter = null, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
    let params = {}
    if (page && limit) {
      params = {
        page: page,
        limit: limit
      }
    }
    if (filter) {
      for (let key in filter) {
        if (filter[key]) {
          params[key] = filter[key]
        }
      }
    }
    return this.request(axios.get, endpoint, params, null, requiredAuth, extraHeaders, allowUnauth)
  }

  post (endpoint, data, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
    return this.request(axios.post, endpoint, null, data, requiredAuth, extraHeaders, allowUnauth)
  }

  put (endpoint, data, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
    return this.request(axios.put, endpoint, null, data, requiredAuth, extraHeaders, allowUnauth)
  }

  delete (endpoint, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
    return this.request(axios.delete, endpoint, null, null, requiredAuth, extraHeaders, allowUnauth)
  }
}

export default RekonoApi

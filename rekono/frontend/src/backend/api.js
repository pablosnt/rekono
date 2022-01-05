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
    if (!store.state.refreshing) {
      store.dispatch('startRefreshingToken')
      return axios.post('/api/token/refresh/', { refresh: localStorage[refreshTokenKey] }, this.headers())
        .then(response => {
          this.removeTokens()
          const decodedTokens = this.processTokens(response.data)
          store.dispatch('finishRefreshingToken')
          return Promise.resolve(decodedTokens)
        })
        .catch(() => {
          this.removeTokens()
          store.dispatch('finishRefreshingToken')
          store.dispatch('redirectToLogin')
          return Promise.reject()
        })
    }
    return Promise.reject()
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
        if (error.response && error.response.status === 401 && !retry) {
          return this.refresh()
            .then(() => { return this.request(method, endpoint, queryData, bodydata, requiredAuth, extraHeaders, allowUnauth, true) })
            .catch(() => {
              if (store.state.refreshing) {
                return this.request(method, endpoint, queryData, bodydata, requiredAuth, extraHeaders, allowUnauth, false)
              }
            })
        }
        return Promise.reject(error)
      })
  }

  get (endpoint, page = null, limit = null, filter = null, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
    let params = {}
    if (page) {
      params.page = page
    }
    if (limit) {
      params.limit = limit
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

  getAllPages (endpoint, filter = null, page = 1, limit = 1000, requiredAuth = true, extraHeaders = null, allowUnauth = false, accumulated = []) {
    return this.get(endpoint, page, limit, filter, requiredAuth, extraHeaders, allowUnauth)
      .then(response => {
        accumulated = accumulated.concat(response.data.results)
        if ((page * limit) < response.data.count) {
          return this.getAllPages(endpoint, filter, page + 1, limit, requiredAuth, extraHeaders, allowUnauth, accumulated)
        } else {
          return Promise.resolve(accumulated)
        }
      })
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

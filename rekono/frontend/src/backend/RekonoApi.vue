
<script>
import axios from 'axios'
import RekonoAlerts from '@/backend/RekonoAlerts'
import RekonoPagination from '@/backend/RekonoPagination'
import { accessTokenKey, refreshTokenKey, removeTokens, processTokens } from '@/backend/tokens'
export default {
  name: 'rekonoApi',
  mixins: [RekonoAlerts, RekonoPagination],
  data () {
    return {
      stages: [
        { id: 1, value: 'OSINT' },
        { id: 2, value: 'Enumeration' },
        { id: 3, value: 'Vulnerabilities' },
        { id: 4, value: 'Services' },
        { id: 5, value: 'Exploitation' }
      ],
      targetTypes: ['Domain', 'IP range', 'Network', 'Private IP', 'Public IP'],
      inputTypes: ['OSINT', 'Host', 'Enumeration', 'Endpoint', 'Technology', 'Vulnerability', 'Exploit', 'Credential', 'Wordlist'],
      findingTypes: ['OSINT', 'Credentials', 'Hosts', 'Enumerations', 'Endpoints', 'Technologies', 'Vulnerabilities', 'Exploits'],
      osTypeByIcon: [
        { value: 'Linux', icon: 'brands/linux', color: 'black', variant: 'warning' },
        { value: 'Windows', icon: 'brands/windows', color: 'darkblue', variant: 'primary' },
        { value: 'MacOS', icon: 'brands/apple', color: 'gray', variant: 'secondary' },
        { value: 'iOS', icon: 'brands/apple', color: 'gray', variant: 'secondary' },
        { value: 'Android', icon: 'brands/android', color: 'forestgreen', variant: 'success' },
        { value: 'Solaris', icon: 'sun', color: 'orange', variant: 'warning' },
        { value: 'FreeBSD', icon: 'brands/freebsd', color: 'red', variant: 'danger' },
        { value: 'Other', icon: 'desktop', color: 'black', variant: 'dark' },
      ],
      portStatusByVariant: [
        { value: 'Open', variant: 'success' },
        { value: 'Open -Filtered', variant: 'primary' },
        { value: 'Filtered', variant: 'warning' },
        { value: 'Closed', variant: 'danger' }
      ],
      severities: ['Critical', 'High', 'Medium', 'Low', 'Info'],
      severityByVariant: [
        { value: 'Critical', variant: 'danger' },
        { value: 'High', variant: 'warning' },
        { value: 'Medium', variant: 'primary' },
        { value: 'Low', variant: 'success' },
        { value: 'Info', variant: 'info' }
      ],
      roles: ['Admin', 'Auditor', 'Reader'],
      auditor: ['Admin', 'Auditor'],
      roleByVariant: {
        admin: 'success',
        auditor: 'danger',
        reader: 'primary'
      },
      notificationScopes: ['Disabled', 'Only my executions', 'All executions'],
      intensities: [
        { value: 1, text: 'Sneaky' },
        { value: 2, text: 'Low' },
        { value: 3, text: 'Normal' },
        { value: 4, text: 'Hard' },
        { value: 5, text: 'Insane' }
      ],
      intensityByVariant: [
        { intensity_rank: 'Insane', variant: 'danger' },
        { intensity_rank: 'Hard', variant: 'warning' },
        { intensity_rank: 'Normal', variant: 'secondary' },
        { intensity_rank: 'Low', variant: 'success' },
        { intensity_rank: 'Sneaky', variant: 'info' }
      ],
      statuses: ['Requested', 'Skipped', 'Running', 'Cancelled', 'Error', 'Completed'],
      statusByVariant: [
        { value: 'Requested', variant: 'primary' },
        { value: 'Skipped', variant: 'secondary' },
        { value: 'Running', variant: 'warning' },
        { value: 'Cancelled', variant: 'danger' },
        { value: 'Error', variant: 'danger' },
        { value: 'Completed', variant: 'success' }
      ],
      cancellableStatuses: ['Requested', 'Running'],
      timeUnits: ['Weeks', 'Days', 'Hours', 'Minutes']
    }
  },
  methods: {
    getOnePage (endpoint, params = null, requiredAuth = true, extraHeaders = null) {
      return this.get(endpoint, this.getPage(), this.getLimit(), params, requiredAuth, extraHeaders)
    },
    getAllPages (endpoint, params = null, page = 1, limit = 1000, requiredAuth = true, extraHeaders = null, accumulated = []) {
      return this.get(endpoint, page, limit, params, requiredAuth, extraHeaders)
        .then(response => {
          accumulated = accumulated.concat(response.data.results)
          if ((page * limit) < response.data.count) {
            return this.getAllPages(endpoint, params, page + 1, limit, requiredAuth, extraHeaders, accumulated)
          } else {
            return Promise.resolve(accumulated)
          }
        })
    },
    get (endpoint, page = null, limit = null, params = null, requiredAuth = true, extraHeaders = null) {
      if (page || limit) {
        if (!params) {
          params = {}
        }
        params = Object.assign({}, params, {page: page, limit: limit})
      }
      return this.request(axios.get, endpoint, params, null, requiredAuth, extraHeaders)
    },
    post (endpoint, data, title = null, message = null, requiredAuth = true, extraHeaders = null) {
      return this.writeOperation(this.request(axios.post, endpoint, null, data, requiredAuth, extraHeaders), title, message)
    },
    put (endpoint, data, title = null, message = null, requiredAuth = true, extraHeaders = null) {
      return this.writeOperation(this.request(axios.put, endpoint, null, data, requiredAuth, extraHeaders), title, message)
    },
    delete (endpoint, title = null, message = null, requiredAuth = true, extraHeaders = null) {
      return this.writeOperation(this.request(axios.delete, endpoint, null, null, requiredAuth, extraHeaders), title, message, this.warning)
    },
    writeOperation (rekonoRequest, title, message, success = this.success) {
      return rekonoRequest
        .then(response => {
          if (title && message) {
            success(title, message)
          }
          return Promise.resolve(response.data)
        })
        .catch(error => {
          if (error && title) {
            this.handleError(error, title)
          }
          return Promise.reject(error)
        })
    },
    request (method, endpoint, queryData = null, bodyData = null, requiredAuth = true, extraHeaders = null, retry = false) {
      let httpRequest = null
      if (bodyData) {
        httpRequest = method(endpoint, this.cleanBody(bodyData), { headers: this.headers(requiredAuth, extraHeaders) })
      } else if (queryData) {
        httpRequest = method(endpoint, { params: this.cleanParams(queryData), headers: this.headers(requiredAuth, extraHeaders) })
      } else {
        httpRequest = method(endpoint, { headers: this.headers(requiredAuth, extraHeaders) })
      }
      return httpRequest
        .then(response => { return Promise.resolve(response) })
        .catch(error => {
          if (error.response && error.response.status === 401 && !retry) {
            return this.refresh()
              .then(() => { return this.request(method, endpoint, queryData, bodyData, requiredAuth, extraHeaders, true) })
              .catch(() => {
                if (this.$store.state.refreshing) {
                  return this.request(method, endpoint, queryData, bodyData, requiredAuth, extraHeaders, false)
                }
              })
          }
          return Promise.reject(error)
        })
    },
    refresh () {
      if (!this.$store.state.refreshing) {
        this.$store.dispatch('changeRefreshStatus')
        return axios.post('/api/token/refresh/', { refresh: localStorage[refreshTokenKey] }, this.headers())
          .then(response => {
            removeTokens()
            processTokens(response.data)
            this.$store.dispatch('changeRefreshStatus')
            return Promise.resolve()
          })
          .catch(() => {
            removeTokens()
            this.$store.dispatch('changeRefreshStatus')
            this.$store.dispatch('redirectToLogin')
            return Promise.reject()
          })
      }
      return Promise.reject()
    },
    headers (requiredAuth, extraHeaders) {
      let requestHeaders = {
        'Content-Type': 'application/json',
        Accept: 'application/json'
      }
      if (this.$store.state.user !== null && requiredAuth) {
        requestHeaders.Authorization = `Bearer ${localStorage[accessTokenKey]}`
        console.log(requestHeaders.Authorization)
      }
      if (extraHeaders) {
        requestHeaders = Object.assign({}, requestHeaders, extraHeaders)
        console.log(requestHeaders)
      }
      return requestHeaders
    },
    handleError (error, title) {
      let message = 'Unexpected error'
      if (error.response.status === 400) {
        const aux = Object.values(error.response.data)[0][0]
        message = aux.charAt(0).toUpperCase() + aux.slice(1)
      }
      else if (error.response.status === 401) {
        message = 'You are not authenticated. Please, try again after login in'
      }
      else if (error.response.status === 403) {
        message = 'You are not authorized to perform this operation'
      }
      else if (error.response.status === 404) {
        message = 'Resource not found'
      }
      this.danger(title, message)
    },
    cleanParams (params) {
      if (params) {
        let cleanParams = {}
        for (var field in params) {
          if (![''. null, undefined].includes(params[field])) {
            cleanParams[field] = params[field]
          }
        }
        return cleanParams
      }
      return params
    },
    cleanBody (body) {
      if (body) {
        for (var field in body) {
          if (['', null, undefined].includes(body[field])) {
            body[field] = null
          }
        }
      }
      return body
    }
  }
}
</script>

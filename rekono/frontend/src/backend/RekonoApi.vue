
<script>
import RekonoAlerts from '@/backend/RekonoAlerts'
import RekonoPagination from '@/backend/RekonoPagination'
import { accessTokenKey, processTokens, refreshTokenKey, removeTokens } from '@/backend/tokens'
import axios from 'axios'
import moment from 'moment'
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
      inputTypes: ['OSINT', 'Host', 'Port', 'Path', 'Technology', 'Vulnerability', 'Exploit', 'Credential', 'Wordlist'],
      findingTypes: ['OSINT', 'Credentials', 'Hosts', 'Ports', 'Paths', 'Technologies', 'Vulnerabilities', 'Exploits'],
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
      timeUnits: ['Weeks', 'Days', 'Hours', 'Minutes'],
      authenticationTypes: ['None', 'Basic', 'Bearer', 'Cookie', 'Digest', 'JWT', 'NTLM'],
      wordlistTypes: ['Endpoint', 'Subdomain'],
      nameRegex: /^[\wÀ-ÿ\s.\-[\]()@]{0,120}$/,
      textRegex: /^[\wÀ-ÿ\s.:,+\-'"?¿¡!#%$€[\]()]{0,300}$/,
      cveRegex: /^CVE-\d{4}-\d{1,7}$/,
      defectDojoKeyRegex: /^[\da-z]{40}$/,
      telegramTokenRegex: /^\d{10}:[\w-]{35}$/,
      credentialRegex: /^[\w./\-=+,:<>¿?¡!#&$()@%[\]{}*]{1,500}$/,
      telegramBotName: null,
      defectDojoUrl: null,
      defectDojoEnabled: null,
      backendRootPath: process.env.VUE_APP_ROOT_BACKEND_PATH
    }
  },
  methods: {
    getSettings () {
      this.get('/api/system/1/').then(response => {
        this.telegramBotName = response.data.telegram_bot_name
        this.telegramBotLink = this.telegramBotName ? `https://t.me/${this.telegramBotName}` : null
        this.defectDojoUrl = response.data.defect_dojo_url
        this.defectDojoEnabled = response.data.defect_dojo_enabled
      })
    },
    getOnePage (endpoint, params = null, requiredAuth = true, extraHeaders = null) {
      return this.get(endpoint, this.getPage(), this.getLimit(), params, requiredAuth, extraHeaders)
    },
    getAllPages (endpoint, params = null, requiredAuth = true, extraHeaders = null, accumulated = [], page = 1) {
      const limit = 1000
      return this.get(endpoint, page, limit, params, requiredAuth, extraHeaders)
        .then(response => {
          accumulated = accumulated.concat(response.data.results)
          if ((page * limit) < response.data.count) {
            return this.getAllPages(endpoint, params, requiredAuth, extraHeaders, accumulated, page + 1)
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
      return this.request(axios.get, endpoint, params, null, requiredAuth, extraHeaders, false)
    },
    post (endpoint, data, title = null, message = null, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
      return this.writeOperation(this.request(axios.post, endpoint, null, data, requiredAuth, extraHeaders, allowUnauth), title, message)
    },
    put (endpoint, data, title = null, message = null, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
      return this.writeOperation(this.request(axios.put, endpoint, null, data, requiredAuth, extraHeaders, allowUnauth), title, message)
    },
    delete (endpoint, title = null, message = null, requiredAuth = true, extraHeaders = null, allowUnauth = false) {
      return this.writeOperation(this.request(axios.delete, endpoint, null, null, requiredAuth, extraHeaders, allowUnauth), title, message, this.warning)
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
          if (error && title && error.response.status !== 401) {
            this.handleError(error, title)
          }
          return Promise.reject(error)
        })
    },
    getUrl (endpoint) {
      if (this.backendRootPath) {
        endpoint = this.backendRootPath + endpoint
      }
      if (this.$store.state.backendUrl) {
        var endpointUrl = new URL(this.$store.state.backendUrl)
        endpointUrl.pathname = endpoint
        return endpointUrl.href
      }
      return endpoint
    },
    request (method, endpoint, queryData = null, bodyData = null, requiredAuth = true, extraHeaders = null, allowUnauth = false, retry = false) {
      let httpRequest = null
      if (bodyData) {
        httpRequest = method(this.getUrl(endpoint), this.cleanBody(bodyData), { headers: this.headers(requiredAuth, extraHeaders) })
      } else if (queryData) {
        httpRequest = method(this.getUrl(endpoint), { params: this.cleanParams(queryData), headers: this.headers(requiredAuth, extraHeaders) })
      } else {
        httpRequest = method(this.getUrl(endpoint), { headers: this.headers(requiredAuth, extraHeaders) })
      }
      return httpRequest
        .then(response => { return Promise.resolve(response) })
        .catch(error => {
          if (error.response && error.response.status === 401 && !retry && !allowUnauth) {
            return this.refresh()
              .then(() => { return this.request(method, endpoint, queryData, bodyData, requiredAuth, extraHeaders, allowUnauth, true) })
              .catch(() => {
                if (this.$store.state.refreshing) {
                  return this.request(method, endpoint, queryData, bodyData, requiredAuth, extraHeaders, allowUnauth, false)
                }
              })
          }
          return Promise.reject(error)
        })
    },
    refresh () {
      if (!this.$store.state.refreshing) {
        this.$store.dispatch('changeRefreshStatus')
        return axios.post(this.getUrl('/api/token/refresh/'), { refresh: sessionStorage.getItem(refreshTokenKey) }, this.headers())
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
        requestHeaders.Authorization = `Bearer ${sessionStorage.getItem(accessTokenKey)}`
      }
      if (extraHeaders) {
        requestHeaders = Object.assign({}, requestHeaders, extraHeaders)
      }
      return requestHeaders
    },
    handleError (error, title) {
      let message = 'Unexpected error'
      if (error.response.status === 400) {
        const aux = Object.values(error.response.data)[0][0]
        message = aux.charAt(0).toUpperCase() + aux.slice(1)
        title = Object.keys(error.response.data)[0]
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
        for (let field in params) {
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
        for (let field in body) {
          if (['', null, undefined].includes(body[field])) {
            body[field] = null
          }
        }
      }
      return body
    },
    changeHashParam (name, value) {
      const url = new URL(window.location.href.replace('#/', ''))
      const original_params = url.search
      name = name.toLowerCase().replace(' ', '_')
      if (value) {
        url.searchParams.set(name, value);
      } else {
        url.searchParams.delete(name);
      }
      window.location.hash =  original_params.length > 0 ? window.location.hash.replace(original_params, url.search) : window.location.hash + url.search
    },
    validate (value, regex) {
      return value && value.length && regex.test(value)
    },
    validateName (value) {
      return this.validate(value, this.nameRegex)
    },
    validateText (value) {
      return this.validate(value, this.textRegex)
    },
    validateCve (value) {
      return this.validate(value, this.cveRegex)
    },
    validateDefectDojoKey (value) {
      return this.validate(value, this.defectDojoKeyRegex)
    },
    validateTelegramToken (value) {
      return this.validate(value, this.telegramTokenRegex)
    },
    validateCredential (value) {
      return this.validate(value, this.credentialRegex)
    },
    validateUrl (value) {
      try {
        new URL(value);
        return true
      } catch (e) {
        return false;
      }
    },
    duration (start, end) {
      const startDate = moment(start)
      const endDate = moment(end)
      const duration = moment.duration(endDate.diff(startDate))
      let text = ''
      const values = [
        {'value': duration.days(), 'text': 'd'},
        {'value': duration.hours(), 'text': 'h'},
        {'value': duration.minutes(), 'text': 'm'},
        {'value': duration.seconds(), 'text': 's'}
      ]
      for (let index in values) {
        if (values[index].value > 0) {
          text += values[index].value.toString() + ' ' + values[index].text + ' '
        }
      }
      return text
    },
    formatDate (date) {
      return moment(date).format('YYYY-MM-DD HH:mm')
    }
  }
}
</script>

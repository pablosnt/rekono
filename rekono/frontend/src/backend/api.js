import axios from 'axios'
import headers from './utils'
import { refresh } from './authentication'

const rekonoApiPost = (endpoint, data, retry = false) => {
  return axios
    .post(endpoint, data, { headers: headers() })
    .then(response => {
      return Promise.resolve(response)
    })
    .catch(error => {
      if (error.response && error.response.status == 401) {
        if (retry) {
          this.$router.push('/login')
        } else {
          refresh()
          return rekonoApiPost(endpoint, data, true)
        }
      }
      return Promise.reject(error)
    })
}

const rekonoApiGet = (endpoint, retry = false) => {
  return axios
    .get(endpoint, { headers: headers() })
    .then(response => {
      return Promise.resolve(response)
    })
    .catch(error => {
      if (error.response && error.response.status == 401) {
        if (retry) {
            this.$router.push('/login')
        } else {
            refresh()
            return rekonoApiGet(endpoint, true)
        }
      }
      return Promise.reject(error)
    })
}
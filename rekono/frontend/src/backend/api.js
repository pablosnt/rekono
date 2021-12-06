import axios from 'axios'
import { headers } from './utils'
import { refresh } from './authentication'
import router from '../router'

const rekonoApiPost = (endpoint, data, retry = false) => {
  return axios
    .post(endpoint, data, { headers: headers() })
    .then(response => {
      return Promise.resolve(response)
    })
    .catch(error => {
      if (error.response && error.response.status === 401) {
        if (retry) {
          router.push('/login')
        } else {
          return refresh()
            .then(() => { return rekonoApiPost(endpoint, data, true) })
            .catch(() => { router.push('/login') })
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
      if (error.response && error.response.status === 401) {
        if (retry) {
          router.push('/login')
        } else {
          return refresh()
            .then(() => { return rekonoApiGet(endpoint, true) })
            .catch(() => { router.push('/login') })
        }
      }
      return Promise.reject(error)
    })
}

export {
  rekonoApiPost, rekonoApiGet
}

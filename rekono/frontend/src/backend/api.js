import axios from 'axios'
import { headers } from './utils'
import { refresh } from './authentication'
import router from '../router'

const rekonoApiGet = (endpoint, retry = false, extraHeaders = null) => {
  return axios
    .get(endpoint, { headers: headers(true, extraHeaders) })
    .then(response => {
      return Promise.resolve(response)
    })
    .catch(error => {
      if (error.response && error.response.status === 401) {
        if (retry) {
          router.push('/login')
        } else {
          return refresh()
            .then(() => { return rekonoApiGet(endpoint, true, extraHeaders) })
            .catch(() => { router.push('/login') })
        }
      }
      return Promise.reject(error)
    })
}

const rekonoApiPost = (endpoint, data, retry = false, extraHeaders = null) => {
  return axios
    .post(endpoint, data, { headers: headers(true, extraHeaders) })
    .then(response => {
      return Promise.resolve(response)
    })
    .catch(error => {
      if (error.response && error.response.status === 401) {
        if (retry) {
          router.push('/login')
        } else {
          return refresh()
            .then(() => { return rekonoApiPost(endpoint, data, true, extraHeaders) })
            .catch(() => { router.push('/login') })
        }
      }
      return Promise.reject(error)
    })
}

const rekonoApiPut = (endpoint, data, retry = false, extraHeaders = null) => {
  return axios
    .put(endpoint, data, { headers: headers(true, extraHeaders) })
    .then(response => {
      return Promise.resolve(response)
    })
    .catch(error => {
      if (error.response && error.response.status === 401) {
        if (retry) {
          router.push('/login')
        } else {
          return refresh()
            .then(() => { return rekonoApiPut(endpoint, data, true, extraHeaders) })
            .catch(() => { router.push('/login') })
        }
      }
      return Promise.reject(error)
    })
}

const rekonoApiDelete = (endpoint, retry = false, extraHeaders = null) => {
  return axios
    .delete(endpoint, { headers: headers(true, extraHeaders) })
    .then(response => {
      return Promise.resolve(response)
    })
    .catch(error => {
      if (error.response && error.response.status === 401) {
        if (retry) {
          router.push('/login')
        } else {
          return refresh()
            .then(() => { return rekonoApiDelete(endpoint, true, extraHeaders) })
            .catch(() => { router.push('/login') })
        }
      }
      return Promise.reject(error)
    })
}

export {
  rekonoApiGet, rekonoApiPost, rekonoApiPut, rekonoApiDelete
}

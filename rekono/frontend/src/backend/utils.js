import store from '../store/'
import { accessTokenKey } from './constants'

const headers = () => {
  var base = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
  if (store.state.user) {
    var accessToken = localStorage[accessTokenKey]
    base['Authorization'] = 'Bearer ' + accessToken
  }
  return base
}

export {
  headers
}
